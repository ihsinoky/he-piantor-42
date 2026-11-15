**Key observation.** The permutation is a pure reversal, so it needs no braiding. Right Wing: pin n sits at X = 35.125 − 1.25(n−1), so pin numbers fall toward the centre. Main: pin n sits at u = −8.125 + 1.25(n−1), so pin numbers rise with u. Whether the route needs a reversal depends on how the fan maps u to X. If the run keeps the X order and the fan maps u to X by a plain translation, the order is reversed. A reversal is the worst case for planar sorting, but it costs nothing in 3D if you use the third dimension deliberately. The mirrored pairing's 52 crossings against the correct pairing's 163–174 is consistent with this.

**1. Structure: use the concentric turns as a "nesting" device, with no sorting zone.**

The cheapest zero-contact reversal is a coaxial spiral. Each wire gets its own radius in the reserve loop, and the radius order is a monotone function of pin number.

- Concentric turns of different radii never intersect, provided they are coplanar, or are stacked with Z separation ≥ OD. Radius pitch ≥ 1.05 mm is enough.
- 14 radii × 1.05 mm = ~14.7 mm of radial build. That is a radial budget, not a vertical one. Check it against the central mass's plan footprint, which is likely larger than its height.
- Rule: the wire that enters the loop at the outermost lateral position, pin 1 on the right Wing, takes the outermost radius, or the innermost one, whichever the Main fan requires.
- Entry and exit then follow the same monotone order. Entry is a tangent run from the outlet row. Exit is a tangent run to the Main row. Reversing is free if the exit is on the opposite side of the loop from the entry, or if the spiral is traversed in the opposite sense. This is the standard "nested U-turn reverses order" trick: a 180° nested turn flips the lateral order of a ribbon.
- Practical rule: treat the bundle as a flat ribbon, 14 × 1.05 mm wide. Run it as a ribbon from outlet to loop with no crossings, because the order is preserved and the ribbon stays flat. Make one 180° fold, either a U-turn in plan or a flip about the ribbon axis, which reverses the order. Then fan to the Main inlets.
- The ribbon fold has a minimum bend radius of 5 mm on the innermost wire. Outer wires have larger radii, so their length grows by about π·Δr per half turn. With 14 wires the outermost is ~13.7 mm further out, adding ~43 mm per half turn. That is far over the 3–10 mm slack.

**Length caveat.** A wire-by-wire radius spread is unaffordable with a full half turn. Two mitigations:
- Spread the ribbon in Z rather than radially. 2 or 3 layers of 5–7 wires cut the radial spread to about 2–3 mm, so the extra length is about 6–9 mm per half turn.
- Pair this with a flip about the ribbon axis, a 180° twist over ~15–20 mm of run. This reverses order with no radial cost.

For a flat ribbon, a twist about its own axis reverses lateral order. The wires stay parallel and each wire's length differs only by about 0.5 mm. The twist needs the ribbon to be ~14.7 mm wide, rotating about its centreline. It needs a clear circle of ~15 mm diameter along the run, or a staged version: split into two 7-wire half-ribbons, each of which twists in a ~7.4 mm envelope.

**Recommended scheme.** The cheapest structure that meets the length budget is a ribbon that holds its lateral order from outlet to loop, a twist or fold placed in the vertical rise into the central mass, and the order then preserved through the concentric turns to the fan. Do the reversal exactly once, at one dedicated location.

**Vertical space.** 14 distinct levels × 1.05 mm = 14.7 mm. The central mass has about Z9–22.6, so about 13.6 mm. It is marginal and tight. The under-Wing channel is only Z2–7.35 (5.35 mm), which fits 5 levels at most. So do not use a unique level per wire. Use 2 levels × 7 wires, hex-packed, which is about 2.1 mm of height, and do the reversal as a twist in the central mass where room exists.

**2. Service slide and length.** The twist-then-nest option preserves both best, because the concentric turns keep their order and slide as one rigid body. Keep the reversal upstream of the loop, so the loop contents are a plain ordered set. This matters for the 30.2 mm slide: a twist inside the sliding part would shear. Place the twist in the fixed portion before the loop, and keep the slack outside it. Per-wire length stays within ~3 mm of the mean, assuming the radial spread is limited to 2–3 mm.

**3. Failure modes, and the cheapest decisive test.**

1. **Twist envelope.** The ribbon cannot rotate if the clear space is below ~15 mm. This is the most likely failure. Test first: a 2D check of the clearance circle at the planned twist station against fixed bodies. It needs no wire modelling.
2. **Bend radius at the fold or twist.** The edge wires in a twist see a helix. With a ~15 mm pitch per half turn and a ~7 mm radius, the curvature is about 1/(r(1+(r/p')²)) and is roughly satisfied at ≥5 mm. Check it analytically before CAD.
3. **Length overrun for outer wires.** Compute the per-wire length from centreline parameters before sweeping.
4. **Wrong assumed reversal.** Verify the reversal by a pure combinatorial test. Take the 14 outlet X positions and 14 Main u positions at the point where the ribbon enters the loop and leaves it, and count inversions. The inversion count must be 0 after the single reversal, not 91, and that count is cheap to compute. It is also the quickest way to confirm which stage reverses the order.
5. **Slide contact.** Simulate the 30.2 mm translation of the loop at 5 or 6 steps with the same audit.

**Cheapest decisive test overall.** Before sweeping any solids, run the inversion count on centreline waypoints, then a pairwise minimum-distance check of the centrelines with a threshold of 1.0 mm plus margin. Centreline distance is much faster than solid booleans and finds the same contacts. Run it per stage. The first stage with non-zero violations is where to add the twist.

I have not run any of this against your CAD data. The numbers above are estimates from the geometry you gave.



Changes    +0 -0
AI Credits 4.76 (22s)
Tokens     ↑ 29.2k (20.0k cached, 9.2k written) • ↓ 2.3k
Resume     copilot --resume=0ecb12e3-fcfb-49b3-a322-f8196c72dd87
