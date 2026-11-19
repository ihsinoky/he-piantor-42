# LED_DRV reconnection

Route from the existing LED_DRV via at **(70.50, 118.00)** on **B.Cu**, add one **0.60 mm pad / 0.30 mm drill through-via at (73.20, 117.10)**, and finish on **In2.Cu** at the existing load-side stub at **(73.75, 115.85)**. Use 0.10 mm track width throughout. The connection requires zero component moves and zero changes to existing stitches, including the MUX_A0 bridge.

```mermaid
flowchart LR
    A["U1.56 · existing via<br/>(70.50, 118.00)"]
    V["New through-via<br/>(73.20, 117.10)"]
    B["Load-side stub · RLED.1<br/>(73.75, 115.85)"]
    A -->|"B.Cu · four segments"| V
    V -->|"In2.Cu · two segments"| B
```

## Waypoints and clearances

All coordinates are in board millimetres on the 0.05 mm grid. Each row is one straight segment. Clearances are copper edge to copper edge, including the round track ends and excluding the new via, which is checked separately.

| Layer | From (x, y) | To (x, y) | Minimum clearance to other copper | Limiting item |
|---|---|---|---:|---|
| B.Cu | (70.50, 118.00) | (71.05, 117.45) | 0.371 mm | MUX_A0 via at (71.55, 116.93037) |
| B.Cu | (71.05, 117.45) | (72.10, 117.45) | 0.169 mm | Same MUX_A0 via |
| B.Cu | (72.10, 117.45) | (72.45, 117.10) | 0.180 mm | USB_DM via at (72.70, 117.60) |
| B.Cu | (72.45, 117.10) | (73.20, 117.10) | 0.149 mm | Same USB_DM via |
| In2.Cu | (73.20, 117.10) | (73.20, 116.40) | 0.357 mm | Same USB_DM via |
| In2.Cu | (73.20, 116.40) | (73.75, 115.85) | 0.554 mm | MUX_A0 via at (73.50, 114.98037) |

The B.Cu path passes on the larger-y side of the MUX_A0 via, then on the smaller-y side of the USB_DM via. It returns to In2.Cu on the load side of the braid. The last waypoint is the centerline end of the existing 0.10 mm LED_DRV stub from (73.75, 115.25) to (73.75, 115.85). The added copper uses 0.10 mm clearance throughout, including inside the FH12 fanout.

At the **(73.20, 117.10)** through-via, the minimum annulus clearance on F.Cu, In2.Cu and B.Cu is **0.1069 mm**, to the USB_DM via at (72.70, 117.60). The center spacing is 0.7071 mm, giving 0.4071 mm drill-edge separation for the two 0.30 mm holes. The annulus also clears the F.Cu J2 mounting pad by **0.1127 mm** and the MUX_A1 via at (73.925, 117.175) by **0.1287 mm**. Use the exact via coordinate. Refill the In1.Cu GND plane to form its antipad. The layer change uses the through-via barrel, with no signal trace on In1.Cu or F.Cu.

The minimum new copper setback from Edge.Cuts is **1.655 mm** on the first B.Cu segment. The new via annulus is **4.193 mm** from Edge.Cuts. All added copper clears the antenna and hole reservations. The new outer-layer copper clears the specified trackpad circle by more than **6.51 mm**, measured from the annulus.

## Verification

I checked continuous segment and via geometry against the board pads, tracks, vias and outline. I then applied the six segments and one via to a scratch copy, refilled the zones, and ran KiCad 9.0.9 DRC. The baseline had one LED_DRV unconnected item. The candidate had zero and no DRC markers referencing the seven new items under a 0.10 mm default clearance test. Other board DRC findings are open.

The checked board snapshot had SHA-256 `7fa3866e03df3ee80d27c9c2448a4381c7f4be3db776a629e2b400e1bfa45016`. The working project's Default netclass lists 0.20 mm clearance and track width, so the reported rule check used the brief's 0.10 mm values in the scratch project. The board file was left untouched.
