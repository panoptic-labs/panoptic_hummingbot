# Panoptic Additions to Hummingbot

We have added Panoptic-specific strategies, and Python helpers, to Hummingbot. You can run them out of this forked repository, and add your own via Pull Request.

Our main focus is the `panoptic_stayinrange_example.py`, which provides an example strategy for providing in-range market-making.

Use this gateway in tandem with [our Hummingbot Gateway fork](https://github.com/panoptic-labs/options_gateway) to run these automated Panoptic trading strategies.

## Setup

You can find instructions below about the general Hummingbot setup. To specifically run Panoptic strategies, you can:

Step 1: Get this repo's bot set up:

1. `git clone https://github.com/panoptic-labs/panoptic_hummingbot.git`
2. `cd panoptic_hummingbot`
3. `./install` (You may need to first [install anaconda](https://www.anaconda.com/download))
4. `conda activate hummingbot`
5. `./compile`
6. `./start`
7. The Hummingbot UI should now present itself! You can now set a password.
8. The Hummingbot Shell will now present itself. You can then `gateway generate-certs` to generate certificates and secure your Hummingbot instance.
    1. You’ll be prompted to set a password and it’ll list the directory those certificates are stored in.
    2. Copy the directory path it generates these certificates though.
    3. For many users, this was `~/panoptic_hummingbot/certs`. This is just a certs folder in the same folder as your hummingbot repo.

Step 2: Set up this fork of the Hummingbot Gateway:

1. `git clone git@github.com:panoptic-labs/options_gateway.git`
2. `cd options_gateway`
3. `yarn` (Ensure you’re using node 18.0.0 or higher - you can use [nvm](https://github.com/nvm-sh/nvm) to manage different node versions if needed.)
4. `yarn build`
5. Give permissions to the gateway setup script: `chmod a+x gateway-setup.sh`
6. Then run it: `./gateway-setup.sh`
7. It will prompt you to copy over the certs, enter the path (and possibly password) for those certs you just generated in (8)(i) above. Enter the path.

Step 3: Launch the Gateway:

`yarn start --passphrase=<passphrase>`

Finally, back in the Hummingbot UI tab, you should see Gateway: ONLINE in the navbar, on the right side to the left of > log pane.

1. You can connect to Panoptic's functionality by running `gateway connect panoptic` in the Hummingbot shell. You will be prompted about your RPC URL and private key to get started.
2. To confirm functionality, you can run `gateway balance` to see your Sepolia ETH balance.
3. You can then add more tokens to track balances of if you like via: `gateway connector-tokens panoptic_ethereum_sepolia ETH,WETH,T0,T1`. Your next call to `gateway balance` will show your balances of all those tokens. Be careful NOT to add spaces between the token tickers.
4. Be sure to approve your tokens to appropriate spenders, such as Uniswap or Panoptic contracts, to see valid gas estimates.

From here, you should be able to implement strategies in this repo that call to your local instance of the Gateway, with our Panoptic methods. You can, of course, write your own code as well that leverages this gateway, by just making calls to `localhost:8080`.

Note: If you run into issues about failures to connect, note that Hummingbot, by default, can make calls to Binance, which georestricts some requests.

## Use

You can try out one of the 3 stub strategies currently present in this repo's `./scripts/panoptic_*.py` files. From the Hummingbot terminal UI, run one of the scripts via `start --script {strategy's_file_name}.py`. The `panoptic_trading_strategy_stub.py` will report some statistics, while the burn and stayinrange strategies will attempt transactions. Do note you'll need to approve any tokens involved in the strategy ahead of time to see actual transactions go through.

Here's what you might roughly see if you run it successfully: ![Example](https://i.imgur.com/XBOUEyH.png)

Be sure to stop the example script with the `stop` command before starting others.

Please [reach out](https://discord.com/invite/8sX5Af2KXG) if you have any issues! Here's the general Hummingbot README:

--------

![Hummingbot](https://i.ibb.co/X5zNkKw/blacklogo-with-text.png)

----
[![License](https://img.shields.io/badge/License-Apache%202.0-informational.svg)](https://github.com/hummingbot/hummingbot/blob/master/LICENSE)
[![Twitter](https://img.shields.io/twitter/url?url=https://twitter.com/_hummingbot?style=social&label=_hummingbot)](https://twitter.com/_hummingbot)
[![Youtube](https://img.shields.io/youtube/channel/subscribers/UCxzzdEnDRbylLMWmaMjywOA)](https://www.youtube.com/@hummingbot)
[![Discord](https://img.shields.io/discord/530578568154054663?logo=discord&logoColor=white&style=flat-square)](https://discord.gg/hummingbot)

Hummingbot is an open source framework that helps you design and deploy automated trading strategies, or **bots**, that can run on many centralized or decentralized exchange. Over the past year, Hummingbot users have generated over $34 billion in trading volume across 140+ unique trading venues.

The Hummingbot codebase is free and publicly available under the Apache 2.0 open source license. Our mission is to **democratize high-frequency trading** by creating a global community of algorithmic traders and developers that share knowledge and contribute to the codebase.

## Quick Links

* [Website and Docs](https://hummingbot.org): Official Hummingbot website and documentation
* [Installation](https://hummingbot.org/installation/docker/): Install Hummingbot on various platforms
* [Discord](https://discord.gg/hummingbot): The main gathering spot for the global Hummingbot community
* [YouTube](https://www.youtube.com/c/hummingbot): Videos that teach you how to get the most of of Hummingbot
* [Twitter](https://twitter.com/_hummingbot): Get the latest announcements about Hummingbot
* [Reported Volumes](https://p.datadoghq.com/sb/a96a744f5-a15479d77992ccba0d23aecfd4c87a52): Reported trading volumes across all Hummingbot instances
* [Newsletter](https://hummingbot.substack.com): Get our newsletter whenever we ship a new release


## Exchange Connectors

Hummingbot connectors standardize REST and WebSocket API interfaces to different types of exchanges, enabling you to build sophisticated trading strategies that can be deployed across many exchanges with minimal changes.  We classify exchanges into the following categories:

* **CEX**: Centralized exchanges that take custody of your funds. Use API keys to connect with Hummingbot.
* **DEX**: Decentralized, non-custodial exchanges that operate on a blockchain. Use wallet keys to connect with Hummingbot.

In addition, connectors differ based on the type of market supported:

 * **CLOB Spot**: Connectors to spot markets on central limit order book (CLOB) exchanges
 * **CLOB Perp**: Connectors to perpetual futures markets on CLOB exchanges
 * **AMM**: Connectors to spot markets on Automatic Market Maker (AMM) decentralized exchanges

### Exchange Sponsors

We are grateful for the following exchanges who support the development and maintenance of Hummingbot via broker partnerships and sponsorships.

| Connector ID | Exchange | CEX/DEX | Market Type | Docs | Discount |
|----|------|-------|------|------|----------|
| `binance` | [Binance](https://accounts.binance.com/register?ref=CBWO4LU6) | CEX | CLOB Spot | [Docs](https://hummingbot.org/exchanges/binance/) | [![Sign up for Binance using Hummingbot's referral link for a 10% discount!](https://img.shields.io/static/v1?label=Fee&message=%2d10%25&color=orange)](https://accounts.binance.com/register?ref=CBWO4LU6) |
| `binance_perpetual` | [Binance](https://accounts.binance.com/register?ref=CBWO4LU6) | CEX | CLOB Perp | [Docs](https://hummingbot.org/exchanges/binance/) | [![Sign up for Binance using Hummingbot's referral link for a 10% discount!](https://img.shields.io/static/v1?label=Fee&message=%2d10%25&color=orange)](https://accounts.binance.com/register?ref=CBWO4LU6) |
| `gate_io` | [Gate.io](https://www.gate.io/referral/invite/HBOTGATE_0_103) | CEX | CLOB Spot | [Docs](https://hummingbot.org/exchanges/gate-io/) | [![Sign up for Gate.io using Hummingbot's referral link for a 10% discount!](https://img.shields.io/static/v1?label=Fee&message=%2d20%25&color=orange)](https://www.gate.io/referral/invite/HBOTGATE_0_103) |
| `gate_io_perpetual` | [Gate.io](https://www.gate.io/referral/invite/HBOTGATE_0_103) | CEX | CLOB Perp | [Docs](https://hummingbot.org/exchanges/gate-io/) | [![Sign up for Gate.io using Hummingbot's referral link for a 20% discount!](https://img.shields.io/static/v1?label=Fee&message=%2d20%25&color=orange)](https://www.gate.io/referral/invite/HBOTGATE_0_103) |
| `htx` | [HTX (Huobi)](https://www.htx.com.pk/invite/en-us/1h?invite_code=re4w9223) | CEX | CLOB Spot | [Docs](https://hummingbot.org/exchanges/huobi/) | [![Sign up for HTX using Hummingbot's referral link for a 20% discount!](https://img.shields.io/static/v1?label=Fee&message=%2d20%25&color=orange)](https://www.htx.com.pk/invite/en-us/1h?invite_code=re4w9223) |
| `kucoin` | [KuCoin](https://www.kucoin.com/r/af/hummingbot) | CEX | CLOB Spot | [Docs](https://hummingbot.org/exchanges/kucoin/) | [![Sign up for Kucoin using Hummingbot's referral link for a 20% discount!](https://img.shields.io/static/v1?label=Fee&message=%2d20%25&color=orange)](https://www.kucoin.com/r/af/hummingbot) |
| `kucoin_perpetual` | [KuCoin](https://www.kucoin.com/r/af/hummingbot) | CEX | CLOB Perp | [Docs](https://hummingbot.org/exchanges/kucoin/) | [![Sign up for Kucoin using Hummingbot's referral link for a 20% discount!](https://img.shields.io/static/v1?label=Fee&message=%2d20%25&color=orange)](https://www.kucoin.com/r/af/hummingbot) |
| `okx` | [OKX](https://www.okx.com/join/1931920269) | CEX | CLOB Spot | [Docs](https://hummingbot.org/exchanges/okx/okx/) | [![Sign up for Kucoin using Hummingbot's referral link for a 20% discount!](https://img.shields.io/static/v1?label=Fee&message=%2d20%25&color=orange)](https://www.okx.com/join/1931920269) |
| `okx_perpetual` | [OKX](https://www.okx.com/join/1931920269) | CEX | CLOB Perp | [Docs](https://hummingbot.org/exchanges/okx/okx/) | [![Sign up for Kucoin using Hummingbot's referral link for a 20% discount!](https://img.shields.io/static/v1?label=Fee&message=%2d20%25&color=orange)](https://www.okx.com/join/1931920269) |
| `dydx_v4_perpetual` | [dYdX](https://www.dydx.exchange/) | DEX | CLOB Perp | [Docs](https://hummingbot.org/exchanges/dydx/) | - |
| `hyperliquid_perpetual` | [Hyperliquid](https://hyperliquid.io/) | DEX | CLOB Perp | [Docs](https://hummingbot.org/exchanges/hyperliquid/) | - |
| `xrpl` | [XRP Ledger](https://xrpl.org/) | DEX | CLOB Spot | [Docs](https://hummingbot.org/exchanges/xrpl/) | - |

### Other Exchange Connectors

Currently, the master branch of Hummingbot also includes the following exchange connectors, which are maintained and updated through the Hummingbot Foundation governance process. See [Governance](https://hummingbot.org/governance/) for more information.

| Connector ID | Exchange | CEX/DEX | Type | Docs | Discount |
|----|------|-------|------|------|----------|
| `ascend_ex` | AscendEx | CEX | CLOB Spot | [Docs](https://hummingbot.org/exchanges/ascendex/) | - |
| `balancer` | Balancer | DEX | AMM | [Docs](https://hummingbot.org/exchanges/balancer/) | - |
| `bitfinex` | Bitfinex | CEX | CLOB Spot | [Docs](https://hummingbot.org/exchanges/bitfinex/) | - |
| `bitget_perpetual` | Bitget | CEX | CLOB Perp | [Docs](https://hummingbot.org/exchanges/bitget-perpetual/) | - |
| `bitmart` | BitMart | CEX | CLOB Spot | [Docs](https://hummingbot.org/exchanges/bitmart/) | - |
| `bitrue` | Bitrue | CEX | CLOB Spot | [Docs](https://hummingbot.org/exchanges/bitrue/) | - |
| `bitstamp` | Bitstamp | CEX | CLOB Spot | [Docs](https://hummingbot.org/exchanges/bitstamp/) | - |
| `btc_markets` | BTC Markets | CEX | CLOB Spot | [Docs](https://hummingbot.org/exchanges/btc-markets/) | - |
| `bybit` | Bybit | CEX | CLOB Spot | [Docs](https://hummingbot.org/exchanges/bybit/) | - |
| `bybit_perpetual` | Bybit | CEX | CLOB Perp | [Docs](https://hummingbot.org/exchanges/bybit/) | - |
| `carbon` | Carbon | DEX | AMM | [Docs](https://hummingbot.org/exchanges/carbon/) | - |
| `coinbase_advanced_trade` | Coinbase | CEX | CLOB Spot | [Docs](https://hummingbot.org/exchanges/coinbase/) | - |
| `cube` | Cube | CEX | CLOB Spot | [Docs](https://hummingbot.org/exchanges/cube/) | - |
| `curve` | Curve | DEX | AMM | [Docs](https://hummingbot.org/exchanges/curve/) | - |
| `dexalot` | Dexalot | DEX | CLOB Spot | [Docs](https://hummingbot.org/exchanges/dexalot/) | - |
| `hashkey` | HashKey | CEX | CLOB Spot | [Docs](https://hummingbot.org/exchanges/hashkey/) | - |
| `hashkey_perpetual` | HashKey | CEX | CLOB Perp | [Docs](https://hummingbot.org/exchanges/hashkey/) | - |
| `injective_v2` | Injective Helix | DEX | CLOB Spot | [Docs](https://hummingbot.org/exchanges/injective/) | - |
| `injective_v2_perpetual` | Injective Helix | DEX | CLOB Perp | [Docs](https://hummingbot.org/exchanges/injective/) | - |
| `kraken` | Kraken | CEX | CLOB Spot | [Docs](https://hummingbot.org/exchanges/kraken/) | - |
| `mad_meerkat` | Mad Meerkat | DEX | AMM | [Docs](https://hummingbot.org/exchanges/mad-meerkat/) | - |
| `mexc` | MEXC | CEX | CLOB Spot | [Docs](https://hummingbot.org/exchanges/mexc/) | - |
| `ndax` | NDAX | CEX | CLOB Spot | [Docs](https://hummingbot.org/exchanges/ndax/) | - |
| `openocean` | OpenOcean | DEX | AMM | [Docs](https://hummingbot.org/exchanges/openocean/) | - |
| `pancakeswap` | PancakeSwap | DEX | AMM | [Docs](https://hummingbot.org/exchanges/pancakeswap/) | - |
| `pangolin` | Pangolin | CEX | DEX | [Docs](https://hummingbot.org/exchanges/pangolin/) | - |
| `polkadex` | Polkadex | DEX | CLOB Spot | [Docs](https://hummingbot.org/exchanges/polkadex/) | - |
| `quickswap` | QuickSwap | DEX | AMM | [Docs](https://hummingbot.org/exchanges/quickswap/) | - |
| `sushiswap` | SushiSwap | DEX | AMM | [Docs](https://hummingbot.org/exchanges/sushiswap/) | - |
| `tinyman` | Tinyman | DEX | AMM | [Docs](https://hummingbot.org/exchanges/tinyman/) | - |
| `traderjoe` | Trader Joe | DEX | AMM | [Docs](https://hummingbot.org/exchanges/traderjoe/) | - |
| `uniswap` | Uniswap | DEX | AMM | [Docs](https://hummingbot.org/exchanges/uniswap/) | - |
| `vertex` | Vertex | DEX | CLOB Spot | [Docs](https://hummingbot.org/exchanges/vertex/) | - |
| `vvs` | VVS | DEX | AMM | [Docs](https://hummingbot.org/exchanges/vvs/) | - |
| `xsswap` | XSSwap | DEX | AMM | [Docs](https://hummingbot.org/exchanges/xswap/) | - |

## Other Hummingbot Repos

* [Deploy](https://github.com/hummingbot/deploy): Deploy Hummingbot in various configurations with Docker
* [Dashboard](https://github.com/hummingbot/dashboard): Web app that help you create, backtest, deploy, and manage Hummingbot instances
* [Quants Lab](https://github.com/hummingbot/quants-lab): Juypter notebooks that enable you to fetch data and perform research using Hummingbot
* [Gateway](https://github.com/hummingbot/gateway): Typescript based API client for DEX connectors
* [Hummingbot Site](https://github.com/hummingbot/hummingbot-site): Official documentation for Hummingbot - we welcome contributions here too!

## Contributions

The Hummingbot architecture features modular components that can be maintained and extended by individual community members.

We welcome contributions from the community! Please review these [guidelines](./CONTRIBUTING.md) before submitting a pull request.

To have your exchange connector or other pull request merged into the codebase, please submit a New Connector Proposal or Pull Request Proposal, following these [guidelines](https://hummingbot.org/governance/proposals/). Note that you will need some amount of [HBOT tokens](https://etherscan.io/token/0xe5097d9baeafb89f9bcb78c9290d545db5f9e9cb) in your Ethereum wallet to submit a proposal.

## Legal

* **License**: Hummingbot is open source and licensed under [Apache 2.0](./LICENSE).
* **Data collection**: See [Reporting](https://hummingbot.org/reporting/) for information on anonymous data collection and reporting in Hummingbot.
