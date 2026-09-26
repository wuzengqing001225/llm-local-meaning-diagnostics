# Source card: wallet

Corpus: defi
Source term ID: `real:wallet`

## Source glossary entry

The Uniswap Wallet is a self-custodial crypto wallet built for swapping.

## Recorded source usage contexts

1. Permit2 Flow Permit2 is a token approval system which uses an offchain (gasless) EIP-712 signed message to allow an onchain contract to spend tokens from a wallet within pre-defined bounds.
2. The swapper needs an EIP-7702 wallet with ERC-7914 support.
3. Create Wallet Hook Create useWallet.ts and copy the code below: 3.
4. Where to Go Next - Set up a wallet for testing - Fund your wallet on mainnet or Sepolia - Review network configuration values
5. Better handling of fee-on-transfer tokens Permit2 also avoids an extra token transfer that occurs in the no-Permit2 proxy flow. - In the standard Permit2 flow, tokens move directly from the wallet to the Universal Router in a single transfer. - In the proxy approval flow, tokens are first transferred from the wallet to the proxy contract, and then forwarded to the Universal Router.
6. Connect wallet - Click "Connect Wallet" - Approve Uniswap Wallet connection 3.
7. The swapping wallet (your user) signs the swap transaction and you broadcast it Enabling the Proxy Approval Flow The Uniswap API exposes a request header that disables Permit2 behavior: x-permit2-disabled When this header is included, the API switches to the proxy approval model.
8. Infura, Alchemy, or self-hosted) - Web3 Library : ethers.js, viem, or web3.js for transaction signing - Wallet Integration :
9. Create Wallet Interface Component Create WalletInterface.tsx and copy the code below: 4.
10. Once your wallet is connected, you can begin by clicking "Create a Subgraph".
11. The wallet grants a one-time native ETH allowance to ERC20ETH , which can be bundled into the initial EIP-7702 delegation.
12. Wallet approves proxy contract for token spend (token to proxy) 2. swap via proxy to Universal Router Why We Recommend Permit2 Over Proxy Approval Permit2 provides important security and usability advantages over the proxy approval workflow. 1.
13. Initialize Your Subgraph Create a subgraph in Subgraph Studio Go to the Subgraph Studio and connect your wallet.
14. Generation of validated transaction calldata, ready for signature by the user's wallet - Balance Checks :
15. Get extensive coverage across chains and third-party wallets with Dynamic's multichain wallet adapter.
16. Permit2 provides time- and (optionally) amount-limited access to a swapper’s wallet, protecting them from compromised routing contracts.

## Original documentation files

- [`uni:content/liquidity/liquidity-provisioning-api/integration-guide.mdx`](../defi_docs/924a171a560f_liquidity-provisioning-api_integration-guide.mdx.txt)
- [`uni:content/liquidity/uniswapx/filling/faq.mdx`](../defi_docs/3455ce2cab77_uni_content_liquidity_uniswapx_filling_faq.mdx.txt)
- [`uni:content/trading/overview.mdx`](../defi_docs/7be721288fc9_uni_content_trading_overview.mdx.txt)
- [`uni:content/trading/swapping-api/agent-attribution.mdx`](../defi_docs/8c21a458338f_ntent_trading_swapping-api_agent-attribution.mdx.txt)
- [`uni:content/trading/swapping-api/building-prerequisites.mdx`](../defi_docs/ad020834b1b9__trading_swapping-api_building-prerequisites.mdx.txt)
- [`uni:content/trading/swapping-api/chained-actions-integration.mdx`](../defi_docs/54f2c9bc4a38_ing_swapping-api_chained-actions-integration.mdx.txt)
- [`uni:content/trading/swapping-api/chained-actions.mdx`](../defi_docs/c48613765062_content_trading_swapping-api_chained-actions.mdx.txt)
- [`uni:content/trading/swapping-api/concepts/no-permit2-workflow.mdx`](../defi_docs/86f8ddca9e4b_ng_swapping-api_concepts_no-permit2-workflow.mdx.txt)
- [`uni:content/trading/swapping-api/concepts/permit2.mdx`](../defi_docs/41bea6d14d01_ontent_trading_swapping-api_concepts_permit2.mdx.txt)
- [`uni:content/trading/swapping-api/faqs.mdx`](../defi_docs/77c0dd102dba_uni_content_trading_swapping-api_faqs.mdx.txt)
- [`uni:content/trading/swapping-api/integration-guide.mdx`](../defi_docs/027740f52914_ntent_trading_swapping-api_integration-guide.mdx.txt)
- [`uni:content/trading/swapping-api/supported-chains.mdx`](../defi_docs/619120f7e7cb_ontent_trading_swapping-api_supported-chains.mdx.txt)
- [`uni:content/unichain/getting-started/get-funds-on-unichain.mdx`](../defi_docs/30e059d474f1_ichain_getting-started_get-funds-on-unichain.mdx.txt)
- [`uni:content/unichain/getting-started/set-up-a-node.mdx`](../defi_docs/b9f90f791676_ntent_unichain_getting-started_set-up-a-node.mdx.txt)
- [`uni:content/unichain/getting-started/setting-up-a-wallet.mdx`](../defi_docs/cae92978e69a_unichain_getting-started_setting-up-a-wallet.mdx.txt)
- [`uni:content/unichain/guides/deploy-a-contract-through-thirdweb.mdx`](../defi_docs/d2faf9def6c3_in_guides_deploy-a-contract-through-thirdweb.mdx.txt)
- [`uni:content/unichain/guides/subgraph-unichain.mdx`](../defi_docs/46cf2a018938_ni_content_unichain_guides_subgraph-unichain.mdx.txt)
- [`uni:content/unichain/guides/transfer-usdc.mdx`](../defi_docs/c0a1ed4d4c8c_uni_content_unichain_guides_transfer-usdc.mdx.txt)
- [`uni:content/unichain/technical-information/flashblocks.mdx`](../defi_docs/d1e8196fec20_t_unichain_technical-information_flashblocks.mdx.txt)
- [`uni:content/unichain/tools/account-abstraction.mdx`](../defi_docs/33b84434299e_i_content_unichain_tools_account-abstraction.mdx.txt)
