# Source card: swapping

Corpus: defi
Source term ID: `real:swapping`

## Source glossary entry

Uniswap Labs maintains a list of "unsupported" tokens, for which swapping is not permitted through any method due to legal or regulatory restrictions, at https://unsupportedtokens.uniswap.org/.

## Recorded source usage contexts

1. We recommend that end users always do their own due diligence before swapping any tokens.
2. The logic executes before and/or after major operations such as pool creation, liquidity addition and removal, swapping, and donations.
3. Swapping through multiple pools no longer requires transferring tokens for intermediate pools.
4. If the UniswapX quote is better, the user is shown a purple lightning bolt , indicating that they will be swapping through X.
5. Supported Chains for Swapping The following chains are supported for swapping.
6. Uniswap Labs maintains a list of "unsupported" tokens, for which swapping is not permitted through any method due to legal or regulatory restrictions, at https://unsupportedtokens.uniswap.org/.
7. New tokens may not be immediately swappable as it is dependent on there being sufficient liquidity in a pool for swapping to take place.
8. The swapping wallet (your user) signs the transaction and you broadcast it 4.
9. Prompt the swapping wallet to sign the Permit2 message The swapping wallet signs the message, resulting in an EIP-712-style signature.
10. This guide is the operational counterpart to Swapping with Chained Actions.
11. Swapping Without Permit2 The Uniswap API supports an alternative swap flow that does not require Permit2 signatures.
12. Uniswap offers distinct methods for integrating swapping functionality into your application.
13. Swapping How can I simulate a swap before submitting it?
14. For conceptual background, see Swapping with Chained Actions.
15. Architecture Client-side responsibilities The Uniswap API swapping endpoints are a quote and transaction building service augmented with useful validation checks.
16. The swapping wallet (your user) signs the swap transaction and you broadcast it Enabling the Proxy Approval Flow The Uniswap API exposes a request header that disables Permit2 behavior: x-permit2-disabled When this header is included, the API switches to the proxy approval model.

## Original documentation files

- [`uni:content/liquidity/overview.mdx`](../defi_docs/a27e071a3373_uni_content_liquidity_overview.mdx.txt)
- [`uni:content/liquidity/uniswapx/concepts/auction-types.mdx`](../defi_docs/5c97155ade9a_nt_liquidity_uniswapx_concepts_auction-types.mdx.txt)
- [`uni:content/liquidity/uniswapx/filling/mainnet/become-a-quoter.mdx`](../defi_docs/f2603805b375_ity_uniswapx_filling_mainnet_become-a-quoter.mdx.txt)
- [`uni:content/liquidity/uniswapx/overview.mdx`](../defi_docs/a54d274b51b2_uni_content_liquidity_uniswapx_overview.mdx.txt)
- [`uni:content/protocols/v4/concepts/architecture.mdx`](../defi_docs/3524cee55370_i_content_protocols_v4_concepts_architecture.mdx.txt)
- [`uni:content/protocols/v4/guides/getting-started.mdx`](../defi_docs/4492cafd8457__content_protocols_v4_guides_getting-started.mdx.txt)
- [`uni:content/protocols/v4/overview.mdx`](../defi_docs/4702dcb71e25_uni_content_protocols_v4_overview.mdx.txt)
- [`uni:content/trading/overview.mdx`](../defi_docs/7be721288fc9_uni_content_trading_overview.mdx.txt)
- [`uni:content/trading/swapping-api/chained-actions-integration.mdx`](../defi_docs/54f2c9bc4a38_ing_swapping-api_chained-actions-integration.mdx.txt)
- [`uni:content/trading/swapping-api/concepts/no-permit2-workflow.mdx`](../defi_docs/86f8ddca9e4b_ng_swapping-api_concepts_no-permit2-workflow.mdx.txt)
- [`uni:content/trading/swapping-api/concepts/permit2.mdx`](../defi_docs/41bea6d14d01_ontent_trading_swapping-api_concepts_permit2.mdx.txt)
- [`uni:content/trading/swapping-api/concepts/swap-routing.mdx`](../defi_docs/4b120c091d8f_t_trading_swapping-api_concepts_swap-routing.mdx.txt)
- [`uni:content/trading/swapping-api/faqs.mdx`](../defi_docs/77c0dd102dba_uni_content_trading_swapping-api_faqs.mdx.txt)
- [`uni:content/trading/swapping-api/getting-started.mdx`](../defi_docs/9dbe16772070_content_trading_swapping-api_getting-started.mdx.txt)
- [`uni:content/trading/swapping-api/integration-guide.mdx`](../defi_docs/027740f52914_ntent_trading_swapping-api_integration-guide.mdx.txt)
- [`uni:content/trading/swapping-api/supported-chains.mdx`](../defi_docs/619120f7e7cb_ontent_trading_swapping-api_supported-chains.mdx.txt)
- [`uni:content/unichain/getting-started/setting-up-a-wallet.mdx`](../defi_docs/cae92978e69a_unichain_getting-started_setting-up-a-wallet.mdx.txt)
