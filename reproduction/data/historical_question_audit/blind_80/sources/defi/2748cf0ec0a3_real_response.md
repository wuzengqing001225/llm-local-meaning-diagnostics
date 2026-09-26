# Source card: response

Corpus: defi
Source term ID: `real:response`

## Source glossary entry

This response is abbreviated: each step also carries token, amount, and gas fields, and the remaining steps are omitted here.

## Recorded source usage contexts

1. Call /quote The quote response may contain a Permit2 message if the swapper needs to authorize Permit2 to spend tokens through the Universal Router. 2.
2. If the quote response returns a UniswapX routing type ( DUTCH_V2 , DUTCH_V3 , or PRIORITY ), include the x-erc20eth-enabled: true header when you submit the signed order to /order .
3. The API computes the corresponding decimal prices for the response.
4. Implementation steps Get quote with permit data Sign the permit Submit to /swap Broadcast transaction Error Handling HTTP status codes Code Meaning ------ --------- 200 Request succeeded 400 Invalid request (validation error) 401 Invalid API key 429 Rate limit exceeded 500 API error (retry with backoff) 503 Temporary unavailability (retry) Error response format Common errors No quotes available Cause :
5. Example request Response Uniswap v2 — /lp/create_classic Uniswap v2 positions always span the full price range (0 to ∞).
6. In the Uniswap API, UniswapX routes behave as follows: - A /quote response may include a UniswapX route when the swap is eligible and a solver can fill it - The API response returns a UniswapX path rather than AMM split-route details - The solver submits the onchain order fill, and the swapper signs the required approval or order signature A UniswapX quote is produced in two phases.
7. The API will return a permitData in the /quote response when one must be signed in order to perform the swap.
8. If a quote fails, the response includes helpful information to understand the problem with the request.
9. Example diff response Getting Help Join the Uniswap Discord and look for the Unichain channel.
10. Always display the adjusted prices returned in the response to the user — not the original input values.
11. Similarly, extremely large orders might exceed available liquidity from quoters. - Response Latency :
12. The API will return a permitData in the /quote response when one must be signed in order to perform the swap.
13. If you do not wish to respond to a quote request, you must return an empty response with status code 204 .
14. If a wallet signs a Permit2 message from an earlier /quote response and later initiates a swap using a new quote, the old signature may no longer be valid, especially for quotes that route through UniswapX which use shorter expiration windows.
15. This response is abbreviated: each step also carries token, amount, and gas fields, and the remaining steps are omitted here.
16. Error Handling HTTP status codes Code Meaning --- --- 200 Request succeeded 400 Invalid request (validation error) 401 Invalid API key 429 Rate limit exceeded 500 API error (retry with backoff) 503 Temporary unavailability (retry) Error response format Common errors v2 fee claim attempt Cause :

## Original documentation files

- [`uni:content/liquidity/liquidity-provisioning-api/getting-started.mdx`](../defi_docs/73e5d2a1f9b2_y_liquidity-provisioning-api_getting-started.mdx.txt)
- [`uni:content/liquidity/liquidity-provisioning-api/integration-guide.mdx`](../defi_docs/924a171a560f_liquidity-provisioning-api_integration-guide.mdx.txt)
- [`uni:content/liquidity/uniswapx/filling/faq.mdx`](../defi_docs/3455ce2cab77_uni_content_liquidity_uniswapx_filling_faq.mdx.txt)
- [`uni:content/liquidity/uniswapx/filling/mainnet/become-a-quoter.mdx`](../defi_docs/f2603805b375_ity_uniswapx_filling_mainnet_become-a-quoter.mdx.txt)
- [`uni:content/trading/swapping-api/agent-attribution.mdx`](../defi_docs/8c21a458338f_ntent_trading_swapping-api_agent-attribution.mdx.txt)
- [`uni:content/trading/swapping-api/amm-vs-uniswapx-routing.mdx`](../defi_docs/600df620ded0_trading_swapping-api_amm-vs-uniswapx-routing.mdx.txt)
- [`uni:content/trading/swapping-api/chained-actions-integration.mdx`](../defi_docs/54f2c9bc4a38_ing_swapping-api_chained-actions-integration.mdx.txt)
- [`uni:content/trading/swapping-api/common-errors.mdx`](../defi_docs/07df3cb69323_i_content_trading_swapping-api_common-errors.mdx.txt)
- [`uni:content/trading/swapping-api/concepts/permit2.mdx`](../defi_docs/41bea6d14d01_ontent_trading_swapping-api_concepts_permit2.mdx.txt)
- [`uni:content/trading/swapping-api/faqs.mdx`](../defi_docs/77c0dd102dba_uni_content_trading_swapping-api_faqs.mdx.txt)
- [`uni:content/trading/swapping-api/getting-started.mdx`](../defi_docs/9dbe16772070_content_trading_swapping-api_getting-started.mdx.txt)
- [`uni:content/trading/swapping-api/integration-guide.mdx`](../defi_docs/027740f52914_ntent_trading_swapping-api_integration-guide.mdx.txt)
- [`uni:content/unichain/technical-information/advanced-txn.mdx`](../defi_docs/37a782013d51__unichain_technical-information_advanced-txn.mdx.txt)
- [`uni:content/unichain/technical-information/flashblocks.mdx`](../defi_docs/d1e8196fec20_t_unichain_technical-information_flashblocks.mdx.txt)
