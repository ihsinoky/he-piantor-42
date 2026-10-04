# PO handoff — USB NPTH DFM coupon

**QUALIFICATION ONLY — DO NOT ORDER.** No external DFM result or support approval
exists yet. USB manufacturing disposition remains unresolved; evaluate the
captured result separately in C4B4B. A green screen alone is not a disposition.

Upload **only** this provided DFM ZIP:

```text
/workspaces/he-piantor-42/hardware/jitx/designs/c4b4a/USB-NPTH-DFM-TEST-ONLY-DO-NOT-ORDER-HUMAN-UPLOAD.zip
```

SHA-256:
`11660b19f2b465bc5ec5d1b0566b1e486077677cbba032f2c1c9a326b09cd16a`

The ZIP contains nine layer Gerbers and separate PTH/NPTH Excellon files.
Do not upload the surrounding folder, KiCad CAD/project files or Gerber Job.
Their known incorrect 1.6 mm overall-thickness metadata is not an order spec.
The ZIP is ignored locally; the committed [manifest](upload-manifest.json)
records each member's hash. If this ZIP is absent, regenerate using the report
and use the new recorded hash; generated timestamps change bytes between runs.

1. Manually upload only the ZIP above to JLCPCB's PCB DFM workflow.
2. Use a **standard rigid, two-layer FR-4** interpretation, **1 oz outer copper**.
   Select/confirm **1.2 mm finished thickness** if thickness is requested. Verify
   a 40 x 25 mm outline, two copper layers and two 0.60 mm NPTH locator holes.
3. Run **PCB DFM Check**. Switch the DFM UI to **metric (mm)** if needed.
4. Inspect **NPTH-to-copper / NPTH-to-track / hole-clearance** findings. The names
   of the service's checks may vary; inspect every finding involving the USB
   locator holes and adjacent copper, including the detailed result views.
5. Capture the checklist below and retain the raw result/report if available.
   **Do not place an order.** Do not infer production acceptance from green or
   absent alerts; use the prepared question below if green or inconclusive.

Screenshot/result checklist:

- Upload filename and process settings, including thickness if requested.
- Overall DFM result and the complete finding list (including green/no findings).
- Detailed result view for **every** USB NPTH/adjacent-copper finding: highlighted
  hole and copper, rule/category, **JLCPCB-measured value in mm**, and **alert level**
  (including green/informational/warning/error as presented).
- Coverage of both locator holes and all four relationships below. If the service
  groups findings, capture each relevant detail; if no finding exists, capture
  the inspected region and explicitly record that no value/alert was shown.
- Check date, ZIP SHA-256, exported DFM result/report when available, and any
  support reply received later. Do not claim a reply that has not been received.

Expected source and generated nominal gaps, NPTH edge to copper edge:

| Contact | Gap (mm) | Gerber contact identity |
| --- | ---: | --- |
| A1_B12 | 0.2000999900 | J1 contacts0 |
| A12_B1 | 0.2000999900 | J1 contacts11 |
| A4_B9 | 0.2348831648 | J1 contacts1 |
| A9_B4 | 0.2348831648 | J1 contacts10 |

The holes are 0.60 mm diameter, centered at x = -2.89 / +2.89 mm, y = 0
in connector coordinates. Each of these four lands is 0.60 x 1.14 mm,
centered at x = -3.20 / +3.20 / -2.40 / +2.40 mm, y = 1.07 mm respectively.
The coupon is translated as a whole; those local relationships are unchanged.

## Copy-paste support question (PO sends manually if green or inconclusive)

> I have a qualification-only 40 x 25 mm Gerber/Excellon coupon containing an
> unchanged HRO TYPE-C-31-M-12 connector landpattern. It has two 0.60 mm NPTH
> locator holes at x = ±2.89 mm, y = 0 in connector coordinates. Adjacent
> rectangular copper lands are 0.60 x 1.14 mm, centered at x = ±3.20 mm and
> ±2.40 mm, y = 1.07 mm. The generated Gerber/Excellon geometry gives
> NPTH-edge-to-copper-edge clearances of 0.2000999900 mm for A1_B12/A12_B1
> and 0.2348831648 mm for A4_B9/A9_B4. Is approximately 0.2001 mm clearance
> acceptable for normal production on standard rigid two-layer FR-4 with
> 1 oz outer copper and 1.2 mm finished board thickness, without any special
> process or manual CAM modification? If the DFM check is green or does not
> report a measured clearance, does it check this exact NPTH-to-pad-copper
> relationship, and what production limitation, tolerance or approval applies?
> This is an inquiry about qualification only; please do not place an order or
> modify the supplied geometry.
