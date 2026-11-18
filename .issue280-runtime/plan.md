# Issue #280 - Unifying compatibility feasibility study (spec consolidation)

STUDY ONLY. No implementation, no board changes.
Deliverable: .issue280-runtime/unifying-spec.md + unifying-spec.json

## Sources to read (primary: code/docs in the repos themselves)
1. LOGITacker (RoganDawes/LOGITacker or maintained fork - confirm canonical)
   - pairing implementation, frame formats, crypto, HID++ handling (device side)
2. Bastille MouseJack (BastilleResearch/mousejack + research notes)
   - nRF24 ESB framing, channel/address handling
3. Solaar (pwr-Solaar/Solaar)
   - receiver pairing flow, HID++ 1.0/2.0 from the host side, docs/
4. logiops / Solaar-mirrored HID++ documentation where relevant

## Questions
Q1 RF layer: ESB params pairing vs normal (rate, address len/derivation,
   channel/hopping, payload len, ACK/retx)
Q2 Pairing state machine: frame sequence, AES-128 key origin/transfer,
   device persistence (address/key/counters), re-pair / receiver reset
Q3 Crypto: AES-128 mode + framing for HID reports (counter/nonce, which
   bytes encrypted, integrity), per LOGITacker device-side code
Q4 Normal operation: over-air keyboard HID frame vs USB HID report,
   keep-alive expectations, minimum HID++ exchanges + non-answer behaviour
Q5 Generation differences (C-U0008 era vs later), each with evidence source
Q6 Open items: what sources do not settle; needs capture vs real receiver

## Method
- Clone each repo shallow into .issue280-runtime/sources/ and read code.
- Every claim in unifying-spec.md cites repo + file/section.
- Blog vs code disagreement: code governs, disagreement noted.
- Checkpoint-commit after each source block.
