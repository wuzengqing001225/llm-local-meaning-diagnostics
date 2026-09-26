# Source card: AutoRoll

Corpus: synthetic
Source term ID: `v1:desk:AutoRoll`

## Source glossary entry

the automatic transfer of a hedge into the next contract before expiry

## Recorded source usage contexts

1. AutoRoll kicked in on the BTC front-month at 03:58 UTC, so the delta book carried straight through expiry without a manual re-strike.
2. Desk note 4/11: ETH position was flat into settlement because AutoRoll fired two hours early on Kevin's book.
3. Can someone check why AutoRoll didn't trigger on the SOL contract last night — we ended up naked for 40 minutes into expiry.
4. Priya flagged that AutoRoll on the March/June switch left a 120 BTC basis mismatch we need to true up by Friday.
5. Risk log 09/14: AutoRoll threshold was bumped from T-6h to T-12h after the OI drop spooked the algo into an early move.
6. If AutoRoll misfires again on the XBT quarterly, we're looking at another manual scramble like last September.
7. Chat - Marcus: AutoRoll just moved the whole hedge off the Dec contract, PnL should reconcile clean tomorrow.
8. The postmortem blamed a stale funding feed for AutoRoll executing against the wrong next-quarter symbol.
9. Note to ops: disable AutoRoll on the illiquid ADA perp until the June contract has enough depth to absorb the size.
10. Weekly report: AutoRoll accounted for 3 of the 5 contract transitions this cycle, the other two required manual intervention.
