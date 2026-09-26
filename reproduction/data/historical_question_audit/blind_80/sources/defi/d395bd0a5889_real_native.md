# Source card: native

Corpus: defi
Source term ID: `real:native`

## Source glossary entry

(no source glossary entry)

## Recorded source usage contexts

1. Supported networks - Unichain Mainnet - Unichain Sepolia Testnet Allbridge Allbridge Core enables the transfer of value between blockchains by offering cross-chain swaps of native stablecoins.
2. Arbitrum, Avalanche, Base, BNB Smart Chain, Robinhood Chain, Tempo, Unichain - UniswapX minimum : 300 USDC equivalent on all supported chains - Native token swaps :
3. Available plugins Plugin Description --- --- uniswap-trading Integrate swaps via the Uniswap API, Universal Router SDK, or direct contract calls. uniswap-hooks Security-first guidance for building Uniswap v4 hooks. uniswap-viem EVM integration with viem and wagmi. uniswap-driver Token discovery and swap/liquidity planning with deep links. uniswap-cca Configure and deploy CCA contracts for token distribution. uniswap-trading-tools Automated trading strategies (DCA, index/basket, and copy-trade) for crypto-native tokens and tokenized real-world assets.
4. As part of the Superchain, Unichain supports native interoperability and cross-chain liquidity access.
5. For the required filler handling and contract details, see the Native ETH Input FAQ.
6. This enables native ETH input support for UniswapX via ERC20-ETH (EIP-7914) on supported wallets and chains.
7. Note, to quote the native token via UniswapX you must set the x-erc20eth-enabled header in your quote request to true .
8. Transfer From Native - OpenZeppelin ERC20ETH audit - UniswapX protocol repository Fade Mechanics What counts as a fade?
9. To use native ETH in UniswapX, set x-erc20eth-enabled to true on the /quote request.
10. Special-case this address in routing logic and treat the input as native ETH.
11. Native ETH cannot grant a standard ERC-20 allowance, so native ETH input historically required wrapping ETH to WETH before the trade.
12. If false , unwraps WETH to native ETH in the withdrawal.
13. Provide one token amount; the API computes the other. > Native ETH :
14. It relies on actual native ETH balances, and balanceOf intentionally reverts to prevent double-entry-point balance-check bugs.
15. The wallet grants a one-time native ETH allowance to ERC20ETH , which can be bundled into the initial EIP-7702 delegation.
16. Use 0x0000000000000000000000000000000000000000 for native ETH token addresses.

## Original documentation files

- [`uni:content/liquidity/liquidity-provisioning-api/integration-guide.mdx`](../defi_docs/924a171a560f_liquidity-provisioning-api_integration-guide.mdx.txt)
- [`uni:content/liquidity/uniswapx/filling/faq.mdx`](../defi_docs/3455ce2cab77_uni_content_liquidity_uniswapx_filling_faq.mdx.txt)
- [`uni:content/liquidity/uniswapx/filling/overview.mdx`](../defi_docs/a237b1143fe4__content_liquidity_uniswapx_filling_overview.mdx.txt)
- [`uni:content/protocols/v4/concepts/architecture.mdx`](../defi_docs/3524cee55370_i_content_protocols_v4_concepts_architecture.mdx.txt)
- [`uni:content/trading/overview.mdx`](../defi_docs/7be721288fc9_uni_content_trading_overview.mdx.txt)
- [`uni:content/trading/swapping-api/faqs.mdx`](../defi_docs/77c0dd102dba_uni_content_trading_swapping-api_faqs.mdx.txt)
- [`uni:content/trading/swapping-api/integration-guide.mdx`](../defi_docs/027740f52914_ntent_trading_swapping-api_integration-guide.mdx.txt)
- [`uni:content/trading/swapping-api/supported-chains.mdx`](../defi_docs/619120f7e7cb_ontent_trading_swapping-api_supported-chains.mdx.txt)
- [`uni:content/unichain/guides/create-a-pool.mdx`](../defi_docs/a810bb6dc358_uni_content_unichain_guides_create-a-pool.mdx.txt)
- [`uni:content/unichain/index.mdx`](../defi_docs/322e703a54b0_uni_content_unichain_index.mdx.txt)
- [`uni:content/unichain/tools/bridges.mdx`](../defi_docs/99faa22e2425_uni_content_unichain_tools_bridges.mdx.txt)
- [`uni:content/uniswap-ai/overview.mdx`](../defi_docs/ebc54f4012f9_uni_content_uniswap-ai_overview.mdx.txt)
