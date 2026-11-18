# Issue #287 — bench-proof purchase list (Japan)

Observed **2026-11-19** on the retailer pages named below, per the
availability-scan rule (exact SKU, dated observation; UNVERIFIED where
a page could not be read). PREP ONLY — nothing here is an order.
Product MCU is decided as **nRF52840** (D-052, PO 2026-11-19), so the
bench radio is the same silicon family as the product MCU (nRF52840
module class): the PCA10059 below is the right platform and
LOGITacker's documented target.

## Core list

### 1. Nordic PCA10059 (nRF52840 USB dongle) × 1 — LOGITacker host

| Channel | SKU | Stock (2026-11-19) | Price (JPY) | Basis |
|---|---|---|---|---|
| **Mouser Japan** | Mouser #949-NRF52840-DONGLE / Mfr #nRF52840-Dongle | **4,282 in stock**, ships immediately | **¥1,799** (unit price as displayed) | Product page read 2026-11-19 |
| DigiKey Japan | DigiKey #1490-1073-ND / Mfr #NRF52840-DONGLE | 901 in stock | ¥2,914 ex-tax / **¥3,205 incl. tax** | Product page read 2026-11-19 |
| Akizuki Denshi | — | PCA10059 **not listed** (site search 2026-11-19; they stock MDBT50Q module boards such as AE-NRF52840 instead — a different board, not a LOGITacker target) | — | Absence is search-based: UNVERIFIED |
| Switch Science | — | PCA10059 **not listed**; they stock Raytac MDBT50Q USB dongles (¥1,881 / ¥1,925 Type-C, tax incl., search results 2026-11-19) — different board/bootloader, **not** a documented LOGITacker target, do not substitute without a separate check | — | Search results 2026-11-19 |

Buy from Mouser JP (cheapest observed, deep stock). Shipping is
extra and confirmed only at checkout (TO VERIFY at order time).

### 2. Sacrificial Unifying receivers × 2

| Channel | Item | Price (JPY) | Basis |
|---|---|---|---|
| **Logicool official store (logicool.co.jp)** | USB Unifyingレシーバー (993-001142, RC24-UFPC2 family) | **¥1,320 tax incl.**, in stock; free shipping on orders ≥ ¥2,000 (so 2 units ship free) | Product page read 2026-11-19 |
| Yodobashi.com | RC24-UFPC2 | ¥1,210 (10% points back) | Search-result snippet, page crawled ~2026-09 — dated, re-check at order time |
| Yahoo Auctions (used) | Unifying receivers, various bundles | Recent closings **¥980–1,400, average ¥1,190** (Aucfan aggregation of Yahoo Auctions data; sample closings 2025-11-28 / 2025-12-08) | Market indication, not a live listing |
| Mercari (used) | Same | Listings exist; **UNVERIFIED** (listing pages not readable in this pass) | — |
| Amazon.co.jp | Same | **UNVERIFIED** (page returned 403 in this pass) | — |

### 3. Genuine Unifying keyboard (ground truth) × 1

Needed for open items 1, 3, 7, 10 (real-device discipline cannot be
captured from our emulator alone). **¥0 if borrowed.** A used
Unifying keyboard via Mercari/Yahoo Auctions is the fallback; price
UNVERIFIED in this pass. Any model is fine — it only has to be a real
Logitech Unifying keyboard.

### Core total

| Route | Total |
|---|---|
| PCA10059 (Mouser JP) + 2 × official-store receivers | ¥1,799 + ¥2,640 = **¥4,439** (+ Mouser shipping) |
| Same, receivers bought used at the ¥1,190 auction average | ≈ **¥4,179** (+ shipping) |

## Which receiver class(es) to buy — and how to tell them apart

The two classes (spec §5.1): **C-U0007** = Nordic-based, receiver
WPID 0x8802, firmware series 012.xxx (fwupd name **RQR12**);
**C-U0008** = TI-based, WPID 0x8808, firmware 024.xxx (**RQR24**).
Firmware enforcement differs by class/firmware (spec §5 items 2–4),
and open item 4 asks which enforcement set the *target* firmware
applies — so class identity matters, and the PO's target model is
not yet confirmed.

Telling them apart **when buying**:

1. **Casing model marking (the pre-purchase cue).** The model number
   `C-U0007` or `C-U0008` is printed on the receiver casing; Logitech's
   own receiver-identification guidance names "Model C-U0007 or
   C-U0008 and the Unifying logo" as the identifier. On marketplace
   listings, use the casing photos (zoom, or ask the seller) — the
   model line is on the casing, not the packaging.
2. **USB PID does NOT help.** Both classes enumerate as
   **046d:c52b** (Solaar `docs/usb-ids.txt`; Bastille advisory 11
   lists both classes under 046d:c52b). A `lsusb` screenshot proves
   "Unifying", never the class.
3. **Bundle era is only a probability cue.** C-U0007 shipped with
   earlier Unifying products, C-U0008 with later ones, so a receiver
   bundled with a recent keyboard is *likely* C-U0008 — treat as a
   hint, confirm by (1) or (4).
4. **Definitive check is post-purchase:** plug it in and read the
   firmware with Solaar (`solaar show`) or `fwupdmgr get-devices` —
   **RQR12 ⇒ C-U0007 (Nordic)**, **RQR24 ⇒ C-U0008 (TI)** (fwupd's
   Logitech HID++ plugin documentation names exactly this mapping).
   Record each receiver's firmware version before any test
   (verification-env.md already requires this).

**Recommendation: buy one of each class.** The product must
ultimately work against whatever receiver the user pairs it with,
and the enforcement differences in spec §5 (pairing-lock requirement,
plaintext-after-encrypted-pairing, keyboard-type blacklist) are
firmware-class properties: testing only one class leaves open item 4
half-answered and risks a second bench round later. At ≈¥1,300 per
receiver the second class is the cheapest insurance in the whole
list. Practical route: one **new official-store receiver** (current
production; class confirmed on arrival by cue 4 — expected to be the
later class by production era, but that expectation is TO VERIFY ON
ARRIVAL, not a fact) plus one **used receiver whose casing photo
shows the other model number**. If both turn out to be the same
class, source the missing class used (≈¥980–1,400) before starting
the item-4 matrix.

## Optional items (not in the core total)

| Item | Why | Price |
|---|---|---|
| 2nd PCA10059 | One dongle sniffs while the other emulates (items 2 and 8 end-to-end form); convenience, not a blocker | ¥1,799 (Mouser JP, observed 2026-11-19, same listing as core #1) |
| Crazyradio 2.0 (Bitcraze, via Seeed) | Second capture radio on a different stack. **Not** a LOGITacker target out of the box; the original Crazyradio PA is discontinued with Bitcraze stock exhausted (do not buy scalped units) | $40.00 at Seeed (listing updated 2026-11-11, per #280 crawl); JPY price UNVERIFIED |
| Used genuine Unifying keyboard | Only if borrowing (core #3) is impossible | UNVERIFIED (Mercari/Yahoo Auctions channels) |

Host tooling is all free: Solaar, Logitech Unifying Software /
Options+, Wireshark (see poc-procedure.md).
