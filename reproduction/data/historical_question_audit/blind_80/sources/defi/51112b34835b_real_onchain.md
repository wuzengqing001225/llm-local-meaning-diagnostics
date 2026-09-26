# Source card: onchain

Corpus: defi
Source term ID: `real:onchain`

## Source glossary entry

(no source glossary entry)

## Recorded source usage contexts

1. The final quote collected to parameterize the auction before posting onchain.
2. API returns unexpected token amounts - Verify the amount is in the correct units (wei, not ether) - Confirm token decimals match the onchain contract - If using priceBounds , check the returned adjustedMinPrice / adjustedMaxPrice in the response — the server may have snapped to different tick boundaries than expected - For new pools, confirm initialPrice is a valid sqrtRatioX96 value Problem :
3. When trading from smart contracts, you must enforce slippage limits via amountOutMinimum or use an onchain price oracle.
4. How Uniswap AMM Routing Works AMM routing refers to swap paths that use onchain AMM liquidity.
5. How it works To propose a trade using the Uniswap v4 SDK, you construct a PoolKey that identifies the pool, then call the onchain Quoter contract to simulate the swap and get an expected output amount.
6. Retrieves current reserves, ticks, sqrtRatioX96, and position data onchain - Dependent Amount Computation :
7. Once an order is broadcast, fillers compete to submit it onchain when it becomes economically viable.
8. For onchain integrations (vaults, strategies, automated rebalancers), you interact directly with the v4 PositionManager contract using its action-encoding pattern.
9. Your app still handles signing and onchain submission.
10. With over 350 real-time data feeds across more than 50 blockchains, Stork enables onchain developers to build high-performance dApps.
11. Permit2 Flow Permit2 is a token approval system which uses an offchain (gasless) EIP-712 signed message to allow an onchain contract to spend tokens from a wallet within pre-defined bounds.
12. Invalid or missing x-api-key header Solutions : - Include the x-api-key header in every request - Confirm the API key was copied correctly (case-sensitive) Transaction revert scenarios If a transaction reverts onchain: 1.
13. Each component is composable and extensible so you can customize your launch flow while preserving clear onchain behavior.
14. Modifying it may cause funds to be lost or onchain reverts. - Always Validate :
15. Due to Ethereum's higher gas costs and 12-second block time, the system uses RFQ to improve pricing before users submit onchain transactions.
16. Permit signature rejected onchain - Some signing libraries require an explicit EIP712Domain type in the types object.

## Original documentation files

- [`uni:content/liquidity/liquidity-launchpad/overview.mdx`](../defi_docs/c10982900bd6_ntent_liquidity_liquidity-launchpad_overview.mdx.txt)
- [`uni:content/liquidity/liquidity-provisioning-api/integration-guide.mdx`](../defi_docs/924a171a560f_liquidity-provisioning-api_integration-guide.mdx.txt)
- [`uni:content/liquidity/overview.mdx`](../defi_docs/a27e071a3373_uni_content_liquidity_overview.mdx.txt)
- [`uni:content/liquidity/uniswapx/concepts/auction-types.mdx`](../defi_docs/5c97155ade9a_nt_liquidity_uniswapx_concepts_auction-types.mdx.txt)
- [`uni:content/liquidity/uniswapx/filling/faq.mdx`](../defi_docs/3455ce2cab77_uni_content_liquidity_uniswapx_filling_faq.mdx.txt)
- [`uni:content/liquidity/uniswapx/overview.mdx`](../defi_docs/a54d274b51b2_uni_content_liquidity_uniswapx_overview.mdx.txt)
- [`uni:content/protocols/v4/guides/reading-pool-reserves.mdx`](../defi_docs/955f51cc0e87_nt_protocols_v4_guides_reading-pool-reserves.mdx.txt)
- [`uni:content/trading/overview.mdx`](../defi_docs/7be721288fc9_uni_content_trading_overview.mdx.txt)
- [`uni:content/trading/swapping-api/amm-vs-uniswapx-routing.mdx`](../defi_docs/600df620ded0_trading_swapping-api_amm-vs-uniswapx-routing.mdx.txt)
- [`uni:content/trading/swapping-api/faqs.mdx`](../defi_docs/77c0dd102dba_uni_content_trading_swapping-api_faqs.mdx.txt)
- [`uni:content/trading/swapping-api/integration-guide.mdx`](../defi_docs/027740f52914_ntent_trading_swapping-api_integration-guide.mdx.txt)
- [`uni:content/unichain/index.mdx`](../defi_docs/322e703a54b0_uni_content_unichain_index.mdx.txt)
- [`uni:content/unichain/tools/account-abstraction.mdx`](../defi_docs/33b84434299e_i_content_unichain_tools_account-abstraction.mdx.txt)
- [`uni:content/unichain/tools/data-indexers.mdx`](../defi_docs/fb4a10dbfec6_uni_content_unichain_tools_data-indexers.mdx.txt)
- [`uni:content/unichain/tools/development-tools.mdx`](../defi_docs/375b71dd2285_uni_content_unichain_tools_development-tools.mdx.txt)
- [`uni:content/unichain/tools/faucets.mdx`](../defi_docs/6907c5b1d78a_uni_content_unichain_tools_faucets.mdx.txt)
- [`uni:content/unichain/tools/node-providers.mdx`](../defi_docs/ce1d00cea5bb_uni_content_unichain_tools_node-providers.mdx.txt)
- [`uni:content/unichain/tools/oracles.mdx`](../defi_docs/726914bd0713_uni_content_unichain_tools_oracles.mdx.txt)
