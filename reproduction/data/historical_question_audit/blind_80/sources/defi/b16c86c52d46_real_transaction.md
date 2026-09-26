# Source card: transaction

Corpus: defi
Source term ID: `real:transaction`

## Source glossary entry

If the exclusive filler fades or there is no exclusive filler, the system proceeds to a Dutch Auction (a descending price auction), where the user's transaction is posted for anyone to permissionlessly fill the order.

## Recorded source usage contexts

1. How It Works Tycho: - Fetches all protocol states and finds all WETH/USDC Uniswap pools. - Simulates a swap of 10 USDC to WETH on every pool. - Encodes a swap for the pool that has the most competitive price at that moment. - If you approve, it submits the required approval and then submits the swap transaction with your signer.
2. Given one token amount, computes the required amount of the other token using the Uniswap SDK - Transaction Creation :
3. If the approval is not yet in place, a fully-formed transaction is returned for the integrator to sign for each un-approved token. 2.
4. Execute the multicall The multicall is used to execute multiple calls in a single transaction For pools paired with native tokens (Ether), provide value in the contract call > Excess Ether is NOT refunded unless developers encoded SWEEP in the actions parameter For a full end-to-end script, developers should see v4-template script Create a pool only To initialize a Uniswap v4 Pool _without initial liquidity_, developers should call PoolManager.initialize() 1.
5. When reporting issues, include: - Request ID from the API response - Full request/response payloads (sanitize sensitive data such as wallet addresses if needed) - Protocol version and chain ID - Transaction hash (if the transaction was broadcast) - Timestamp of the request
6. Hex-encoded signed transaction data Important :
7. It uses a command-encoding pattern where you pack a sequence of actions (swap, settle input tokens, take output tokens) into byte arrays and execute them in a single transaction. > Safety Note :
8. Request ID from API response Full request/response payloads (sanitize sensitive data) Chain ID and transaction hash (if applicable) Timestamp of the request Is there a sandbox environment?
9. The API endpoints return pre-validated and correct data; modifying its value may cause funds to be lost or onchain transaction reverts.
10. You work with JSON responses, wallet signing, and transaction submission.
11. Specify exactly when your transaction should execute using block numbers or timestamps - Revert protection :
12. Endpoint Behavior ---------- ---------- /check_approval Returns ERC-20 approve calldata targeting the proxy contract /quote Does not include permitData /swap Swap transaction targets the proxy contract instead of Permit2 The proxy contract uses a deterministic CREATE2 deployment, so it has the same address on every chain: 0x0000000085E102724e78eCd2F45DC9cA239Affad .
13. Implement logic to resubmit bundles if they expire without execution Limitations - Single transaction per bundle :
14. Check transaction receipts to confirm execution or detect expiration 3.
15. This is a "gasful" transaction because the integrator will write the transaction to the chain to fill the swap.
16. The reactor checks that the required output amounts reach the order's recipients within the same transaction.

## Original documentation files

- [`uni:content/liquidity/liquidity-provisioning-api/getting-started.mdx`](../defi_docs/73e5d2a1f9b2_y_liquidity-provisioning-api_getting-started.mdx.txt)
- [`uni:content/liquidity/liquidity-provisioning-api/integration-guide.mdx`](../defi_docs/924a171a560f_liquidity-provisioning-api_integration-guide.mdx.txt)
- [`uni:content/liquidity/overview.mdx`](../defi_docs/a27e071a3373_uni_content_liquidity_overview.mdx.txt)
- [`uni:content/liquidity/uniswapx/filling/faq.mdx`](../defi_docs/3455ce2cab77_uni_content_liquidity_uniswapx_filling_faq.mdx.txt)
- [`uni:content/liquidity/uniswapx/filling/mainnet/filling-on-mainnet.mdx`](../defi_docs/3d77a03ae803__uniswapx_filling_mainnet_filling-on-mainnet.mdx.txt)
- [`uni:content/protocols/v4/guides/managing-liquidity/overview.mdx`](../defi_docs/8124e352d7ff_tocols_v4_guides_managing-liquidity_overview.mdx.txt)
- [`uni:content/trading/overview.mdx`](../defi_docs/7be721288fc9_uni_content_trading_overview.mdx.txt)
- [`uni:content/trading/swapping-api/building-prerequisites.mdx`](../defi_docs/ad020834b1b9__trading_swapping-api_building-prerequisites.mdx.txt)
- [`uni:content/trading/swapping-api/chained-actions-integration.mdx`](../defi_docs/54f2c9bc4a38_ing_swapping-api_chained-actions-integration.mdx.txt)
- [`uni:content/trading/swapping-api/chained-actions.mdx`](../defi_docs/c48613765062_content_trading_swapping-api_chained-actions.mdx.txt)
- [`uni:content/trading/swapping-api/concepts/no-permit2-workflow.mdx`](../defi_docs/86f8ddca9e4b_ng_swapping-api_concepts_no-permit2-workflow.mdx.txt)
- [`uni:content/trading/swapping-api/concepts/permit2.mdx`](../defi_docs/41bea6d14d01_ontent_trading_swapping-api_concepts_permit2.mdx.txt)
- [`uni:content/trading/swapping-api/concepts/swap-routing.mdx`](../defi_docs/4b120c091d8f_t_trading_swapping-api_concepts_swap-routing.mdx.txt)
- [`uni:content/trading/swapping-api/faqs.mdx`](../defi_docs/77c0dd102dba_uni_content_trading_swapping-api_faqs.mdx.txt)
- [`uni:content/trading/swapping-api/getting-started.mdx`](../defi_docs/9dbe16772070_content_trading_swapping-api_getting-started.mdx.txt)
- [`uni:content/trading/swapping-api/integration-guide.mdx`](../defi_docs/027740f52914_ntent_trading_swapping-api_integration-guide.mdx.txt)
- [`uni:content/unichain/getting-started/get-funds-on-unichain.mdx`](../defi_docs/30e059d474f1_ichain_getting-started_get-funds-on-unichain.mdx.txt)
- [`uni:content/unichain/guides/create-a-pool.mdx`](../defi_docs/a810bb6dc358_uni_content_unichain_guides_create-a-pool.mdx.txt)
- [`uni:content/unichain/guides/deploy-a-contract-through-thirdweb.mdx`](../defi_docs/d2faf9def6c3_in_guides_deploy-a-contract-through-thirdweb.mdx.txt)
- [`uni:content/unichain/guides/deploy-a-smart-contract.mdx`](../defi_docs/76da9a188a0a_tent_unichain_guides_deploy-a-smart-contract.mdx.txt)
