// Non-authoritative Dashboard read model. See docs/governance.md.
window.PROJECT_STATUS = {
  schemaVersion: 1, updatedAt: "2026-10-03T11:01:11+00:00",
  currentWork: "EDA-002C1 in progress / blocked: AP2112K-3.3TRG1 accepted; eight component source/package STOPs documented（M1電気モデルは凍結済み）",
  evidence: {
    commit: { sha: "795479e", at: "2026-10-02T22:41:32+09:00", summary: "Implement native M1 four-key Hall evaluation circuit (#27)" },
    pullRequest: { state: "snapshot", label: "Historical snapshot; check GitHub for current PR state" },
    ci: { result: "UNKNOWN", at: null, lastSuccess: "Not recorded", detail: "GitHub Actions の結果はこの静的 snapshot に未同期" },
    artifacts: { state: "FROZEN", detail: "PR #27 native tscircuit M1 electrical golden reference" }
  },
  milestones: [
    {id:"M0",name:"設計方針・基本形状",status:"done",deliverable:"42キー要件、17 mm配置、取得方式の設計方針",exit:"主要要件・キー中心座標・評価方針が文書化済み"},
    {id:"M1",name:"磁気方式・評価基板",status:"current",deliverable:"4キーHallセンサ評価基板、計測FW、実測レポート",exit:"ERC/DRC合格、実機でレンジ・ノイズ・走査速度・消費電力を測定し方式を確定"},
    {id:"M2",name:"42キー Rev.A",status:"next",deliverable:"製造可能な42キーPCB Rev.Aと基本Vial/Hall FW",exit:"本基板ERC/DRC・製造性検査とFW buildが合格"},
    {id:"M3",name:"統合・筐体・試験",status:"todo",deliverable:"筐体、統合機、組立・校正・試験手順",exit:"実機操作、全キー校正、USB、Vial、筐体適合の試験に合格"},
    {id:"M4",name:"完成版リリース",status:"todo",deliverable:"再現可能なv1.0製造・FW・筐体パッケージ",exit:"最終成果物を固定しユーザーが完成版を承認"}
  ],
  streams: [
    {name:"Hardware",cells:["設計方針 完了","M1 電気モデル凍結 / JITX graph export PASS accepted / EDA-002C1 blocked checkpoint","Rev.A PCB","統合改版","製造版"]},
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
    {name:"G1 評価回路レビュー",status:"not-ready",check:"回路/ERC、BOM、測定計画",trigger:"評価PCB製造データ完成時",unlocks:"評価基板の発注"},
    {name:"G2 磁気方式確定",status:"not-ready",check:"レンジ、ノイズ、走査速度、電力、干渉",trigger:"評価基板の実測完了時",unlocks:"42キー回路の固定"},
    {name:"G3 Rev.A 発注前確認",status:"not-ready",check:"本PCB DRC、BOM、Gerber、コスト",trigger:"42キー製造パッケージ完成時",unlocks:"Rev.A PCBA発注"},
    {name:"G4 実機操作確認",status:"not-ready",check:"打鍵、校正、Vial、USB、筐体適合",trigger:"統合機のbring-up完了時",unlocks:"完成版の固定"},
    {name:"G5 最終版承認",status:"not-ready",check:"v1.0の全製造物と手順",trigger:"受入試験合格時",unlocks:"v1.0リリース"}
  ],
  risks: [
    {kind:"risk",title:"17 mmキーキャップ干渉",detail:"一般的な約18 mm幅は干渉するため16.5 mm角MX軸を前提に検証する。"},
    {kind:"risk",title:"磁束レンジと個体差",detail:"スイッチ・センサ・距離を一組として4キー評価基板で先に実測する。"},
    {kind:"risk",title:"42センサの電力",detail:"USB 500 mA近辺の可能性があるため本基板前に電力Gateを通す。"},
    {kind:"risk",title:"中央部のねじり荷重",detail:"一体型PCB外形と筐体補強を並行設計する。"},
    {kind:"risk",title:"JITX RuntimeDesign stability",detail:"EDA-002C0 is accepted PASS for the challenger/parity workflow. RuntimeDesign query and net-resolution methods remain documented but explicitly experimental; every future JITX Python package or runtime change must rerun the normalized exporter and bootstrap graph self-test before compatibility is assumed."},
    {kind:"risk",title:"M1 layout gated",detail:"PR #27 native TSX electrical model remains the authoritative frozen golden reference. JITX is only a challenger; EVT-002 and final 2-layer placement/routing/DRC remain gated."}
  ],
  tasks: [
    ["DSH-001","PM","専用HTMLダッシュボード","done","Codex","-"],
    ["DSH-002","PM","Project Health / Roadmap / Gate表示","done","Codex","DSH-001"],
    ["REQ-001","REQ","全体仕様書","progress","Codex","-"],
    ["REQ-002","REQ","通常高さ磁気スイッチ選定","progress","Codex","-"],
    ["REQ-003","REQ","17 mmピッチ用キーキャップ適合確認","progress","Codex","REQ-002"],
    ["REQ-004","REQ","Piantorキー中心座標抽出","done","Codex","-"],
    ["REQ-005","REQ","120°一体型ジオメトリ確定","progress","Codex","REQ-004"],
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
    ["EDA-002C1","EDA","JITX component modeling","hold","Copilot CLI","AP2112 accepted; eight exact source/package STOPs"],
    ["EVT-001","EVT","4キー評価基板 native 電気モデル（PR #27 golden）","done","Codex + CI","PR #27"],
    ["EVT-002","EVT","4キー評価基板 PCB配置配線","hold","Codex","M1 JITX electrical parity / product-owner gate"],
    ["EVT-003","MFG","評価基板 JLCPCBパッケージ","todo","Codex","EVT-002"],
    ["EVT-004","FW","評価FW・CSV計測","progress","Codex","EVT-001"],
    ["EVT-005","TEST","評価基板を発注","hold","User","EVT-003 / G1"],
    ["EVT-006","TEST","磁気センサ実測","hold","User + Codex","EVT-004,EVT-005"],
    ["PCB-001","PCB","42キー本基板 回路図","todo","Codex","EVT-006 / G2"],
    ["PCB-002","PCB","キー配置・基板外形","todo","Codex","REQ-003,REQ-005"],
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
