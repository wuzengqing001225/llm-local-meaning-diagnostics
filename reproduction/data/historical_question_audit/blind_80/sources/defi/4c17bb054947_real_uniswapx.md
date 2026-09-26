# Source card: uniswapx

Corpus: defi
Source term ID: `real:uniswapx`

## Source glossary entry

UniswapX filling UniswapX is an auction-based protocol where fillers (market makers) compete to execute user swap orders.

## Recorded source usage contexts

1. The UniswapX Quote contains auction parameters, which the user signs to create a gasless offchain message.
2. Below that, UniswapX is included only when its quote improves on the AMM route by at least 0.2%.
3. The Order Service gets a soft quote to decide between UniswapX and Classic routing.
4. The amount is too low to be quoted by UniswapX.
5. With the default BEST_PRICE routing preference, the API considers UniswapX alongside the Uniswap Protocol and selects the most efficient route based on current inputs.
6. If the quote response returns a UniswapX routing type ( DUTCH_V2 , DUTCH_V3 , or PRIORITY ), include the x-erc20eth-enabled: true header when you submit the signed order to /order .
7. Anyone can fill orders on UniswapX.
8. See AMM vs UniswapX routing for details.
9. Integrate as a quoter on UniswapX to compete for exclusive filling rights on Ethereum mainnet.
10. UniswapX on Ethereum uses a two-phase auction system that balances execution quality with gas efficiency.
11. Chain coverage Solver activity varies across chains, so UniswapX route frequency can differ by network.
12. Begin sending quotes and orders to beta via the UniswapX CLI.
13. Routing Outcomes - To perform a swap using only Uniswap protocol liquidity pools, specify protocols as V2 , V3 , and/or V4 . - To perform a swap using only UniswapX protocol liquidity, specify protocols as UNISWAPX_V2 or UNISWAPX_V3 .
14. Sample fill contract implementations are provided in the UniswapX repo:
15. All UniswapX quote requests require a minimum swap value of 300 USDC equivalent across all supported chains.
16. Trading on UniswapX To trade using UniswapX, swappers create orders that define their auction parameters and price tolerance.

## Original documentation files

- [`uni:content/liquidity/liquidity-provisioning-api/integration-guide.mdx`](../defi_docs/924a171a560f_liquidity-provisioning-api_integration-guide.mdx.txt)
- [`uni:content/liquidity/overview.mdx`](../defi_docs/a27e071a3373_uni_content_liquidity_overview.mdx.txt)
- [`uni:content/liquidity/uniswapx/concepts/architecture.mdx`](../defi_docs/b5b605c75168_ent_liquidity_uniswapx_concepts_architecture.mdx.txt)
- [`uni:content/liquidity/uniswapx/concepts/auction-types.mdx`](../defi_docs/5c97155ade9a_nt_liquidity_uniswapx_concepts_auction-types.mdx.txt)
- [`uni:content/liquidity/uniswapx/concepts/uniswaprfq.mdx`](../defi_docs/ba1247e27d67_ntent_liquidity_uniswapx_concepts_uniswaprfq.mdx.txt)
- [`uni:content/liquidity/uniswapx/deployments.mdx`](../defi_docs/51110dd311b3_uni_content_liquidity_uniswapx_deployments.mdx.txt)
- [`uni:content/liquidity/uniswapx/filling/dutch-v3-chains/filling-on-dutch-v3-chains.md`](../defi_docs/f2f6daa53c1c_ng_dutch-v3-chains_filling-on-dutch-v3-chains.md.txt)
- [`uni:content/liquidity/uniswapx/filling/faq.mdx`](../defi_docs/3455ce2cab77_uni_content_liquidity_uniswapx_filling_faq.mdx.txt)
- [`uni:content/liquidity/uniswapx/filling/mainnet/become-a-quoter.mdx`](../defi_docs/f2603805b375_ity_uniswapx_filling_mainnet_become-a-quoter.mdx.txt)
- [`uni:content/liquidity/uniswapx/filling/mainnet/filling-on-mainnet.mdx`](../defi_docs/3d77a03ae803__uniswapx_filling_mainnet_filling-on-mainnet.mdx.txt)
- [`uni:content/liquidity/uniswapx/filling/overview.mdx`](../defi_docs/a237b1143fe4__content_liquidity_uniswapx_filling_overview.mdx.txt)
- [`uni:content/liquidity/uniswapx/overview.mdx`](../defi_docs/a54d274b51b2_uni_content_liquidity_uniswapx_overview.mdx.txt)
- [`uni:content/trading/overview.mdx`](../defi_docs/7be721288fc9_uni_content_trading_overview.mdx.txt)
- [`uni:content/trading/swapping-api/amm-vs-uniswapx-routing.mdx`](../defi_docs/600df620ded0_trading_swapping-api_amm-vs-uniswapx-routing.mdx.txt)
- [`uni:content/trading/swapping-api/chained-actions-integration.mdx`](../defi_docs/54f2c9bc4a38_ing_swapping-api_chained-actions-integration.mdx.txt)
- [`uni:content/trading/swapping-api/chained-actions.mdx`](../defi_docs/c48613765062_content_trading_swapping-api_chained-actions.mdx.txt)
- [`uni:content/trading/swapping-api/common-errors.mdx`](../defi_docs/07df3cb69323_i_content_trading_swapping-api_common-errors.mdx.txt)
- [`uni:content/trading/swapping-api/concepts/no-permit2-workflow.mdx`](../defi_docs/86f8ddca9e4b_ng_swapping-api_concepts_no-permit2-workflow.mdx.txt)
- [`uni:content/trading/swapping-api/concepts/permit2.mdx`](../defi_docs/41bea6d14d01_ontent_trading_swapping-api_concepts_permit2.mdx.txt)
- [`uni:content/trading/swapping-api/concepts/swap-routing.mdx`](../defi_docs/4b120c091d8f_t_trading_swapping-api_concepts_swap-routing.mdx.txt)
