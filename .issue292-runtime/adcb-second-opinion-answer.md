# ADC_B routing proposal

Connect U1.46 to the existing ADC_B In2.Cu stub at **(85.50, 121.00)**. Use **F.Cu → In2.Cu → B.Cu → In2.Cu**, three **0.60 mm diameter / 0.30 mm drill through-vias**, and two local F.Cu doglegs. The route requires zero component moves and fits the brief’s copper clearances. KiCad sign-off also requires the module clearance exception on In2.Cu and a **0.20 mm local drill-to-copper allowance**.

The three via sites are in the open band north of the fine pad rows, inside the module field. Moving BTN west opens V1. In2.Cu passes between ADC_A and the HALL_PWR_EN and VBAT_SENSE stitches. The PAD_DR dogleg opens V2, where B.Cu can cross the inner-layer barriers. V3 returns to In2.Cu before the trackpad circle.

## ADC_B waypoints

Coordinates are absolute board millimetres on the 0.05 mm grid. Join consecutive points within each row with straight segments. Use **0.10 mm width** throughout ADC_B.

| Layer | Ordered waypoints (x, y) | Minimum trace-to-copper clearance |
|---|---|---|
| F.Cu | **U1.46** (73.15, 121.15) → (73.15, 120.65) → (73.05, 120.55) → **V1** (73.05, 120.15) | 0.200 mm to BTN |
| In2.Cu | **V1** (73.05, 120.15) → (73.90, 120.60) → (74.20, 120.60) → (74.45, 120.35) → (74.55, 120.10) → (74.75, 119.95) → (75.00, 119.90) → (75.75, 120.25) → **V2** (75.90, 120.30) | 0.0911 mm to SYS_3V3, 0.0919 mm to the HALL_PWR_EN via, and 0.0950 mm to the VBAT_SENSE via, all inside the module field |
| B.Cu | **V2** (75.90, 120.30) → (76.60, 120.80) → (77.90, 120.60) → (78.35, 120.15) → (78.70, 120.10) → **V3** (79.55, 120.55) | 0.1004 mm to the SYS_3V3 via at (76.725, 120.325) |
| In2.Cu | **V3** (79.55, 120.55) → (85.20, 120.85) → **existing ADC_B** (85.50, 121.00) | 0.1077 mm to ADC_A |

The final waypoint joins the west end of the existing In2.Cu segment from (85.50, 121.00) to (85.55, 121.05), which is already in the CFB.1/RFB.2 component. Refill the In1.Cu GND plane to form antipads around the three barrels.

## F.Cu doglegs

- **BTN.** Replace the straight segment at x = 72.85 from y = 119.35 to 121.75. Retain the 0.05 mm width and original centerline from (72.85, 119.35) to (72.85, 119.45) and from (72.85, 120.85) to (72.85, 121.75). Between those stubs use this **0.10 mm** dogleg: (72.85, 119.45) → (72.60, 119.70) → (72.60, 120.60) → (72.85, 120.85). This preserves both original endpoints, including the stitch at (72.85, 119.35). The dogleg clears U1.46 by 0.0914 mm and V1 by 0.1000 mm. The retained lower stub has its original 0.075 mm gap to U1.46. U1.47 and SW1.1 stay connected.
- **PAD_DR.** Replace the straight segment at x = 76.10 from y = 119.45 to 121.40. Use **0.10 mm** width between the original endpoints: (76.10, 119.45) → (76.30, 120.25) → (76.30, 120.70) → (76.10, 120.90) → (76.10, 121.40). The first endpoint joins the existing jog to the PAD_DR via at (76.00, 119.35). Minimum clearance is **0.0500 mm** to V2 and **0.0500 mm** to U1.36, both inside the module field. The closest gap to the SYS_3V3 stitch is 0.0750 mm. U1.50 and JPAD.5 stay connected.

## Via and keep-out clearances

Annulus and drill gaps are edge to edge and measured to other nets.

| Via | F.Cu | In2.Cu | B.Cu | Closest drill-to-drill gap |
|---|---:|---:|---:|---:|
| V1 (73.05, 120.15) | 0.1000 mm to BTN dogleg | 0.2245 mm to BTN via | 0.2245 mm to BTN via | 0.5246 mm |
| V2 (75.90, 120.30) | 0.0500 mm to PAD_DR dogleg | 0.1500 mm to ADC_A | 0.1500 mm to RESET_N | 0.5254 mm |
| V3 (79.55, 120.55) | 0.1250 mm to PAD_SDA | 0.1500 mm to ADC_A | 0.3754 mm to MUX_A2 via | 0.6753 mm |

The closest ADC_B copper to Edge.Cuts is **2.375 mm** on the first F.Cu leg. The closest new 0.10 mm dogleg copper is **2.174 mm** from Edge.Cuts. V3’s outer annulus clears the trackpad circle by **0.309 mm** and the B.Cu trace clears it by **0.559 mm**. The copper clears the antenna and mounting-hole reservations. The route uses the module exception within (69.30, 119.05)–(80.90, 128.90).

## KiCad rule check

The working project lists **0.20 mm Default netclass clearance**, and the board’s MODULE_FIELD_FINE rule area covers F.Cu. The project also has a **0.25 mm drill-to-copper minimum**. The tightest drill-to-copper gap in the proposal is **0.2000 mm** from V2’s drill to the PAD_DR dogleg. The HALL_PWR_EN and VBAT_SENSE passes also come within 0.25 mm of the drills. Confirm that the fabricator accepts 0.20 mm drill-to-copper inside the module field before applying this route.

In the scratch DRC I set the Default clearance to 0.10 mm per the brief, enabled MODULE_FIELD_FINE on F.Cu, In2.Cu and B.Cu, and applied the following overrides. The drill-to-drill minimum stayed at 0.25 mm.

```scheme
(rule "Module fanout copper clearance"
  (condition "A.insideArea('MODULE_FIELD_FINE') && B.insideArea('MODULE_FIELD_FINE')")
  (constraint clearance (min 0.05mm)))
(rule "Module fanout drill to copper"
  (condition "A.insideArea('MODULE_FIELD_FINE') && B.insideArea('MODULE_FIELD_FINE')")
  (constraint hole_clearance (min 0.20mm)))
```

I checked continuous track and via geometry, then refilled and ran KiCad 9.0.9 DRC on a scratch baseline and candidate using the same rules. ADC_B went from one open to zero. The candidate had zero DRC markers referencing the proposed copper. Unrelated board-wide DRC findings remain. An independent copper connectivity check confirmed BTN and PAD_DR each still had one connected component. The scratch baseline used board SHA-256 `3c40dd0187d5c70e77779af645ad0cf4ebbe202e9b3c0542657d8fae475e1b88`. The working board was left untouched by this review.
