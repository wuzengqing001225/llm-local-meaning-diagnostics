# Source card: FeeTier2

Corpus: synthetic
Source term ID: `v1:desk:FeeTier2`

## Source glossary entry

the second volume-based fee level that reduces taker fees

## Recorded source usage contexts

1. Once BTC-PERP notional cleared 50M this month, our account rolled into FeeTier2 and taker costs on the desk dropped noticeably.
2. Ops: can we confirm the sub-account 1182 actually hit FeeTier2 before we route the next batch of aggressive ETH orders through it?
3. Desk chat 03/14: 'nice, our maker rebate stayed flat but FeeTier2 finally kicked in so the taker leg on that unwind got cheaper.'
4. Risk note: reclassifying the volume calc changed the threshold date, so we now hit FeeTier2 two days earlier than projected.
5. Q1 report: aggregate volume across venues pushed the flagship fund past the FeeTier2 cutoff, saving roughly 40bps on taker fills for the quarter.
6. Jamie flagged that the exchange recalculated rolling 30-day volume and bumped us down out of FeeTier2 right before the OI-heavy expiry.
7. Log entry 22:41 - taker slippage model updated to reflect FeeTier2 pricing after the volume reset at midnight UTC.
8. Someone should check whether the market-making bot's fill costs assume FeeTier2 or the base tier, because the PnL attribution looks off.
9. Why did the cost basis on Friday's liquidation sweep not reflect FeeTier2 even though we crossed the volume threshold on Tuesday?
10. Compliance memo: fee schedule attached shows the account sitting in FeeTier2 as of the September statement, consistent with the trailing volume report.
