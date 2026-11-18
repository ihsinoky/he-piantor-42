# Issue #287 preparation — work plan

Goal: everything ready before bench-proof hardware exists. PREP ONLY —
no purchases. Basis: `.issue280-runtime/unifying-spec.md` (§5
generations, §6 ten open items) and `verification-env.md` (shopping
list + open-item mapping, prices there are 2026-11-18 search
indications, NOT observations — this task replaces them with dated
observations).

## Steps

1. **plan.md** (this file) — commit.
2. **purchase-list.md / .json**
   - PCA10059: check Mouser JP, DigiKey JP, Akizuki, Switch Science
     product pages directly; record stock + JPY price + observation
     date; UNVERIFIED where a page cannot be read.
   - Sacrificial Unifying receivers: channels for a JP buyer (Amazon
     JP, Mercari, Yahoo Auctions, Logitech spare parts), typical
     observed prices.
   - Receiver-class identification (C-U0007 Nordic/WPID 0x8802/fw
     012.xxx vs C-U0008 TI/WPID 0x8808/fw 024.xxx): casing model
     marking, shared USB PID 046d:c52b (does NOT distinguish),
     post-purchase confirmation via Solaar firmware/WPID readout.
     Cues must trace to #280 files or Solaar/Logitech docs.
   - Recommendation: which class(es) to buy, with reasoning.
   - Optional items (2nd PCA10059, Crazyradio 2.0, genuine keyboard)
     priced separately; core total in JPY.
   - Commit.
3. **poc-procedure.md**
   - LOGITacker build/flash on PCA10059 from the upstream repo docs
     (exact repo, build commands, dongle bootloader flashing method).
   - Host setup: Solaar, Wireshark + LOGITacker dissectors.
   - Pairing run + key-send test sequence.
   - Test matrix: each of spec §6 items 1–10 → concrete step + pass
     observation (start from verification-env.md mapping, make each
     step executable).
   - Safety/scope notes: own receivers only; end state of sacrificial
     receivers.
   - Steps not verifiable without hardware marked TO VERIFY ON
     ARRIVAL.
   - Commit.

## Rules

- Prices/stock: observed on the retailer page today (2026-11-19),
  dated; UNVERIFIED rather than estimated.
- No purchases, no orders, no cart actions.
