# import asyncio
import bisect
import numpy as np
import time
import asyncio

from .utility.panoptic_helpers import utils as ph

from hummingbot.client.settings import GatewayConnectionSetting
# from hummingbot.core.event.events import TradeType
from hummingbot.core.gateway.gateway_http_client import GatewayHttpClient
from hummingbot.core.utils.async_utils import safe_ensure_future
from hummingbot.strategy.script_strategy_base import Decimal, ScriptStrategyBase


class TradePanoptions(ScriptStrategyBase):
    """
    This example shows how one could market maker on Panoptic using the Gateway endpoints.
    The user can configure targets, for which they provide:
    - What ticks (relative to the current tick) & timescales they need to sell Panoptions on
    - What max utilisation and minimum open interest they need to be maintaining
    This strategy will hten get currenct spot price for the token pair, check if you're meeting
    your targets, and sell more straddles/calls/puts to meet them if not.
    It will also keep you within gamma and close-ability guardrails.
    Strategy data is logged and plotted for analysis.
    """

    # trading params and configuration
    connector_chain_network = "panoptic_ethereum_sepolia"
    trading_pair = {"t0-t1"}
    markets = {}
    perturbation_testing = True
    verbosity = 1
    targets = [
        {
            "tick_to_maintain": -1,
            "max_utilisation": 0.5,
            "min_notional_value_to_sell_USD": 1000,
            "timescale" : "1M"
        },
        {
            "tick_to_maintain": 0,
            "max_utilisation": 0.5,
            "min_notional_value_to_sell_USD": 1000,
            "timescale" : "1M"
        },
        {
            "tick_to_maintain": 1,
            "max_utilisation": 0.5,
            "min_notional_value_to_sell_USD": 1000,
            "timescale" : "1M"
        }
    ]

    # NOTE: If you make this true, then as prices move, you'll have more and more outdated positions hanging around
    # You will then likely hit the position limit pretty quickly
    # In the future, we could make this config a little more advanced and let you specify a handful of tokenIds
    # you specifically want to avoid having burnt
    maintain_offtarget_positions = False # Should we burn positions you hold that aren't serving a target?

    # internal state variables and methods
    launched = False # Have you launched the strategy?
    initialized = False # Have all the initialization steps completed?
    ready = True # Are all on-chain tasks complete and you're ready to process another one?
    tick_count = 0

    # executed each tick (configure tick size in Hummingbot client before launching strategy)
    def on_tick(self):
        # As written, the tick can now be equivalent to an actual clock, as processes are now controlled by
        # flags and wrapped in safe_ensure_future(...)
        self.log(f"Tick count: {self.tick_count}", 1)
        self.tick_count = self.tick_count + 1

        # initial setup - only execute once
        if not self.launched:
            self.log(f"Launching...", 1)
            self.launched = True
            safe_ensure_future(self.initialize())

        # repeat each tick
        if (self.initialized and self.ready):
            # Tricky because the 'safe_ensure_future' bit immediately returns the contained logic as being complete.
            # It won't wait for the processes inside to finish before allowing tick to tok. Can try to get around
            # this by using flags, but that feels clunky.
            self.ready=False
            safe_ensure_future(self.monitor_and_apply_logic())

    # async task since we are using Gateway
    async def monitor_and_apply_logic(self):
        self.log(f"Checking price...", 2)
        self.log(f"POST /options/getSpotPrice [ connector: {self.connector} ]", 0)
        response = await GatewayHttpClient.get_instance().api_request(
            method="post",
            path_url="options/getSpotPrice",
            params=self.request_payload,
            fail_silently=False
        )
        self.spot_price=response['spotPrice']
        self.log(f"Price: {self.spot_price}", 1)

        self.log(f"Converting spot price to tick location...", 2)
        self.tick_location = ph.adjusted_price_to_tick(
            self.spot_price, self.request_payload["token0Decimals"],
            self.request_payload["token1Decimals"]
        )

        self.request_payload.update({
            "atTick": int(np.floor(self.tick_location))
        })
        self.log(f"Current spot price tick location: {self.tick_location}", 1)

        # Save the spot price and tick location to a log file
        self.log(f"Logging spot data...", 2)
        spot_log_path = "logs/spot_data.dat"
        ph.log_spot_data(spot_log_path, self.request_payload['uniswapV3PoolAddress'], self.spot_price, self.tick_location)

        # TODO: Get this working: if self.tick_count % 10 == 0: ph.generate_spot_plot(spot_log_path)

        self.log(f"Finding relevant Uniswap pool tick locations...", 2)
        lower_idx = bisect.bisect_right(self.tick_locations, self.tick_location) - 1
        upper_idx = lower_idx + 1
        lower_tick = self.tick_locations[lower_idx] if lower_idx >= 0 else None
        upper_tick = self.tick_locations[upper_idx] if upper_idx < len(self.tick_locations) else None
        self.log(f"Lower tick: {lower_tick}", 2)
        self.log(f"Upper tick: {upper_tick}", 2)

        self.log(f"Checking queryPositions...", 2)
        self.log(f"POST /options/queryPositions [ connector: {self.connector} ]", 0)
        response = await GatewayHttpClient.get_instance().api_request(
            method="post",
            path_url="options/queryPositions",
            params=self.request_payload,
            fail_silently=False
        )
        self.open_positions = response['openPositionIdList']
        self.log(f"Open position list: {self.open_positions}", 2)

        # TODO: Primary concern, i think, even before meeting targets, is to see if we're violating
        # guardrails that free us from the market making agreement:
        # - Are my positions closeable? (Use PanopticHelper.reduceSizeIfNecessary())
        # - Am i exceeding my gamma exposure?
        # We should check if either condition is true and return early if so.

        # TODO: To save gas, it would be a lot better to have a universal flag on Panoptic gateway calls
        # that would have each endpoint just return an unsigned tx data,
        # and then add a pool.multicall endpoint. We could then aggregate each burn and mint
        # in the below logic into one tx
        # For now, we'll just do it using the existing endpoints:

        # Iterate through our targets and see if we're selling sufficiently on each:
        for target in self.targets:
            usd_notional_value_being_sold_at_target = {
                'call': 0,
                'put': 0
            }
            usd_notional_value_bought_at_target = {
                'call': 0,
                'put': 0
            }
            # TODO would probably be better to search in the reverse order:
            # "at this given tick, am i selling a call & a put and is either exceeding X%?"
            # But that would require some new subgraph queries etc - so just going to do:
            # "are any of my positions at the target tick+width, and if so, do they exceed X%?"
            # So we'll maintain that approach for now
            self.log(f"Checking validity of open positions...", 2)
            if len(self.open_positions) > 0:
                # TODO: rename to ontarget_positions
                self.applicable_positions = []
                self.log(f"Checking if any open position fulfills target {target}", 2)
                for position_index, position in enumerate(self.open_positions):
                    self.request_payload["tokenId"] = position
                    self.log(f"Position: {self.request_payload['tokenId']}", 2)
                    response = await GatewayHttpClient.get_instance().api_request(
                        method="post",
                        path_url="options/unwrapTokenId",
                        params=self.request_payload,
                        fail_silently=False
                    )
                    # Step 1: Does this position contain a call & a put at the target strike & width?
                    self.log(f"Legs in position: {response['numberOfLegs']}", 2)
                    for leg_index in range(response['numberOfLegs']):
                        strike = response['legInfo'][leg_index]['strike']
                        width = response['legInfo'][leg_index]['width']
                        target_strike = ph.get_valid_tick(
                            int(np.floor(self.tick_location - target['tickToMaintain'])),
                            self.tickSpacing,
                            self.tickSpacing * ph.timescale_to_width(target['timescale'], self.tickSpacing)
                        )
                        if strike == target_strike && width == ph.timescale_to_width(target['timescale'], self.tickSpacing):
                            # TODO: check if leg is a sold call or a sold put
                            # TODO: if it is:
                            # - get the USD notional value of what is being sold:
                            #     - strike * positionSize * USD price of the asset
                            # - increment either volume_being_sold_at_target['call'] or volume_being_sold_at_target['put'] correspondingly
                            # TODO: Append this position onto applicable_positions

            # TODO: Next, query the subgraph for positions with any legs purchased against this tick/width
            # - if found, increment usd_volume_bought_at_target appropriately based the notional value of each long leg of each position

            # NOTE: This three-statemenet if-else tree _tries_ to handle market makers selling inequal amounts of puts and calls
            # However, if the inequality is driven by multi-leg positions that size the puts and calls differently,
            # we will fail to close your dragging positions and you will hit the positions-per-account limit pretty fast.
            # Works best with straddles/strangles, e.g. the first case:
            if (usd_volume_being_sold_at_target['call'] == usd_volume_being_sold_at_target['put']):
                if (
                    usd_volume_being_sold_at_target['call'] < target['min_notional_value_to_sell_USD'] ||
                    (
                        usd_volume_bought_at_target['call'] / usd_volume_being_sold_at_target['call'] > target['max_utilisation'] ||
                        usd_volume_bought_at_target['put'] / usd_volume_being_sold_at_target['put'] > target['max_utilisation']
                    )
                ):
                    usd_notional_value_to_sell = max(
                        target['min_notional_value_to_sell_USD'],
                        usd_volume_bought_at_target['put'] * (1 / target['max_utilisation']),
                        usd_volume_bought_at_target['call'] * (1 / target['max_utilisation']),
                    )
                    # TODO: Do a burn-and-mint to burn applicable_positions, then sell a straddle with a larger position size
                    # (Or, if applicable_positions == [], just mint the straddle)
                    # How large? Well, enough to meet the minimum (and maybe a little more:)
                    # usd_notional_value_to_sell / (strike * USD price of the asset)
                    # TODO: I might need to modify burnAndMint to accept > 1 position to do this...
                    # TODO: in the future, some day, we should let people sell a strangles here instead of straddles in a
                    # config above
                    # TODO: then:
                    # - add new position to open_positions & applicable_positions
                    # - remove burnt positions from open_positions & applicable_positions
            else if (
                usd_volume_being_sold_at_target['call'] < target['min_notional_value_to_sell_USD'] ||
                usd_volume_bought_at_target['call'] / usd_volume_being_sold_at_target['call'] > target['max_utilisation']
            ):
                usd_notional_value_to_sell = max(
                    target['min_notional_value_to_sell_USD'],
                    usd_volume_bought_at_target['call'] * (1 / target['max_utilisation']),
                )
                # TODO: Filter applicable_positions to just single-leg sold calls
                # TODO: Then, burn-and-mint to burn the old calls and sell a new call at size:
                # usd_notional_value_to_sell / (strike * USD price of the asset)
                # TODO: then:
                # - add new position to open_positions & applicable_positions
                # - remove burnt positions from open_positions & applicable_positions
            else if (
                usd_volume_being_sold_at_target['put'] < target['min_notional_value_to_sell_USD'] ||
                usd_volume_bought_at_target['put'] / usd_volume_being_sold_at_target['put'] > target['max_utilisation']
            ):
                # TODO: Filter applicable_positions to just single-leg sold puts
                # TODO: Then, burn-and-mint to burn the old puts and sell a new put at size:
                # usd_notional_value_to_sell / (strike * USD price of the asset)
                # TODO: then:
                # - add new position to open_positions & applicable_positions
                # - remove burnt positions from open_positions & applicable_positions

        if !maintain_offtarget_positions:
            offtarget_positions = [position for position in self.open_positions if position not in applicable_positions]
            # TODO: we need an endpoint to call burnOptions(tokenId[]); for now, iteratively calling burnOption(tokenId)
            for offtarget_position in offtarget_positions:
                updated_open_positions = [position for position in self.open_positions if position != offtarget_position]

                request_payload = {
                    "chain": chain,
                    "network": network,
                    "connector": connector,
                    "address": address,
                    "burnTokenId": offtarget_position,
                    "newPositionIdList": updated_open_positions,
                    "tickLimitLow": self.tickLimitLow,
                    "tickLimitHigh": self.tickLimitHigh
                }

                burn_response = await GatewayHttpClient.get_instance().api_request(
                    method="post",
                    path_url="options/burn",
                    params=request_payload,
                    fail_silently=False
                )

                await self.poll_transaction(chain, network, burn_response['txHash'])

                # TODO: check tx success
                # if it succeeded, update open_positions:
                self.open_positions = updated_open_positions

        self.ready=True

    async def initialize(self):
        self.t0_symbol, self.t1_symbol = list(self.trading_pair)[0].split("-")
        self.connector, self.chain, self.network = self.connector_chain_network.split("_")

        # fetch wallet address and print balances
        self.gateway_connections_conf = GatewayConnectionSetting.load()
        if len(self.gateway_connections_conf) < 1:
            self.log("No existing wallet.\n", 0)
            return
        self.wallet = [w for w in self.gateway_connections_conf if w["chain"] == self.chain and w["connector"] == self.connector and w["network"] == self.network]
        self.address = self.wallet[0]['wallet_address']

        self.request_payload = {
            "chain": self.chain,
            "network": self.network,
            "connector": self.connector,
            "address": self.address
        }

        self.log(f"Getting token addresses...", 2)
        self.log(f"POST /options/getTokenAddress [ connector: {self.connector}]", 0)
        self.request_payload["tokenSymbol"]= self.t0_symbol
        self.log(f"Finding token {self.t0_symbol}", 2)
        response = await GatewayHttpClient.get_instance().api_request(
            method="post",
            path_url="options/getTokenAddress",
            params=self.request_payload,
            fail_silently=False
        )

        self.request_payload.update({
            "t0_address": response['tokenAddress'],
            "token0Decimals": response['tokenDecimals']
        })
        self.log(f"t0 address: {self.request_payload['t0_address']}", 2)

        self.request_payload.update({
            "tokenSymbol": self.t1_symbol
        })
        self.log(f"Finding token {self.t1_symbol}", 2)
        response = await GatewayHttpClient.get_instance().api_request(
            method="post",
            path_url="options/getTokenAddress",
            params=self.request_payload,
            fail_silently=False
        )
        self.request_payload.update({
            "t1_address": response['tokenAddress'],
            "token1Decimals": response['tokenDecimals']
        })
        self.log(f"t1 address: {self.request_payload['t1_address']}", 2)

        self.log(f"Getting UniswapV3 token pool address...", 2)
        self.log(f"POST /options/checkUniswapPool [ connector: {self.connector}]", 0)

        self.request_payload.update({
            "fee": 500
        })
        response = await GatewayHttpClient.get_instance().api_request(
            method="post",
            path_url="options/checkUniswapPool",
            params=self.request_payload,
            fail_silently=False
        )
        self.request_payload.update({
            "uniswapV3PoolAddress": response["uniswapV3PoolAddress"]
        })
        self.log(f"Uniswap V3 token pool address: {self.request_payload['uniswapV3PoolAddress']}", 2)

        self.log(f"Getting Panoptic token pool address...", 2)
        self.log(f"POST /options/getPanopticPool [ connector: {self.connector}]", 0)

        self.request_payload.update({
            "univ3pool": self.request_payload['uniswapV3PoolAddress'] # redundant
        })
        response = await GatewayHttpClient.get_instance().api_request(
            method="post",
            path_url="options/getPanopticPool",
            params=self.request_payload,
            fail_silently=False
        )
        self.request_payload.update({
            "panopticPoolAddress": response["panopticPoolAddress"],
            "panopticPool": response["panopticPoolAddress"],
        })
        self.log(f"Panoptic token pool address: {self.request_payload['panopticPoolAddress']}", 1)

        self.log(f"Checking ticks...", 2)
        self.log(f"POST /options/getTickSpacingAndInitializedTicks [ connector: {self.connector} ]", 0)
        response = await GatewayHttpClient.get_instance().api_request(
            method="post",
            path_url="options/getTickSpacingAndInitializedTicks",
            params=self.request_payload,
            fail_silently=False
        )
        self.tickSpacing=response['tickSpacing']
        self.tick_locations=response['ticks']
        self.log(f"Tick spacing: {self.tickSpacing}", 1)
        self.log(f"Ticks: {self.tick_locations[0:10]}...{self.tick_locations[-10:]}", 2)

        self.wallet_address=self.address #redundant

        self.initialized=True

    # continuously poll for transaction until confirmed
    async def poll_transaction(self, chain, network, txHash):
        pending: bool = True
        while pending is True:
            self.log(f"POST /network/poll [ txHash: {txHash} ]", 0)
            pollData = await GatewayHttpClient.get_instance().get_transaction_status(
                chain,
                network,
                txHash
            )
            transaction_status = pollData.get("txStatus")
            if transaction_status == 1:
                self.log(f"Trade with transaction hash {txHash} has been executed successfully.", 1)
                pending = False
            elif transaction_status in [-1, 0, 2]:
                self.log(f"Trade is pending confirmation, Transaction hash: {txHash}", 1)
                await asyncio.sleep(2)
            else:
                self.log(f"Unknown txStatus: {transaction_status}", 1)
                self.log(f"{pollData}", 2)
                pending = False

    def log(self, message, triviality):
        if (triviality <= self.verbosity):
            self.logger().info(message)
