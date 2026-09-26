# Source card: contracts

Corpus: defi
Source term ID: `real:contracts`

## Source glossary entry

!Modular Contracts Overview Modular contracts are composed of two components: - Core Contract : smart contracts that serve as the foundation of the modular contract - Module Contract : smart contracts that are installed on top of the core contract You can think of Modular Contracts like building bricks.

## Recorded source usage contexts

1. Deploy these contracts on each chain you want to support.
2. Retrieve open orders and monitor order status. - Via smart contracts :
3. Api3 Api3 delivers first-party oracles that pay you, connecting real-world data directly to smart contracts while reclaiming lost value through Oracle Extractable Value (OEV).
4. Executor contracts must call reactor.executeWithCallback or reactor.executeBatchWithCallback , and can specify arbitrary callback data passed into the reactorCallback call.
5. Supported networks - Unichain Mainnet - Unichain Sepolia Testnet GhostGraph GhostGraph makes it easy to build blazingly fast indexers (subgraphs) for smart contracts.
6. Supported networks - Unichain Mainnet - Unichain Sepolia Testnet Thirdweb Thirdweb is a full-stack, open-source development platform for Web3 apps and games, offering client-side SDKs for user onboarding and identity, backend servers for gas sponsorship and onchain transactions, data infrastructure for blockchain indexing, and audited smart contracts with deployment tooling.
7. Modular contracts is a framework that enables the creation of highly customizable and upgradeable smart contracts.
8. Getting historical data on smart contracts can be frustrating when building a dapp.
9. Deploy Strategy : call LiquidityLauncher.distributeToken() to deploy strategy and auction contracts. 3.
10. Smart Contracts (Native) Building directly against the Uniswap v4 smart contracts gives you maximum control and composability.
11. Hooks are deployed contracts and are called by the Uniswap v4 PoolManager for permissionless execution.
12. More sophisticated fillers can implement arbitrarily complex strategies by deploying their own Executor contracts.
13. Direct to Canonical Bridge You can also fund a Unichain wallet directly by sending ETH to the canonical Unichain bridge contracts:
14. On Unichain, developers can leverage: - Solidity Contracts Library:
15. Reactor Description --- --- PriorityOrderReactor Settles orders via filler competition using priority gas fees V2DutchOrderReactor Settles linear decay Dutch orders using block timestamp for auction decay V3DutchOrderReactor Settles linear decay Dutch orders using block number instead of timestamp, enabling finer granularity on chains like Arbitrum (250ms block resolution) ExclusiveDutchOrderReactor Settles linear decay Dutch orders with exclusivity period before decay begins LimitOrderReactor Settles simple static limit orders Fill Contracts Order fill contracts _fill_ UniswapX orders.
16. How to integrate The Liquidity Launchpad is accessed via smart contract interactions with the Liquidity Launcher and strategy contracts onchain.

## Original documentation files

- [`uni:content/liquidity/liquidity-launchpad/overview.mdx`](../defi_docs/c10982900bd6_ntent_liquidity_liquidity-launchpad_overview.mdx.txt)
- [`uni:content/liquidity/overview.mdx`](../defi_docs/a27e071a3373_uni_content_liquidity_overview.mdx.txt)
- [`uni:content/liquidity/uniswapx/concepts/architecture.mdx`](../defi_docs/b5b605c75168_ent_liquidity_uniswapx_concepts_architecture.mdx.txt)
- [`uni:content/liquidity/uniswapx/filling/dutch-v3-chains/filling-on-dutch-v3-chains.md`](../defi_docs/f2f6daa53c1c_ng_dutch-v3-chains_filling-on-dutch-v3-chains.md.txt)
- [`uni:content/liquidity/uniswapx/filling/faq.mdx`](../defi_docs/3455ce2cab77_uni_content_liquidity_uniswapx_filling_faq.mdx.txt)
- [`uni:content/liquidity/uniswapx/filling/mainnet/become-a-quoter.mdx`](../defi_docs/f2603805b375_ity_uniswapx_filling_mainnet_become-a-quoter.mdx.txt)
- [`uni:content/liquidity/uniswapx/filling/mainnet/filling-on-mainnet.mdx`](../defi_docs/3d77a03ae803__uniswapx_filling_mainnet_filling-on-mainnet.mdx.txt)
- [`uni:content/protocols/v4/concepts/architecture.mdx`](../defi_docs/3524cee55370_i_content_protocols_v4_concepts_architecture.mdx.txt)
- [`uni:content/trading/overview.mdx`](../defi_docs/7be721288fc9_uni_content_trading_overview.mdx.txt)
- [`uni:content/trading/swapping-api/concepts/no-permit2-workflow.mdx`](../defi_docs/86f8ddca9e4b_ng_swapping-api_concepts_no-permit2-workflow.mdx.txt)
- [`uni:content/trading/swapping-api/concepts/permit2.mdx`](../defi_docs/41bea6d14d01_ontent_trading_swapping-api_concepts_permit2.mdx.txt)
- [`uni:content/unichain/getting-started/get-funds-on-unichain.mdx`](../defi_docs/30e059d474f1_ichain_getting-started_get-funds-on-unichain.mdx.txt)
- [`uni:content/unichain/guides/deploy-a-contract-through-thirdweb.mdx`](../defi_docs/d2faf9def6c3_in_guides_deploy-a-contract-through-thirdweb.mdx.txt)
- [`uni:content/unichain/guides/deploy-a-smart-contract.mdx`](../defi_docs/76da9a188a0a_tent_unichain_guides_deploy-a-smart-contract.mdx.txt)
- [`uni:content/unichain/guides/subgraph-unichain.mdx`](../defi_docs/46cf2a018938_ni_content_unichain_guides_subgraph-unichain.mdx.txt)
- [`uni:content/unichain/guides/transfer-usdc.mdx`](../defi_docs/c0a1ed4d4c8c_uni_content_unichain_guides_transfer-usdc.mdx.txt)
- [`uni:content/unichain/index.mdx`](../defi_docs/322e703a54b0_uni_content_unichain_index.mdx.txt)
- [`uni:content/unichain/tools/data-feeds.mdx`](../defi_docs/84ef01782c44_uni_content_unichain_tools_data-feeds.mdx.txt)
- [`uni:content/unichain/tools/data-indexers.mdx`](../defi_docs/fb4a10dbfec6_uni_content_unichain_tools_data-indexers.mdx.txt)
- [`uni:content/unichain/tools/development-tools.mdx`](../defi_docs/375b71dd2285_uni_content_unichain_tools_development-tools.mdx.txt)
