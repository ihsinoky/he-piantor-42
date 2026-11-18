# Plan — AA/AAA battery sizing (Issue #280 follow-up)

PO decision (2026-11-18): battery = AA or AAA cells, user-replaceable.
No Li-ion pack, no in-device charging assumption.

## Basis numbers to pull (and their sources)
- [ ] Continuous Hall load (design): from hw-implications.md (c) study → verify vs docs/decisions.md (127 mA/Wing design load, 5.2 V rail, TPS63070-class buck-boost)
- [ ] DRV5055 ICC / tON: (c) study cites DRV5055 datasheet SBAS640 (ICC = 3 typ) — reuse with citation
- [ ] Burst scan: T=10 ms, 1 ms window → 10% Hall duty (idle); from (c) study
- [ ] Radio option sleep currents: (i) nRF24L01+ + RP2040, (ii-a) nRF52 co-processor — from (c) study (hw-implications.md)
- [ ] Keep-alive cost: from unifying-spec.md (keep-alive interval byte 0x08 announced in REQ1; exact units OPEN item — state assumption)
- [ ] Case geometry: plate 10.90, under-board void ~3.10 mm, central bay — from (c) study + case records
- [ ] TPS63070 input range + efficiency: manufacturer datasheet (TI) — pull actual VIN range
- [ ] Cell capacities: Panasonic eneloop (AA ~1900 mAh min, AAA ~750 mAh min) + named alkaline datasheet (Energizer E91/E92 class) at stated discharge rates — datasheet values only
- [ ] Cell dims: AA 14.5 dia x 50.5 mm, AAA 10.5 x 44.5 mm (given in brief)

## Method
1. Cell configurations 2/3/4 x AA/AAA x alkaline/NiMH: voltage fresh→EOD, Wh (series adds V not mAh), converter coverage check across full discharge curve at design load, efficiency assumption stated.
2. Runtime model: stated usage profile (awake bursts T=10ms/1ms window; active-typing hours/day at stated higher duty; radio keep-alive; MCU sleep floor per option). Derate capacity for drain. Sensitivity: which assumption moves the answer most.
3. Case consequence: placement candidates (south margin / central bay hump / external pod), deck-height & footprint cost, low-deck mandate survival.
4. Verdict vs targets: 1 day / 1 week (8h x 5d) / 1 month, per radio option. Does AA/AAA flip the (c) ranking (i) vs (ii-a)?

## Deliverable
`.issue280-runtime/aa-sizing.md` + `.json`
