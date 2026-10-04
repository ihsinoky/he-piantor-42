// Non-authoritative Dashboard read model. See docs/governance.md.
window.PROJECT_STATUS = {
  schemaVersion: 1, updatedAt: "2026-10-04T06:29:03+00:00",
  currentWork: "C4A accepted / merged PR #42; C4B issue #43 BLOCKED (partial copper/ODB/CSV; full routing/DRC and qualified Gerber/drill open); C2 electrical PASS preserved; C4C next / Human Gate; G0A ready-for-decision / G0B not-ready / EVT-002 blocked-unstarted",
  evidence: {
    commit: { sha: "795479e", at: "2026-10-02T22:41:32+09:00", summary: "Implement native M1 four-key Hall evaluation circuit (#27)" },
    pullRequest: { state: "snapshot", label: "Historical snapshot; check GitHub for current PR state" },
    ci: { result: "UNKNOWN", at: null, lastSuccess: "Not recorded", detail: "GitHub Actions の結果はこの静的 snapshot に未同期" },
    artifacts: { state: "FROZEN", detail: "PR #27 permanent frozen four-key qualification fixture; not physical Rev.M1" }
  },
  milestones: [
    {id:"M0",name:"設計方針・基本形状",status:"done",deliverable:"過去の42キー要件・17 mm配置・取得方針（D-015でpitch再評価）",exit:"主要要件・キー中心座標・評価方針が文書化済み"},
    {id:"M1",name:"磁気方式・評価基板",status:"current",deliverable:"再利用Main + pitch/磁気Evaluation Wing(s)、計測FW、実測レポート（hardware未実装）",exit:"ERC/DRC合格、実測で磁気・pitch・analog pathをG2判断"},
    {id:"M2",name:"42キー Rev.A",status:"next",deliverable:"accepted Main再利用 + Left 21-key Wing + Right 21-key Wing + production FW（G2判断後）",exit:"Main/Wing ERC/DRC・製造性検査とFW buildが合格"},
    {id:"M3",name:"統合・筐体・試験",status:"todo",deliverable:"筐体、統合機、組立・校正・試験手順",exit:"実機操作、全キー校正、USB、Vial、筐体適合の試験に合格"},
    {id:"M4",name:"完成版リリース",status:"todo",deliverable:"再現可能なv1.0製造・FW・筐体パッケージ",exit:"最終成果物を固定しユーザーが完成版を承認"}
  ],
  streams: [
    {name:"Hardware",cells:["設計方針 完了","四キーfixture凍結 / C0-C2 accepted / C3 historical valid / C4A merged #42 / C4B BLOCKED / C4C next Human Gate / physical Main-Wing unimplemented / G0A ready-for-decision / G0B not-ready","Main再利用 + Left/Right Wings","統合改版","製造版"]},
    {name:"Firmware",cells:["要件 完了","計測FW","Hall + Vial","統合・校正","v1.0"]},
    {name:"Enclosure / Mechanical",cells:["形状条件 完了","PCB条件待ち","外形連携","STEP / STL","製造版"]},
    {name:"Verification / Test",cells:["計画 完了","磁気・電力実測","Rev.A bring-up","統合試験","受入試験"]}
  ],
  streamStates: [
    ["done","progress","todo","todo","todo"],
    ["done","progress","todo","todo","todo"],
    ["done","waiting","todo","todo","todo"],
    ["done","waiting","todo","todo","todo"]
  ],
  gates: [
    {name:"G0A JITX Backend Adoption",status:"ready-for-decision",check:"C0-C3 accepted evidence + C4B physical/manufacturing pipeline result",trigger:"C4B BLOCKED evidence complete for C4C decision; successful pipeline not proven",unlocks:"C4C GO/NO-GO: active EDA backend for physical Rev.M1"},
    {name:"G0B Rev.M1 Architecture / Interface Freeze",status:"not-ready",check:"Main/Wing architecture, logical interface, exact connector/pinout, experiment design, representative interconnect, pitch-test structure, Rev.A reuse, DFM, approved geometry source",trigger:"architecture/interface review package complete",unlocks:"Rev.M1 schematic/PCB through manufacturing-package completion"},
    {name:"G1 Rev.M1 Main + Evaluation Wing pre-order review",status:"not-ready",check:"Main/Wing circuit/ERC, DRC, BOM, actual manufacturing outputs, measurement plan",trigger:"manufacturing package complete after G0A/G0B",unlocks:"Rev.M1 Main + Evaluation Wing order"},
    {name:"G2 post-EVT-002 magnetic / pitch / analog-path decision",status:"not-ready",check:"range, noise, scan speed, power, interference, interconnect, 17.0/16.5/16.0 mm usability",trigger:"physical measurements/report complete",unlocks:"production pitch and magnetic architecture / Rev.A circuit freeze"},
    {name:"G3 Rev.A 発注前確認",status:"not-ready",check:"Main/Left/Right DRC, BOM, Gerber, drill/PnP, cost",trigger:"42-key manufacturing package complete",unlocks:"Rev.A PCBA order"},
    {name:"G4 実機操作確認",status:"not-ready",check:"打鍵、校正、Vial、USB、筐体適合",trigger:"統合機のbring-up完了時",unlocks:"完成版の固定"},
    {name:"G5 最終版承認",status:"not-ready",check:"v1.0の全製造物と手順",trigger:"受入試験合格時",unlocks:"v1.0リリース"}
  ],
  risks: [
    {kind:"risk",title:"pitch / キーキャップ干渉",detail:"17.0 / 16.5 / 16.0 mmで使用感・磁気・switch/keycap干渉を比較。100 x 100 mmはcost targetのみ。"},
    {kind:"risk",title:"磁束レンジと個体差",detail:"Main + Evaluation Wingでスイッチ・センサ・距離・interconnectを一組として実測する。"},
    {kind:"risk",title:"42センサの電力",detail:"USB 500 mA近辺の可能性があるため本基板前に電力Gateを通す。"},
    {kind:"risk",title:"中央部のねじり荷重",detail:"Main/Wingの接続・固定と筐体補強は後続mechanical gateで検証する。"},
    {kind:"risk",title:"JITX RuntimeDesign stability",detail:"EDA-002C0 is accepted PASS for the challenger/parity workflow. RuntimeDesign query and net-resolution methods remain documented but explicitly experimental; every future JITX Python package or runtime change must rerun the normalized exporter and bootstrap graph self-test before compatibility is assumed."},
    {kind:"risk",title:"M1 layout gated",detail:"PR #27 is the frozen historical qualification oracle under unchanged D-014. Physical Main/Wing is separate; C4B/C4C adoption and G0B interface freeze gate implementation."}
  ],
  tasks: [
    ["DSH-001","PM","専用HTMLダッシュボード","done","Codex","-"],
    ["DSH-002","PM","Project Health / Roadmap / Gate表示","done","Codex","DSH-001"],
    ["REQ-001","REQ","全体仕様書","progress","Codex","-"],
    ["REQ-002","REQ","通常高さ磁気スイッチ選定","progress","Codex","-"],
    ["REQ-003","REQ","17.0/16.5/16.0 mm評価用キーキャップ適合確認","progress","Codex","REQ-002"],
    ["REQ-004","REQ","Historical QMK/Piantor coordinate provenance/reference; not an input to future project-owned Rev.A geometry","done","Codex","historical reference only"],
    ["REQ-005","REQ","Rev.A Wing geometry source / license decision","hold","PMO + Human Gate","project-owned or explicitly approved source required before implementation"],
    ["REQ-006","REQ","project-owned or explicitly approved Left/Right Wing geometry definition","todo","Codex","REQ-005"],
    ["ELEC-001","ELEC","Hallセンサ選定","progress","Codex","REQ-002"],
    ["ELEC-002","ELEC","ADC / MUX方式決定","progress","Codex","ELEC-001"],
    ["ELEC-003","ELEC","MCU・USB-C・電源・ESD回路","progress","Codex","-"],
    ["ELEC-004","ELEC","通電LED回路","done","Codex","ELEC-003"],
    ["ELEC-005","ELEC","レイヤーRGB LED回路","todo","Codex","ELEC-003"],
    ["EDA-000","EDA","KiCad設計ルート（retired fallback / reference）","hold","Codex","retired"],
    ["EDA-001","EDA","2層 native stock tscircuit feasibility","done","Codex + CI","GO"],
    ["EDA-002A","EDA","Cloud Codex JITX capability probe（historical STOP）","hold","Human + Codex","Cloud Codex unsuitable"],
    ["EDA-002B","EDA","Codespaces JITX bootstrap + M1 parity contract","done","Copilot CLI + Codespaces","real bootstrap build PASS"],
    ["EDA-002C0","EDA","documented JITX graph export","done","Copilot CLI + Codespaces","accepted PASS; RuntimeDesign methods experimental"],
    ["EDA-002C1","EDA","JITX component modeling","done","Codex","9/9 PASS accepted; PR #36 merged; geometry differences preserved"],
    ["EDA-002C2","EDA","M1 JITX electrical parity","done","Codex","issue #37; done / accepted / merged PR #38; electrical PASS; geometry NOT established"],
    ["EDA-002C3","EDA","Historical manufacturer/frozen geometry evidence","done","PMO + Human","issue #39 / merged PR #40; evidence retained, not all questions resolved; convergence no longer adoption criterion"],
    ["EDA-002C4A","EDA","Evaluation / architecture rebaseline","done","Codex","issue #41; accepted / merged PR #42; no adoption decision"],
    ["EDA-002C4B","EDA","JITX board-level physical/manufacturing pipeline proof","hold","Codex","issue #43; investigation complete / BLOCKED; partial copper/ODB/CSV; full routing/DRC + Gerber/drill open; qualification only / no order"],
    ["EDA-002C4C","EDA","JITX adoption Human Gate","hold","PMO + Human","next / Human Gate; C0-C3 + C4B BLOCKED evidence; G0A ready-for-decision, no adoption decision"],
    ["EVT-001","EVT","historical 4-key native electrical qualification fixture（PR #27 golden）","done","Codex + CI","PR #27"],
    ["EVT-002","EVT","Rev.M1 Main + Evaluation Wing physical implementation","hold","Codex","unstarted; G0A backend adoption + G0B architecture/interface freeze"],
    ["EVT-003","MFG","評価基板 JLCPCBパッケージ","todo","Codex","EVT-002"],
    ["EVT-004","FW","評価FW・CSV計測","progress","Codex","EVT-001"],
    ["EVT-005","TEST","評価基板を発注","hold","User","EVT-003 / G1"],
    ["EVT-006","TEST","磁気センサ実測","hold","User + Codex","EVT-004,EVT-005"],
    ["PCB-001","PCB","accepted Main + Left/Right 21-key Wing回路図","todo","Codex","EVT-006 / G2"],
    ["PCB-002","PCB","キー配置・基板外形","todo","Codex","REQ-003,REQ-006"],
    ["PCB-003","PCB","本基板 配置配線","todo","Codex","PCB-001,PCB-002"],
    ["PCB-004","PCB","ERC/DRC/製造性チェック","todo","Codex + CI","PCB-003"],
    ["FW-001","FW","Vial対応基盤","todo","Codex","ELEC-003"],
    ["FW-002","FW","Hall走査・校正","todo","Codex","EVT-006"],
    ["FW-003","FW","レイヤーLED制御","todo","Codex","FW-001,ELEC-005"],
    ["MECH-001","MECH","筐体構造決定","todo","Codex","PCB-002"],
    ["MECH-002","MECH","STEP / STL生成","todo","Codex","MECH-001"],
    ["MFG-001","MFG","本基板 JLCPCBパッケージ","todo","Codex","PCB-004 / G3"],
    ["DOC-001","DOC","組立・校正・試験手順","todo","Codex","MFG-001,FW-002"],
    ["REL-001","REL","v1.0成果物固定","todo","Codex","DOC-001 / G5"]
  ]
};
