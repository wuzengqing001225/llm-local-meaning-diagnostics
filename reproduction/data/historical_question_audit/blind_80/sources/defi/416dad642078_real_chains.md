# Source card: chains

Corpus: defi
Source term ID: `real:chains`

## Source glossary entry

Block times on these chains are roughly 1 second.

## Recorded source usage contexts

1. Reactor Description --- --- PriorityOrderReactor Settles orders via filler competition using priority gas fees V2DutchOrderReactor Settles linear decay Dutch orders using block timestamp for auction decay V3DutchOrderReactor Settles linear decay Dutch orders using block number instead of timestamp, enabling finer granularity on chains like Arbitrum (250ms block resolution) ExclusiveDutchOrderReactor Settles linear decay Dutch orders with exclusivity period before decay begins LimitOrderReactor Settles simple static limit orders Fill Contracts Order fill contracts _fill_ UniswapX orders.
2. Unichain is a DeFi-focused Ethereum L2 designed for fast blocks, lower costs, and efficient onchain liquidity across chains.
3. Routing patterns The router automatically selects one of three patterns, based on the tokens and chains involved.
4. It currently serves historical onchain data ingested from 100+ EVM chains, including Unichain Sepolia.
5. Ethereum measures the exclusivity window and decay in time, while the other chains measure them in block numbers.
6. Access to Reliable RPC Infrastructure You must operate or use a provider that supports: - The chains you wish to trade on (e.g., Ethereum, Unichain, other L2s) - Knowledge of how to troubleshoot RPC submission failures 4.
7. Once the exclusivity window ends (at decayStartBlock on the DutchV3 chains, decayStartTime on Ethereum), all fillers compete equally in the Dutch auction.
8. This same RFQ and exclusive Dutch auction also runs on other UniswapX chains, settled through the DutchV3 reactor.
9. Use the tokenInChainId field to filter, and respond with HTTP status code 204 for chains you do not quote.
10. UniswapX is available only on selected chains, and constraints can vary by chain.
11. UniswapX uses RFQ to parameterize orders across supported chains.
12. Those tokens and their chains are available here: https://unsupportedtokens.uniswap.org/.
13. UniswapX Chain Support UniswapX is available on the following chains:
14. See Supported Chains for current coverage and constraints.
15. Use EIP-1559 on supported chains Slippage configuration Balance protection vs execution success:
16. All UniswapX quote requests require a minimum swap value of 300 USDC equivalent across all supported chains.

## Original documentation files

- [`uni:content/liquidity/liquidity-provisioning-api/integration-guide.mdx`](../defi_docs/924a171a560f_liquidity-provisioning-api_integration-guide.mdx.txt)
- [`uni:content/liquidity/uniswapx/concepts/architecture.mdx`](../defi_docs/b5b605c75168_ent_liquidity_uniswapx_concepts_architecture.mdx.txt)
- [`uni:content/liquidity/uniswapx/concepts/auction-types.mdx`](../defi_docs/5c97155ade9a_nt_liquidity_uniswapx_concepts_auction-types.mdx.txt)
- [`uni:content/liquidity/uniswapx/filling/dutch-v3-chains/filling-on-dutch-v3-chains.md`](../defi_docs/f2f6daa53c1c_ng_dutch-v3-chains_filling-on-dutch-v3-chains.md.txt)
- [`uni:content/liquidity/uniswapx/filling/faq.mdx`](../defi_docs/3455ce2cab77_uni_content_liquidity_uniswapx_filling_faq.mdx.txt)
- [`uni:content/liquidity/uniswapx/filling/mainnet/filling-on-mainnet.mdx`](../defi_docs/3d77a03ae803__uniswapx_filling_mainnet_filling-on-mainnet.mdx.txt)
- [`uni:content/protocols/v4/guides/reading-pool-reserves.mdx`](../defi_docs/955f51cc0e87_nt_protocols_v4_guides_reading-pool-reserves.mdx.txt)
- [`uni:content/trading/swapping-api/amm-vs-uniswapx-routing.mdx`](../defi_docs/600df620ded0_trading_swapping-api_amm-vs-uniswapx-routing.mdx.txt)
- [`uni:content/trading/swapping-api/building-prerequisites.mdx`](../defi_docs/ad020834b1b9__trading_swapping-api_building-prerequisites.mdx.txt)
- [`uni:content/trading/swapping-api/chained-actions-integration.mdx`](../defi_docs/54f2c9bc4a38_ing_swapping-api_chained-actions-integration.mdx.txt)
- [`uni:content/trading/swapping-api/chained-actions.mdx`](../defi_docs/c48613765062_content_trading_swapping-api_chained-actions.mdx.txt)
- [`uni:content/trading/swapping-api/common-errors.mdx`](../defi_docs/07df3cb69323_i_content_trading_swapping-api_common-errors.mdx.txt)
- [`uni:content/trading/swapping-api/concepts/swap-routing.mdx`](../defi_docs/4b120c091d8f_t_trading_swapping-api_concepts_swap-routing.mdx.txt)
- [`uni:content/trading/swapping-api/faqs.mdx`](../defi_docs/77c0dd102dba_uni_content_trading_swapping-api_faqs.mdx.txt)
- [`uni:content/trading/swapping-api/getting-started.mdx`](../defi_docs/9dbe16772070_content_trading_swapping-api_getting-started.mdx.txt)
- [`uni:content/trading/swapping-api/integration-guide.mdx`](../defi_docs/027740f52914_ntent_trading_swapping-api_integration-guide.mdx.txt)
- [`uni:content/trading/swapping-api/supported-chains.mdx`](../defi_docs/619120f7e7cb_ontent_trading_swapping-api_supported-chains.mdx.txt)
- [`uni:content/unichain/getting-started/setting-up-a-wallet.mdx`](../defi_docs/cae92978e69a_unichain_getting-started_setting-up-a-wallet.mdx.txt)
- [`uni:content/unichain/index.mdx`](../defi_docs/322e703a54b0_uni_content_unichain_index.mdx.txt)
- [`uni:content/unichain/tools/account-abstraction.mdx`](../defi_docs/33b84434299e_i_content_unichain_tools_account-abstraction.mdx.txt)
