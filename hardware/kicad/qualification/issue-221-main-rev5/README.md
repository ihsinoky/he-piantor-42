# Main Rev.5 — Issue #221 source verification hold

Status: **HOLD — Fly Daughterboard pin-number-to-net mapping unconfirmed.**

This directory contains research and an independently extracted Rev.4 input
contract. It does **not** contain an accepted Rev.5 PCB or manufacturing package.
Do not use the Rev.4 manufacturing ZIP as a Rev.5 substitute.

- Requirements: [Issue #221](https://github.com/ihsinoky/he-piantor-42/issues/221).
- Detailed result and acceptance checklist: [report](../../../../docs/issue-221-main-rev5.md).
- Source findings: [sources.json](sources.json).
- Reproducible native PCB/XML/BOM input inspection: [inspect-input.py](inspect-input.py).
- Inspection result: [input-contract.json](input-contract.json).
- Decision proposal: [D-035](../../../../docs/decisions.md#d-035---main-rev5-fly-daughterboard-connector-proposal).

The runtime instruction requires unverified Fly pin correspondence to be
reported as unconfirmed for PMO judgment. Connector identity, cable compatibility
marketing and wire colours alone do not establish the four numbered USB nets.
All implementation and manufacturing acceptance checks remain pending.
