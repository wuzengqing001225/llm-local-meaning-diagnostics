# Source card: approval

Corpus: defi
Source term ID: `real:approval`

## Source glossary entry

If the approval is not yet in place, a fully-formed transaction is returned for the integrator to sign for each un-approved token.

## Recorded source usage contexts

1. If the approval is not yet in place, a fully-formed transaction is returned to the integrator to sign. 2.
2. MIGRATE is a supported action value on /lp/check_approval , which returns the approvals needed to migrate a position (for example, approval of the Uniswap v3 NFT).
3. The integrator checks if they have given the necessary approval to the Permit2 contract to spend the token they intended to swap through a /check_approval request. 1.
4. In this flow, the swapping wallet grants a standard ERC-20 approval directly to a proxy contract, which then routes the swap through the Universal Router.
5. However, using the Permit2 flow whenever possible is recommended , as it provides better security and a more flexible approval model for users.
6. Approval Flow Before any LP transaction can be executed, tokens must be approved for spending.
7. If the approval is not yet in place, a fully-formed transaction is returned for the integrator to sign for each un-approved token. 2.
8. Any required approval appears as an explicit step inside the plan.
9. The swapping wallet (your user) signs the swap transaction and you broadcast it Enabling the Proxy Approval Flow The Uniswap API exposes a request header that disables Permit2 behavior: x-permit2-disabled When this header is included, the API switches to the proxy approval model.
10. Permit2 Flow Permit2 is a token approval system which uses an offchain (gasless) EIP-712 signed message to allow an onchain contract to spend tokens from a wallet within pre-defined bounds.
11. Approval key parameters Parameter Description --- --- protocol V2 , V3 , or V4 chainId The blockchain network lpTokens Array of { tokenAddress, amount } objects action CREATE , INCREASE , DECREASE , or MIGRATE generatePermitAsTransaction If true , returns permit as a transaction instead of typed data Creating a Position Uniswap v3 and Uniswap v4 — /lp/create The caller specifies a price range and the amount of one token.
12. The API will identify this scenario and provide both revoke and approval calldata for the swapper to sign. - As a best practice, call /check_approval before a swapper performs a swap to ensure they have a valid approval.
13. In the Permit2 flow, the API simulates three calls to account for the wallet's approval state: 1. approve(token to Permit2) 2.
14. The integrator checks if they have the necessary approval to send token(s) to the desired pool using a /check_approval request. 1.
15. Transaction Flow Comparison Both flows ultimately execute swaps through the Universal Router , but the approval model differs as shown below:
16. Onchain approval transaction reverts - Check that gasLimit is sufficient for the approval - Confirm the token contract supports the standard ERC-20 approve interface - For fee-on-transfer tokens, verify the spender contract handles them correctly API issues Problem : 429 Rate Limit Exceeded Implement request caching for repeated queries on the same position:

## Original documentation files

- [`uni:content/liquidity/liquidity-provisioning-api/getting-started.mdx`](../defi_docs/73e5d2a1f9b2_y_liquidity-provisioning-api_getting-started.mdx.txt)
- [`uni:content/liquidity/liquidity-provisioning-api/integration-guide.mdx`](../defi_docs/924a171a560f_liquidity-provisioning-api_integration-guide.mdx.txt)
- [`uni:content/liquidity/uniswapx/filling/faq.mdx`](../defi_docs/3455ce2cab77_uni_content_liquidity_uniswapx_filling_faq.mdx.txt)
- [`uni:content/trading/swapping-api/amm-vs-uniswapx-routing.mdx`](../defi_docs/600df620ded0_trading_swapping-api_amm-vs-uniswapx-routing.mdx.txt)
- [`uni:content/trading/swapping-api/chained-actions-integration.mdx`](../defi_docs/54f2c9bc4a38_ing_swapping-api_chained-actions-integration.mdx.txt)
- [`uni:content/trading/swapping-api/chained-actions.mdx`](../defi_docs/c48613765062_content_trading_swapping-api_chained-actions.mdx.txt)
- [`uni:content/trading/swapping-api/concepts/no-permit2-workflow.mdx`](../defi_docs/86f8ddca9e4b_ng_swapping-api_concepts_no-permit2-workflow.mdx.txt)
- [`uni:content/trading/swapping-api/concepts/permit2.mdx`](../defi_docs/41bea6d14d01_ontent_trading_swapping-api_concepts_permit2.mdx.txt)
- [`uni:content/trading/swapping-api/getting-started.mdx`](../defi_docs/9dbe16772070_content_trading_swapping-api_getting-started.mdx.txt)
- [`uni:content/trading/swapping-api/integration-guide.mdx`](../defi_docs/027740f52914_ntent_trading_swapping-api_integration-guide.mdx.txt)
- [`uni:content/unichain/guides/deploy-a-superchain-erc20.mdx`](../defi_docs/e6e287fbf6d1_nt_unichain_guides_deploy-a-superchain-erc20.mdx.txt)
- [`uni:content/unichain/guides/routing-on-unichain.mdx`](../defi_docs/0dcf8a268a31__content_unichain_guides_routing-on-unichain.mdx.txt)
