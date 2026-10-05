# Human JLCDFM observation

Provenance: PO observation supplied in [Issue #51](https://github.com/ihsinoky/he-piantor-42/issues/51)
and the task instructions; recorded 2026-10-05. This is a textual observation
record, not an independently captured web report. The upload date and raw
screenshots were not supplied.

The PO manually uploaded the exact C4B4A qualification ZIP:
`USB-NPTH-DFM-TEST-ONLY-DO-NOT-ORDER-HUMAN-UPLOAD.zip`.
SHA-256: `11660b19f2b465bc5ec5d1b0566b1e486077677cbba032f2c1c9a326b09cd16a`.
This matches the historical [upload manifest](../c4b4a-evidence/upload-manifest.json).
Process context: standard rigid 2-layer FR-4, 1 oz outer copper,
1.2 mm finished thickness.

The upload parsed and rendered successfully. Separate PTH and NPTH drill files
were present; the viewer displayed both under **Plated drill layers**.
No explicit measured NPTH-edge-to-adjacent-SMD-pad-copper result was exposed
for the four accepted nominal relationships (0.2000999900 / 0.2348831648 mm).

**Disposition: INCONCLUSIVE for the exact NPTH-to-pad-copper measurement.**
This observation establishes neither that JLCDFM checks nor that it does not
check the exact relationship internally. Absence of a web warning is not
production approval. The layer label alone does not establish factory PTH
interpretation; see the [supplier response](jlcpcb-support-response.md).

The agent did not log in, upload, contact JLCPCB or place an order.
