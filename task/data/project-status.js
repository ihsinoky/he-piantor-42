// Non-authoritative Dashboard read model. See docs/governance.md.
window.PROJECT_STATUS = {
  schemaVersion: 2,
  source: {
    confirmedAt: "2026-10-12T20:08:22Z",
    reference: "PR #80 merged into main",
    statusUrl: "https://github.com/ihsinoky/he-piantor-42/pull/80",
    reportUrl: "../docs/native-kicad-authoring-feasibility.md",
    historyUrl: "../docs/eda-path-history.md"
  },
  current: {
    heading: "実物Rev.M1の設計前",
    location: "実物Rev.M1の設計前。設計・配線方法の成立を評価中ですが、現時点の候補は未認定です。",
    blocker: "実物基板に必要な設計データ作成・接続検査・配線・間隔検査・製造出力・再現実行を一通り成立させる経路が未認定です。EDA-004Eの初回fixture受入も警告2件で不成立でした。",
    change: "小規模fixtureの保存・別プロセス再読込と形状・接続情報の保持を確認しました。これは実物Mainの成立確認ではなく、初回受入の警告も残っています。"
  },
  nextAction: {
    status: "次の技術計画は未承認 — 方針判断が必要",
    owner: "PO / PMO",
    action: "続行・保留・評価方針の見直しのどれを計画するか決める。新たな実験内容や順序はこの表示では提案・承認していません。",
    target: "受入済み評価報告と現工程の不足証拠",
    startCondition: "判断材料の不足、技術担当、完了条件、日程は未定です。"
  },
  plan: {
    planningNote: "目的・成果物・確認方法・完了条件・担当の見方で整理。正式な規格適合計画や追加の承認制度ではありません。",
    product: [
      { name:"実物Rev.M1の設計・製造・実測", purpose:"磁気方式・ピッチ・電力と代表的な信号経路を評価する。", output:"Main + pitch / 磁気Evaluation Wing(s)、計測FW、製造前パッケージ、測定結果レポート。", confirm:"G1: ERC/DRC、BOM、製造出力、測定計画を発注前に確認。G2: 磁気範囲、ノイズ、scan speed、電力、pitch usability等を実測。", completion:"実物で測定しG2判断の根拠を記録。注文承認は別判断。", owner:"技術担当未定。G1/G2判断はPO。", dependency:"EDA方法の承認が必要。計測FWとPCBに依存し、筐体はPCB条件後に連携。", source:"hardware/rev-m1/evaluation-plan.md · hardware/rev-m1/architecture.md" },
      { name:"測定結果を42キーRev.Aへ反映", purpose:"G2の方式・pitch判断を42キー設計へ反映する。", output:"accepted Main + project-owned Left/Right 21-key Wings + firmware。", confirm:"ERC/DRC、製造性、FW build、G3発注前レビュー。", completion:"必要packageとG3判断材料を用意。承認・発注は別判断。", owner:"技術担当未定。G2/G3判断はPO。", dependency:"Rev.M1実測、G2判断、Wing geometry承認。", source:"D-015 / hardware/rev-m1/architecture.md" },
      { name:"統合・実機確認", purpose:"筐体・基板・firmwareを統合して動作を確認する。", output:"組立済み機器、校正・試験手順。", confirm:"打鍵、全キー校正、USB/Vial、筐体適合。", completion:"統合試験とG4確認。", owner:"技術担当未定。G4判断はPO。", dependency:"Rev.A相当基板/FW。筐体はPCB条件に依存。", source:"docs/project-status.md · G4" },
      { name:"完成版", purpose:"再現可能な成果物を固定する。", output:"v1.0製造・firmware・筐体packageと手順。", confirm:"受入試験と成果物/製造手順の再現性。", completion:"G5でPOが完成版を承認。", owner:"技術担当未定。承認はPO。", dependency:"統合試験、校正、製造package。", source:"docs/project-status.md · G5" }
    ],
    qualification: {
      purpose:"実物基板の設計データから製造データまでを作成・検証し、同じ条件で再現できる技術経路を確立する。",
      output:"承認された工程計画、回路/PCBデータ、回路接続・配線・間隔の検査証拠、製造出力、再生成結果。",
      completion:"承認済みの計画がまだありません。必要な技術的exit条件、対象、担当をPOが計画決定時に補完します。",
      owner:"方針・計画の判断: PO、材料整理: PMO。技術実施担当は未定／未承認。",
      steps:[
        { id:"circuit", name:"回路・接続情報を作る", output:"回路図または同等の電気接続定義。", check:"部品/ピン/ネットの整合を回路レベルで検査。PCB配線後のDRCとは別。", result:"未認定", evidence:"固定版KiCadにpublicなheadless schematic作成経路を確認できず、現MainのERC/接続一致は未実施。" },
        { id:"board", name:"基板形状・接続・設計ルールへ反映", output:"部品形状・net割当・outline・stackとruleを持つPCB。", check:"保存再読込で定義した対象を比較し、初回DRC受入を確認。", result:"一部確認・初回受入失敗", evidence:"EDA-004EはKiCad 9.0.9の固定小規模fixtureのみ。PCB作成・保存・別process再読込とfixtureのobject parityは確認、DRC warning 2件でacceptance FAIL。" },
        { id:"route", name:"基板を配線する", output:"接続が保たれ、物理制約内に配線されたPCB。", check:"実際の銅配線で全対象netを接続し、電気・物理検証へ渡す。", result:"未実施", evidence:"EDA-004Eではrouteを行っていない。固定fixture内のlocal trackはMain配線の認定ではない。" },
        { id:"verify", name:"接続と間隔を検査する", output:"schematic/PCB接続一致と、配線後のclearance検査結果。", check:"回路レベル接続検査と配線後DRC/実効spacing rule検査を別々に確認。", result:"未認定", evidence:"Current Mainの接続検査・有効0.20 mm spacing ruleのnegative test・配線後DRCは未実施。" },
        { id:"manufacture", name:"製造データを出力する", output:"対象基板のGerber/drill/BOM/placement等の製造一式。", check:"PCB設計との一致、製造前DFMとG1 reviewを確認。", result:"未実施", evidence:"EDA-004Eの対象外。native KiCad fixtureから製造データを認定していない。" },
        { id:"reproduce", name:"同じ条件で再生成する", output:"記録済み固定環境から再生成した結果。", check:"新しい空のwork areaで成果物・意味の差を比較。", result:"未実施", evidence:"初回fixture acceptanceが失敗したため、empty-workspace regenerationを開始していない。" }
      ],
      notice:"この機能関係図は必要能力の説明です。次の実験順序・技術案・着手承認を表しません。"
    }
  },
  latestEvaluation: {
    id: "EDA-004E",
    title: "小規模fixtureの基板保存・別process再読込で形状・接続情報が保たれるか",
    purpose:"設計・配線方法の成立確認工程全体のうち、基板object作成と保存/読込の意味保持をKiCad 9.0.9で限定確認。",
    issue: { id:"79", url:"https://github.com/ihsinoky/he-piantor-42/issues/79" },
    acceptedRecord: { id:"80", url:"https://github.com/ihsinoky/he-piantor-42/pull/80", status:"mainで記録受入済み" },
    workStatus: "評価作業完了・記録受入済み",
    technicalStatus: "初回受入不成立 — PCB I/Oの一部確認であり、方式採用や製品合格ではありません。",
    learned: "KiCad 9.0.9で固定した小規模試験基板を作成・保存し、別プロセスで再読込できました。初回DRCに予期しない警告が2件あり、試験の受入条件は満たしませんでした。",
    unknown: "回路図作成経路・現在Mainの接続検査・実際の配線・配線後の間隔ルール・製造データ・空の作業場所からの再生成は、未認定または未実施です。",
    impact: "実物Rev.M1の設計開始、KiCad方式の採用、製造への移行は承認されていません。",
    nextCondition: "POが続行/保留/方針見直しを判断する場合、未認定範囲・担当・完了条件を埋めた計画を先に決めること。計画は未承認です。",
    testedQuestion:"KiCad 9.0.9で、小規模試験基板を作成・保存し、別processで再読込したときに固定fixtureの形状・接続情報が保持されるか。",
    evidenceBoundary:"fixture上のPCB I/Oとobject parityの証拠です。実物Mainの回路図/接続、配線、実効間隔、製造出力、再生成には適用できると確認していません。",
    evidence: [
      { label: "保存・別プロセス再読込", result: "成功", detail: "KiCad 9.0.9の固定小規模fixture" },
      { label: "接続情報・部品形状の保持", result: "一部のみ確認", detail: "固定fixtureの保存前後を比較" },
      { label: "初回fixtureのDRC受入", result: "失敗", detail: "予期しない警告2件。受入条件未達" },
      { label: "回路図作成・現在Mainの接続検査", result: "未確認", detail: "Main ERC/接続一致の評価に未着手" },
      { label: "実際の配線・配線後の間隔検査", result: "未実施", detail: "有効な配線ルールも未認定" },
      { label: "製造データ・空の場所からの再生成", result: "未実施", detail: "製造出力と再現性を示す証拠なし" }
    ]
  },
  currentProblems: [
    { title:"初回fixtureの受入失敗", basis:"KiCad 9.0.9 DRCで予期しないwarningが2件。U1 referenceのsilk overlapと未設定のResistor_SMD library。", impact:"このfixtureの受入条件を満たさず、評価はSTOP。", proof:"両warningの根拠を扱った条件での受入証拠が必要。", handling:"現在未解決。warning修正だけではschematic/Main/配線/製造経路の認定にならない。方式全体の不可能性を示す証拠でもない。", owner:"次計画が未承認のため担当未定。", source:"docs/native-kicad-authoring-feasibility.md § Fixed fixture and measured results", href:"../docs/native-kicad-authoring-feasibility.md" }
  ],
  uncertainties: [
    { title:"固定版のschematic作成・回路接続検査", basis:"KiCad 9.0.9にpinned public headless schematic authoring pathを確認できず、current Main ERC/parityも未実施。", impact:"正しい回路をPCBへ渡す方法が不明で、実物Main設計へ進めない。", proof:"承認対象となるschematic/connectivity routeと、Mainでの回路検査・一致証拠。", handling:"未認定。次の技術work/packageは未承認。", owner:"未定。POが計画を承認後に割当。", source:"docs/native-kicad-authoring-feasibility.md § Public functions and fixed environment", href:"../docs/native-kicad-authoring-feasibility.md" },
    { title:"小規模fixtureから実規模Mainへの適用", basis:"EDA-004Eは小さいfixture。一方、read-only inventoryは49 components、37 netsで、完全なMain generation/connection proofはない。", impact:"fixture parityが実Mainの部品、pins、networks、librariesを保証しない。", proof:"許可されたcurrent Main対象と製品要件に対する部品/接続/geometry reconciliation。", handling:"未確認。Mainへ適用できると推定しない。", owner:"未定。", source:"docs/native-kicad-authoring-feasibility.md § Representative Main read-only coverage", href:"../docs/native-kicad-authoring-feasibility.md" },
    { title:"接続正しさと必要な配線間隔の両立", basis:"EDA-004Eでは配線未実施。strict 0.20 mm effective-rule negative probe未実施。", impact:"connected copperと安全なspacingを同時に満たすと示せず、製造へ進めない。", proof:"対象回路に対する配線後の電気的接続確認と実効spacing rule/DRC証拠。", handling:"未実証。特定routerや次の実験順序は選定していない。", owner:"未定。", source:"docs/native-kicad-authoring-feasibility.md § Fixed fixture and measured results", href:"../docs/native-kicad-authoring-feasibility.md" },
    { title:"rule有効性と条件を揃えた再生成", basis:"保存された0.20 mm settingsは実効rule enforcementの証拠ではない。empty-directory rerunも未実施。", impact:"設定どおりの判定や再現可能な製造生成を保証できない。", proof:"必要間隔を判別するnegative testと、許可された固定条件でのfresh regeneration比較。", handling:"未認定・未実施。", owner:"未定。", source:"docs/native-kicad-authoring-feasibility.md § Fixed fixture and measured results", href:"../docs/native-kicad-authoring-feasibility.md" },
    { title:"固定環境/API/部品libraryの維持負担", basis:"評価環境はKiCad 9.0.9のPython SWIG PCB APIでdeprecated（公開removal planはKiCad 11）。exact library config不足が初回fixtureのwarning原因。package/API/library更新は未検証。", impact:"版更新、ABI、license/hash、library identityやrule設定の保守が必要になる可能性がある。具体的な維持費・工数は不明。", proof:"承認する保守範囲、再現可能な環境/ライブラリ手順、移行負担の根拠。", handling:"cost unknown。工数や寿命を推定していない。", owner:"未定。", source:"docs/native-kicad-authoring-feasibility.md § Public functions and fixed environment / Representative Main read-only coverage", href:"../docs/native-kicad-authoring-feasibility.md" },
    { title:"評価反復による製品工程の停滞", basis:"EDA-004B〜Eの履歴で技術経路は未認定。EDA-004E reportの0.750hはAI effortの保守的推定で、active engineer-hoursの計測値ではない。", impact:"経路評価を続けても実物Rev.M1の設計・製造・実測へ移れない可能性。発生率と残工数は不明。", proof:"製品段階へ移る判断条件、残す技術ゲート、予算/担当についてPOが選択。", handling:"判断が必要。新しい実験、対策、予算は未承認。", owner:"POが判断。次の技術担当未定。", source:"docs/eda-path-history.md · docs/native-kicad-authoring-feasibility.md § STOP, reporting and effort", href:"../docs/eda-path-history.md" }
  ],
  decision: {
    question:"次の計画を作るか、現状を保留するか、方針を見直すか。方式採用やRev.M1設計開始は別判断です。",
    evidence:"受入済みEDA-004E report/history、回路図/Main接続の未確認、Main規模へ適用する証拠不足、電気接続とspacingを両立する配線/有効rule証拠不足、manufacturing/reproducibility未実施、API/library維持負担不明。",
    owner:"POが判断。PMOは既存記録と不足証拠を整理。技術計画の担当は未割当。",
    planStatus:"承認済みの次工程計画・担当・完了条件・日程はありません。具体的な次の実験は提案・未承認であり、ここでは提示しません。",
    proposal:"未承認の提案をこのPRでは追加しない。"
  },
  history: [
    { name: "初期KiCad", tested: "旧4キー回路図とPCBの修正・CI検査", stopped: "繰り返したファイル形式修正の記録があり、PR #10 CIのPCB DRCは587違反・未接続40件。個々の原因とwriterは不明。", reuse: "既存シンボル・footprint・要求を検証済み参照として再利用。", retry: "異なる保存/検証方式と、現在の電気・形状の証拠が必要。", refs: "PR #6 / #10、D-014、Issue #79", href: "https://github.com/ihsinoky/he-piantor-42/pull/10" },
    { name: "JITX", tested: "部品モデル、電気的整合、headless物理・後工程", stopped: "PO判断D-016でRev.M1/Rev.Aの物理backendはNO-GO。完全な対応済みheadless多層配線は実証されず。", reuse: "受入済みの部品・電気・DFM・後工程の知見。", retry: "対応済みの完全配線手順と、投資・保守範囲の別途承認が必要。", refs: "D-016、Issue #55、C4B5", href: "../docs/eda-path-history.md" },
    { name: "stock tscircuit", tested: "native stock物理配線とMainのclearance介入", stopped: "評価した内部router探索は終了。介入A/Bで誤配線回帰があり、backendは未採用。", reuse: "native electrical source、固定モデル、独立物理検証。", retry: "対応済み機構で接続性と0.20 mm間隔を同時に示す必要。", refs: "D-018、Issue #61–#71、EDA-003B–F", href: "../docs/eda-path-history.md" },
    { name: "Circuit JSON → KiCad", tested: "bounded converter repairと小規模/Main前段の検査", stopped: "別々の試行でGND landのnet欠落/short、footprint library ID衝突、schematic ERC未成立。配線試行なし。", reuse: "raw fixture、固定環境、capture手順と限られたcheckerの知見。", retry: "正確なfootprint identityと接続済みschematic/ERC等の条件が必要。", refs: "EDA-004B–D、Issue #73 / #75 / #77、PR #76 / #78", href: "../docs/eda-path-history.md" },
    { name: "native KiCad objects", tested: "KiCad 9.0.9の固定小規模PCB作成・保存・別プロセス読込", stopped: "初回DRCに予期しない警告2件。回路図経路がなく、Mainへ進む前にSTOP。", reuse: "PCB I/Oと固定fixtureの保存前後の比較結果。", retry: "PO/PMOが具体的な回路図経路を承認し、限定した修正・実効ルール試験・条件付き再評価を許可した場合のみ。", refs: "EDA-004E、Issue #79、PR #80、D-014", href: "../docs/native-kicad-authoring-feasibility.md" }
  ],
  evidenceLinks: {
    latestReport: "../docs/native-kicad-authoring-feasibility.md",
    pathHistory: "../docs/eda-path-history.md",
    githubActions: "https://github.com/ihsinoky/he-piantor-42/actions",
    issue79: "https://github.com/ihsinoky/he-piantor-42/issues/79",
    pr80: "https://github.com/ihsinoky/he-piantor-42/pull/80"
  },
  milestones: [
    {id:"M0",name:"設計方針・基本形状",status:"done",deliverable:"過去の42キー要件・17 mm配置・取得方針（D-015でpitch再評価）",exit:"主要要件・キー中心座標・評価方針が文書化済み"},
    {id:"M1",name:"磁気方式・評価基板",status:"current",deliverable:"再利用Main + pitch/磁気Evaluation Wing(s)、計測FW、実測レポート（hardware未実装）",exit:"ERC/DRC合格、実測で磁気・pitch・analog pathをG2判断"},
    {id:"M2",name:"42キー Rev.A",status:"next",deliverable:"accepted Main再利用 + Left 21-key Wing + Right 21-key Wing + production FW（G2判断後）",exit:"Main/Wing ERC/DRC・製造性検査とFW buildが合格"},
    {id:"M3",name:"統合・筐体・試験",status:"todo",deliverable:"筐体、統合機、組立・校正・試験手順",exit:"実機操作、全キー校正、USB、Vial、筐体適合の試験に合格"},
    {id:"M4",name:"完成版リリース",status:"todo",deliverable:"再現可能なv1.0製造・FW・筐体パッケージ",exit:"最終成果物を固定しユーザーが完成版を承認"}
  ],
  streams: [
    {name:"Hardware",cells:["設計方針 完了","成立確認中: EDA-004Eの固定fixtureはPCB I/Oの一部確認、初回DRC受入不成立。実物Mainは未認定。","Main再利用 + Left/Right Wings","統合改版","製造版"]},
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
    {name:"G0A JITX Backend Adoption",status:"done",check:"C0-C3 accepted evidence + historical C4B-C4B4A + C4B4B external disposition + C4B5 routing BLOCKED evidence",trigger:"Completed PO decision, issue #55 / D-016: JITX active physical backend NO-GO for Rev.M1 / Rev.A; C4B5 complete-routing workflow not demonstrated",unlocks:"Historical JITX NO-GO preserved; G0B remains done; EDA-004B #73 ENVIRONMENT_BLOCKED, representative Main unqualified; full implementation blocked"},
    {name:"G0B Rev.M1 Architecture / Interface Freeze",status:"done",check:"D-017: exact JST GH 14-position connector/pinout, six common-GND returns, external WING_EN pull-down, nominal 100 mm 1:1 harness, pitch Wings/full-load three-TMUX-three-ADC coverage, test access, measurement framework, DFM",trigger:"Issue #57 PO GO accepted the freeze",unlocks:"Architecture/interface remain frozen; EDA-004B #73 ENVIRONMENT_BLOCKED; EDA-004C #75 CONVERSION_BLOCKED; further work requires PO disposition; full implementation blocked"},
    {name:"G1 Rev.M1 Main + Evaluation Wing pre-order review",status:"not-ready",check:"Main/Wing circuit/ERC, DRC, BOM, actual manufacturing outputs, measurement plan",trigger:"manufacturing package complete after separately accepted backend qualification and authorized full Rev.M1 implementation",unlocks:"Rev.M1 Main + Evaluation Wing order"},
    {name:"G2 post-EVT-002 magnetic / pitch / analog-path decision",status:"not-ready",check:"range, noise, scan speed, power, interference, interconnect, 17.0/16.5/16.0 mm usability",trigger:"physical measurements/report complete",unlocks:"production pitch and magnetic architecture / Rev.A circuit freeze"},
    {name:"G3 Rev.A 発注前確認",status:"not-ready",check:"Main/Left/Right DRC, BOM, Gerber, drill/PnP, cost",trigger:"42-key manufacturing package complete",unlocks:"Rev.A PCBA order"},
    {name:"G4 実機操作確認",status:"not-ready",check:"打鍵、校正、Vial、USB、筐体適合",trigger:"統合機のbring-up完了時",unlocks:"完成版の固定"},
    {name:"G5 最終版承認",status:"not-ready",check:"v1.0の全製造物と手順",trigger:"受入試験合格時",unlocks:"v1.0リリース"}
  ],
  risks: [
    {kind:"risk",title:"USB product manufacturing release",detail:"OPEN — PRE-ORDER DFM REVIEW REQUIRED for Rev.M1 / Rev.A. All four nominal gaps meet JLCPCB 0.20 mm capability floor, not production approval. 0.25 mm preferred target and 0.001 mm numerical review guard are project-owned, not JLCPCB requirements or recommendations. Increase margin where feasible, or explicitly accept/document minimum geometry and pass actual order-time CAM/process review; no production exception granted."},
    {kind:"risk",title:"Historical JITX downstream thickness handoff",detail:"Retained JITX path evidence/limitation, not the primary NO-GO reason. PASS_WITH_LIMITATIONS: generated CAD/Gerber-job overall thickness metadata is misleading (1.6 mm); exclude it from manufacturing handoff and independently select/confirm 1.2 mm finished thickness."},
    {kind:"risk",title:"pitch / キーキャップ干渉",detail:"17.0 / 16.5 / 16.0 mmで使用感・磁気・switch/keycap干渉を比較。100 x 100 mmはcost targetのみ。"},
    {kind:"risk",title:"磁束レンジと個体差",detail:"Main + Evaluation Wingでスイッチ・センサ・距離・interconnectを一組として実測する。"},
    {kind:"risk",title:"42センサの電力",detail:"Accepted DRV5055 at 5 V: 3 mA typical / 5 mA maximum; approximately 127 mA per 21-key Wing / 254 mA for 42 sensors-two Wings. Planning estimates only; final USB/system power budget, other loads and startup/inrush qualification remain open."},
    {kind:"risk",title:"中央部のねじり荷重",detail:"Main/Wingの接続・固定と筐体補強は後続mechanical gateで検証する。"},
    {kind:"risk",title:"JITX RuntimeDesign stability",detail:"EDA-002C0 is accepted PASS for the challenger/parity workflow. RuntimeDesign query and net-resolution methods remain documented but explicitly experimental; every future JITX Python package or runtime change must rerun the normalized exporter and bootstrap graph self-test before compatibility is assumed."},
    {kind:"risk",title:"KiCad importer reuse",detail:"EDA-003A accepted UPSTREAM_FIX_CANDIDATE. Both copper-pour keepouts silently lost without material-loss warnings; rounded-pad corner radius incorrect. Reuse NOT approved; native TSX authoritative, KiCad reference-secondary evidence. Future reuse needs separately accepted fidelity evidence after fixes."},
    {kind:"risk",title:"Historical alternate-method evaluation",detail:"EDA-004B through EDA-004E are completed reports with different targets and results. Their CI, partial checks, or historical success do not qualify the current Rev.M1 design path."}
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
    ["EDA-002C4B","EDA","JITX board-level physical/manufacturing pipeline proof","done","Codex","issue #43; historical BLOCKED investigation retained; current path disposition in C4B4B; routing in C4B5"],
    ["EDA-002C4B2","EDA","JITX → headless KiCad downstream CAM","done","Codex","issue #45 / merged PR #46; historical BLOCKED evidence retained; current disposition in C4B4B"],
    ["EDA-002C4B3","EDA","JITX downstream manufacturing blocker disposition","done","Codex","issue #47 / merged PR #48; historical BLOCKED investigation retained; USB reclassified by C4B4B as product pre-order DFM risk"],
    ["EDA-002C4B4A","EDA","USB NPTH JLCPCB DFM qualification coupon","done","Codex","issue #49 / merged PR #50; unchanged geometry and human-upload package completed"],
    ["EDA-002C4B4B","EDA","JLCPCB external DFM evidence and disposition","done","Codex","issue #51; external evidence classified; JLCDFM INCONCLUSIVE; downstream path PASS_WITH_LIMITATIONS; USB OPEN — PRE-ORDER DFM REVIEW REQUIRED; accepted disposition; merged PR #52"],
    ["EDA-002C4B5","EDA","Complete-routing feasibility","done","Codex","issue #53 / merged PR #54; done / accepted BLOCKED evidence: 39 downstream unconnected + dangling via; retained unchanged"],
    ["EDA-002C4C","EDA","JITX adoption Human Gate","done","PMO + Human","issue #55 / D-016; completed PO NO-GO for JITX physical backend; native stock tscircuit historical forward path at D-016; G0B remains done; D-018 now governs alternate-backend planning"],
    ["EDA-003A","EDA","KiCad footprint importer requalification","done","Codex","issue #58 / merged PR #59; accepted UPSTREAM_FIX_CANDIDATE; keepouts silently lost, warning gap, incorrect rounded-pad radius; importer reuse NOT approved / native TSX authoritative"],
    ["EDA-003B","EDA","Representative stock-tscircuit physical/routing proof","done","Codex","#61 / PR #62: BLOCKED — ROUTING_CAUSED_PHYSICAL_ERRORS; Main seven wrong-net components; qualification execution complete, board unqualified"],
    ["EDA-003C","EDA","Latest-stock routing risk qualification","done","Codex","#63 / PR #64: WRONG_NET_FIXED_LOWER_RISKS_REMAIN; isolated 0.0.2748; production 0.0.2646 unchanged; Main/Wing physical and Main export blockers remain"],
    ["EDA-003D","EDA","Main clearance risk triage","done","Codex","#65 / PR #66: BACKEND_DECISION_REQUIRED; BROAD / DISTRIBUTED; 71 records / 54 physical conflicts"],
    ["EDA-003E","EDA","Via-clearance signature fixability","done","Codex","#67 / PR #68: BACKEND_DECISION_REQUIRED; numeric lead, repair boundary unqualified"],
    ["EDA-003F","EDA","Strict clearance intervention A/B","done","Codex","#69 / PR #70: INTERVENTION_UNSAFE_REGRESSION; K1, two wrong-net copper components; no confirmation"],
    ["EDA-004A","EDA","Alternate physical backend Human Gate planning","done","PO + Codex","#71 explicit PO comment / D-018: planning GO; B first bounded qualification candidate, not adopted; no experiment authorized; next execution Issue body drafted for PO manual creation"],
    ["EDA-004B","EDA","Bounded headless KiCad + Freerouting Main qualification","done","Codex","#73 / PR #74: ENVIRONMENT_BLOCKED / P1_SMOKE_CAPTURE_GUARD_ERROR; Stage 1 partial, evidence PARTIAL (missing raw smoke JSON, executor capture/sequence errors); Main initial-confirmation 0/0, smoke routing 0; stages 2-4 and ERC/DRC/reconciliation NOT ENTERED; all Main metrics null; terminal reporting complete / technical qualification incomplete; first executor capture failure, secondary P1_CONVERTER_MODULE_LOAD; immediate stop not followed; backend unqualified"],
    ["EDA-004C","EDA","Candidate B headless smoke requalification","done","Codex","EDA-004C #75 / PR #76 CONVERSION_BLOCKED / C1_DUPLICATE_GND_PAD_NET_LOSS; fixed-source build and input checks succeeded after disclosed preparation corrections; second duplicate GND land net absent in KiCad, DRC shorting_items; synthetic ERC unqualified; smoke initial-fresh 0/0, Main 0; DSN-SES/post-route/reproducibility NOT ENTERED; 26 parity fault replays detected; next PMO/PO review; terminal reporting complete; no backend adoption or Main PASS"],
    ["EVT-001","EVT","historical 4-key native electrical qualification fixture（PR #27 golden）","done","Codex + CI","PR #27"],
    ["EDA-004D","EDA","Bounded converter repair","done","Codex","#77 / PR #78 CONVERSION_BLOCKED: D1_FOOTPRINT_LIBRARY_ID_COLLISION; limited repair parity pass, remaining ERC failures; no routes"],
    ["EDA-004E","EDA","Native KiCad authoring feasibility and history","done","Codex","#79 / PR #80: 固定fixtureのPCB I/Oと形状保持を一部確認。初回受入は予期しないDRC警告2件で不成立。Main・配線・製造・再生成は未認定。"],
    ["EVT-002","EVT","Rev.M1 Main + Evaluation Wing physical implementation","hold","Codex","未承認。次の技術評価方針についてPO/PMOの判断待ち。詳細: ../docs/native-kicad-authoring-feasibility.md"],
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
