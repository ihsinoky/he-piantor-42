// Non-authoritative Dashboard read model. See docs/governance.md.
window.PROJECT_STATUS = {
  schemaVersion: 2,
  source: {
    confirmedAt: "2026-10-12T20:08:22Z",
    reference: "mainの正本記録",
    statusUrl: "https://github.com/ihsinoky/he-piantor-42/pull/80",
    reportUrl: "../docs/native-kicad-authoring-feasibility.md",
    historyUrl: "../docs/eda-path-history.md"
  },
  current: {
    heading: "実物Rev.M1の設計前",
    location: "実物Rev.M1の設計前。設計・配線方法の成立を評価中ですが、現時点の候補は未認定です。",
    blocker: "実物基板に必要な設計データ作成・接続検査・配線・間隔検査・製造出力・再現実行を一通り成立させる経路が未認定です。"
  },
  nextAction: {
    status: "次の実験は未承認（既存の条件は維持）",
    owner: "PMOが案と不足材料を整理し、POが判断",
    action: "続行・保留・方針見直しを判断する。新しい試験案をこの表示で選定・承認していません。",
    target: "EDA-004Eの受入済み報告、D-018の計画と既存条件",
    startCondition: "PMOが対象・方法・担当案・受入条件・投資範囲を整理した後。実施にはPO作成IssueとPO指示が必要。"
  },
  plan: {
    planningNote: "既存の製品条件と、次の未承認の試験計画を分けて表示します。",
    product: [
      { name:"実物Rev.M1の設計・製造・実測", status:"実装未着手・技術経路の判断待ち", purpose:"磁気方式・ピッチ・電力と代表的な信号経路を評価する。", output:"Main基板・ピッチ/磁気の評価用基板、計測用ファームウェア、発注前資料、測定報告書。", confirm:"G1: 回路・基板検査、部品表、製造データ、測定計画を発注前に確認。G2: 磁気範囲、ノイズ、走査速度、電力、ピッチの使いやすさを実測。", completion:"実物で測定しG2判断の根拠を記録。注文承認は別判断。", owner:"技術担当未定。G1/G2判断はPO。", dependency:"設計方法の判断が必要。計測用ファームウェアと基板に依存し、筐体は基板条件後に連携。", source:"hardware/rev-m1/evaluation-plan.md · hardware/rev-m1/architecture.md" },
      { name:"測定結果を42キーRev.Aへ反映", purpose:"G2の方式・ピッチ判断を42キー設計へ反映する。", output:"確定したMain基板・プロジェクト所有の左右21キー基板・ファームウェア。", confirm:"回路・基板検査、製造性、ファームウェアのビルド、G3発注前レビュー。", completion:"必要な資料とG3判断材料を用意。承認・発注は別判断。", owner:"技術担当未定。G2/G3判断はPO。", dependency:"Rev.M1実測、G2判断、左右基板形状の承認。", source:"D-015 / hardware/rev-m1/architecture.md" },
      { name:"統合・実機確認", purpose:"筐体・基板・ファームウェアを統合して動作を確認する。", output:"組立済み機器、校正・試験手順。", confirm:"打鍵、全キー校正、USB/Vial、筐体適合。", completion:"統合試験とG4確認。", owner:"技術担当未定。G4判断はPO。", dependency:"Rev.A相当基板とファームウェア。筐体は基板条件に依存。", source:"docs/project-status.md · G4" },
      { name:"完成版", purpose:"再現可能な成果物を固定する。", output:"v1.0製造・ファームウェア・筐体一式と手順。", confirm:"受入試験と成果物・製造手順の再現性。", completion:"G5でPOが完成版を承認。", owner:"技術担当未定。承認はPO。", dependency:"統合試験、校正、製造データ一式。", source:"docs/project-status.md · G5" }
    ],
    qualification: {
      status:"既存条件あり · 次の実験は未承認",
      purpose:"実物基板の設計データを作り、接続・配線・間隔・製造出力を確かめ、同じ条件で再現できる方法を成立させる。",
      output:"回路・基板データと、接続・配線・間隔・製造出力・再生成の確認記録。",
      completion:"この評価全体の目標と制約は既定です。EDA-004E後の個別対象・方法・担当・受入条件は未承認です。",
      owner:"技術案と判断材料: PMO。実施判断: PO。新しい実験の実施担当は未定。",
      establishedSummary:"2層・厚さ1.2 mm・配線間隔0.20 mmを維持。D-018はMain先行・初回Main評価の技術作業上限2人日を定めた限定計画で、次の実験許可ではありません。",
      establishedDetail:"D-015/D-017: 2層・1.2 mmの基板基準。D-018: 0.20 mmの材料間隔、Main合格後にWing/出力へ進む順序、初回Main配線1回と初回合格時のみ新規確認1回、初回Main評価の技術作業上限2人日。候補Bの限定計画に対する条件で、他候補や次回実験へ自動適用・実施許可しません。候補Bは優先された評価候補であり、採用済み方式ではありません。EDA-004B〜Dは同計画下の過去の報告で、配線前に停止しました。",
      establishedSources:[
        {label:"project decisions D-015 / D-017 / D-018",href:"../docs/decisions.md"},
        {label:"bounded historical qualification plan",href:"../docs/alternate-physical-backend-qualification-plan.md"},
        {label:"EDA path history",href:"../docs/eda-path-history.md"}
      ],
      steps:[
        { id:"circuit", name:"回路・接続情報を作る", output:"部品どうしの電気的なつながりを記した回路図。", check:"回路図上で部品・端子・接続の整合を確認する。配線後の基板検査とは別。" },
        { id:"board", name:"基板の形・部品・接続・設計条件へ反映", output:"部品の形や接続、基板外形と設計条件を反映した基板データ。", check:"保存前後で形状・接続が保たれることと、初回の基板検査を確認する。" },
        { id:"route", name:"基板を配線する", output:"指定された接続を物理的な銅箔で結んだ基板。", check:"対象の接続が実際の銅箔でつながっているかを確認する。" },
        { id:"verify", name:"接続と配線間隔を検査する", output:"回路図との接続一致と、配線後の接続・間隔の確認記録。", check:"回路図の接続確認と、配線後の基板検査・間隔確認を分けて行う。" },
        { id:"manufacture", name:"製造データを出力する", output:"基板設計に対応した製造用データ一式。", check:"基板との一致と、発注前の製造条件確認を行う。" },
        { id:"reproduce", name:"同じ条件で再生成する", output:"記録した環境と入力から再生成したデータ。", check:"空の作業場所で再生成し、結果が一致するか比較する。" }
      ],
      notice:"これは必要な機能の関係です。次の試験順序や実施承認を示しません。"
    }
  },
  latestEvaluation: {
    id: "EDA-004E",
    title: "小規模な試験基板の保存・再読込で形状と接続が保たれるか",
    purpose:"設計・配線方法を確かめる工程全体のうち、試験基板の作成・保存・再読込を限定して確認。",
    issue: { id:"79", url:"https://github.com/ihsinoky/he-piantor-42/issues/79" },
    acceptedRecord: { id:"80", url:"https://github.com/ihsinoky/he-piantor-42/pull/80", status:"mainで記録受入済み" },
    workStatus: "評価作業完了・記録受入済み",
    technicalStatus: "小規模試験基板の保存・再読込と確認対象の形状・接続情報の保持は成功。初回受入条件は未達で、方式採用や製品合格ではありません。",
    currentSummary:"保存ファイルを別のプログラム実行で開き直し、確認対象の形状・接続情報は小規模試験基板上で保持。警告2件で初回受入未達、実物Mainへの適用は未確認です。",
    currentProblem: { title:"試験基板で警告が2件あり、受入条件に達しなかった", basis:"KiCad 9.0.9の基板検査で予期しない警告が2件。U1の部品番号の印刷が、はんだ付け部分に重なる警告と、Resistor_SMD部品ライブラリの未設定。", impact:"この試験基板は受入条件未達。警告の解消だけでは、実物基板を設計できるとは判断できません。", proof:"両警告を扱った条件での受入証拠が必要。", handling:"次の実験は未承認。警告はこの試験の停止理由であり、方式全体が実現不能という証拠ではない。", owner:"PMOが材料を整理し、POが方針判断。実施担当は未定。", source:"docs/native-kicad-authoring-feasibility.md § Fixed fixture and measured results", href:"../docs/native-kicad-authoring-feasibility.md" },
    learned: "小規模な試験基板を作成・保存し、保存したファイルを別のプログラム実行で開き直しました。今回の試験基板では、確認対象の形状と接続情報が保たれました。実物Mainへの適用は未確認です。初回の基板検査では警告2件があり、受入条件は未達でした。",
    unknown: "実物Mainへの適用、回路図の作成と接続確認、実際の配線、必要な配線間隔の確認、製造データ、空の作業場所からの再生成は未認定または未実施です。",
    impact: "実物Rev.M1の設計開始、方式の採用、製造への移行は承認されていません。",
    nextCondition: "次の実験は未承認です。PMOが既存条件・不足証拠・対象・方法・担当案・個別受入条件を整理し、POが判断します。実施には別IssueとPO指示が必要です。",
    testedQuestion:"KiCad 9.0.9で小規模な試験基板を作成・保存し、保存したファイルを別のプログラム実行で開き直したとき、確認対象の形状と接続情報が保たれるか。",
    evidenceBoundary:"指定した小規模試験基板では確認対象の形状と接続情報が保たれました。この結果は試験対象内での成功であり、実物Mainの回路・接続、配線、必要な間隔、製造データ、再生成への適用は未確認です。",
    coverage: [
      { stepId:"circuit", result:"未認定", detail:"KiCad 9.0.9で画面操作なしに回路図を自動作成する公開の方法を確認できず、実物Mainの接続検査も未実施。" },
      { stepId:"board", result:"試験対象内で成功", detail:"KiCad 9.0.9の小規模試験基板で、保存したファイルを別のプログラム実行で開き直し、確認対象の形状と接続情報が保たれることを確認。初回検査は警告2件で受入条件未達。実物Mainへの適用は未確認。" },
      { stepId:"route", result:"未実施", detail:"実際の配線は行っていません。試験基板の短い配線はMainの配線能力を示しません。" },
      { stepId:"verify", result:"未認定", detail:"実物Mainの接続検査、0.20 mm間隔設定が働くかの確認、配線後の基板検査は未実施。" },
      { stepId:"manufacture", result:"未実施", detail:"この評価の対象外。製造データの証拠なし。" },
      { stepId:"reproduce", result:"未実施", detail:"初回受入条件未達のため、空の作業場所からの再生成は未実施。" }
    ],
    evidence: [
      { label: "保存ファイルの開き直し", result: "成功", detail: "KiCad 9.0.9の小規模な試験基板を別のプログラム実行で確認" },
      { label: "確認対象の形状・接続情報の保持", result: "成功", detail: "指定した小規模試験基板の保存前後を比較。実物Mainへの適用は未確認" },
      { label: "試験基板の初回検査", result: "失敗", detail: "予期しない警告2件。受入条件未達" },
      { label: "回路図作成・実物Mainの接続検査", result: "未確認", detail: "実物Mainの回路・接続確認は未実施" },
      { label: "実際の配線・配線後の間隔検査", result: "未実施", detail: "配線と配線間隔の検査は未実施" },
      { label: "製造データ・空の作業場所からの再生成", result: "未実施", detail: "製造用データと再現性を示す証拠なし" }
    ]
  },
  uncertainties: [
    { title:"回路図を作り、回路の接続を確かめる方法が未確認", basis:"KiCad 9.0.9で画面操作なしに回路図を自動作成する公開の方法を確認できず、実物Mainの接続検査も未実施。", impact:"正しい回路を基板へ反映できると確認できず、実物設計へ進めません。", proof:"回路図の作成方法と、対象Mainで回路のつながりが合う証拠。", handling:"未認定。次の実験は未承認。", owner:"PMOが案と材料を整理し、POが判断。実施担当未定。", source:"回路図・接続経路の技術報告", href:"../docs/native-kicad-authoring-feasibility.md" },
    { title:"小規模試験の結果を実物Mainに適用できるか不明", basis:"直近評価は小規模基板のみ。読み取り調査では部品49個、電気的につながるグループ37個（ネット）があるが、Mainの生成・接続確認ではない。", impact:"試験基板の成功だけでは実物Mainの部品・端子・接続を保証できません。", proof:"許可されたMain設計で部品・端子・接続・形状が一致する証拠。", handling:"未確認。Mainに適用可能とは扱わない。", owner:"PMOが不足証拠を整理。実施担当未定、判断はPO。", source:"実物Mainの読み取り範囲", href:"../docs/native-kicad-authoring-feasibility.md" },
    { title:"正しい接続と必要な配線間隔の両立が未実証", basis:"直近の小規模基板では配線しておらず、0.20 mm間隔設定が実際に検出できるかも未確認。", impact:"接続と安全な間隔を同時に満たす基板と示せず、製造へ進めません。", proof:"対象基板で配線接続と必要な間隔を確認した証拠。", handling:"未実証。次の配線方法や試験順序は未承認。", owner:"PMOが案と材料を整理し、POが判断。実施担当未定。", source:"試験基板の検査・配線結果", href:"../docs/native-kicad-authoring-feasibility.md" },
    { title:"配線間隔の検査と条件をそろえた再生成が未確認", basis:"間隔設定が実際に働くかの確認と、空の作業場所からの再生成は未実施。", impact:"設定した間隔が守られることや、製造データを再現できることを保証できません。", proof:"必要間隔を検出する確認と、記録条件による再生成の比較。", handling:"未認定・未実施。", owner:"実施担当未定。対象・方法・受入条件をPMOが整理し、POが判断。", source:"試験基板の検査・再生成結果", href:"../docs/native-kicad-authoring-feasibility.md" },
    { title:"固定環境・廃止予定の基板設計用プログラム・部品情報の維持負担", basis:"KiCad 9.0.9のPython基板APIは廃止予定で、部品ライブラリ設定不足が今回の警告原因の一つ。更新時の検証は未実施。", impact:"環境や部品情報を保守できる範囲が不明で、長期利用の判断材料が不足しています。", proof:"維持する環境・部品情報と、更新・再現に必要な作業の証拠。", handling:"維持費・工数は不明。推定していません。", owner:"PMOが判断材料を整理。担当と維持範囲は未定。", source:"固定環境と部品ライブラリの評価", href:"../docs/native-kicad-authoring-feasibility.md" },
    { title:"評価が続き、製品開発へ進めない可能性", basis:"過去の複数評価後も実物基板の設計経路は未認定。0.750時間はAI作業時間の推定で、技術者の実測時間ではない。", impact:"評価に時間を使い続けても、実物Rev.M1の設計・製造・測定に進めないおそれがあります。", proof:"続行・保留・方向見直しの判断と、必要な投資・担当・製品工程への移行条件。", handling:"発生率や残工数は不明。新しい対策・予算は未承認。", owner:"PMOが案と材料を整理し、POが判断。技術担当未定。", source:"docs/eda-path-history.md · 評価時間の報告書", href:"../docs/eda-path-history.md" }
  ],
  decision: {
    status:"既存方針を維持 · 次の実験は未承認",
    question:"既存条件とD-018の限定計画を踏まえ、次の実験を計画するか、保留するか、方針を見直すか。",
    evidence:"直近の停止報告に加え、Mainへ適用できる証拠、正しい接続と間隔の両立、間隔設定の実効性、製造データと再生成、維持負担が不足。PMOが対象・方法・担当案・個別受入条件・投資範囲を整理します。",
    owner:"案と技術材料の整理: PMO。実施するかの判断: PO。実施担当は未定。",
    planStatus:"D-018の過去の限定計画と基板条件は記録済みです。EDA-004E後の実験対象・方法・担当・個別受入条件は未承認。実施には別IssueとPO指示が必要です。",
    proposal:"具体的な次の実験をこのPRで選定・承認しません。"
  },
  history: [
    { name: "初期KiCad", tested: "旧4キー回路図とPCBの修正・CI検査", stopped: "繰り返したファイル形式修正の記録があり、PR #10 CIのPCB DRCは587違反・未接続40件。個々の原因とwriterは不明。", reuse: "既存シンボル・footprint・要求を検証済み参照として再利用。", retry: "異なる保存/検証方式と、現在の電気・形状の証拠が必要。", refs: "PR #6 / #10、D-014、Issue #79", href: "https://github.com/ihsinoky/he-piantor-42/pull/10" },
    { name: "JITX", tested: "部品モデル、電気的整合、headless物理・後工程", stopped: "PO判断D-016でRev.M1/Rev.Aの物理backendはNO-GO。完全な対応済みheadless多層配線は実証されず。", reuse: "受入済みの部品・電気・DFM・後工程の知見。", retry: "対応済みの完全配線手順と、投資・保守範囲の別途承認が必要。", refs: "D-016、Issue #55、C4B5", href: "../docs/eda-path-history.md" },
    { name: "stock tscircuit", tested: "native stock物理配線とMainのclearance介入", stopped: "評価した内部router探索は終了。介入A/Bで誤配線回帰があり、backendは未採用。", reuse: "native electrical source、固定モデル、独立物理検証。", retry: "対応済み機構で接続性と0.20 mm間隔を同時に示す必要。", refs: "D-018、Issue #61–#71、EDA-003B–F", href: "../docs/eda-path-history.md" },
    { name: "Circuit JSON → KiCad", tested: "bounded converter repairと小規模/Main前段の検査", stopped: "別々の試行でGND landのnet欠落/short、footprint library ID衝突、schematic ERC未成立。配線試行なし。", reuse: "raw fixture、固定環境、capture手順と限られたcheckerの知見。", retry: "正確なfootprint identityと接続済みschematic/ERC等の条件が必要。", refs: "EDA-004B–D、Issue #73 / #75 / #77、PR #76 / #78", href: "../docs/eda-path-history.md" },
    { name: "native KiCad objects", tested: "KiCad 9.0.9の固定小規模基板を作成・保存し、別のプログラム実行で開き直し", stopped: "初回DRCに予期しない警告2件。回路図経路がなく、Mainへ進む前にSTOP。", reuse: "試験対象内で確認した基板データの保存・再読込と形状・接続情報の保持。", retry: "PO/PMOが具体的な回路図経路を承認し、限定した修正・実効ルール試験・条件付き再評価を許可した場合のみ。", refs: "EDA-004E、Issue #79、PR #80、D-014", href: "../docs/native-kicad-authoring-feasibility.md" }
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
    {name:"Hardware",cells:["設計方針 完了","成立確認中: 小規模試験基板の保存・再読込で対象情報の保持を確認。初回検査受入未達、実物Mainは未認定。","Main再利用 + Left/Right Wings","統合改版","製造版"]},
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
    {name:"G0A JITX Backend Adoption",status:"done",check:"C0-C3 accepted evidence + historical C4B-C4B4A + C4B4B external disposition + C4B5 routing BLOCKED evidence",trigger:"Completed PO decision, issue #55 / D-016: JITX physical backend NO-GO for Rev.M1 / Rev.A; C4B5 complete-routing workflow not demonstrated",unlocks:"Historical JITX NO-GO remains. D-018 accepted planning scope only; later EDA-004B–E evaluations did not qualify a product method or authorize implementation."},
    {name:"G0B Rev.M1 Architecture / Interface Freeze",status:"done",check:"D-017: exact JST GH 14-position connector/pinout, six common-GND returns, external WING_EN pull-down, nominal 100 mm 1:1 harness, pitch Wings/full-load three-TMUX-three-ADC coverage, test access, measurement framework, DFM",trigger:"Issue #57 PO GO accepted the freeze",unlocks:"Accepted interface and architecture remain frozen. Later method evaluations did not qualify the product path; full implementation is not authorized."},
    {name:"G1 Rev.M1 Main + Evaluation Wing pre-order review",status:"not-ready",check:"Main/Wing circuit/ERC, DRC, BOM, actual manufacturing outputs, measurement plan",trigger:"manufacturing package complete after separately accepted backend qualification and authorized full Rev.M1 implementation",unlocks:"Rev.M1 Main + Evaluation Wing order"},
    {name:"G2 post-EVT-002 magnetic / pitch / analog-path decision",status:"not-ready",check:"range, noise, scan speed, power, interference, interconnect, 17.0/16.5/16.0 mm usability",trigger:"physical measurements/report complete",unlocks:"production pitch and magnetic architecture / Rev.A circuit freeze"},
    {name:"G3 Rev.A 発注前確認",status:"not-ready",check:"Main/Left/Right DRC, BOM, Gerber, drill/PnP, cost",trigger:"42-key manufacturing package complete",unlocks:"Rev.A PCBA order"},
    {name:"G4 実機操作確認",status:"not-ready",check:"打鍵、校正、Vial、USB、筐体適合",trigger:"統合機のbring-up完了時",unlocks:"完成版の固定"},
    {name:"G5 最終版承認",status:"not-ready",check:"v1.0の全製造物と手順",trigger:"受入試験合格時",unlocks:"v1.0リリース"}
  ],
  risks: [
    {kind:"risk",title:"USB product manufacturing release",detail:"OPEN — PRE-ORDER DFM REVIEW REQUIRED for Rev.M1 / Rev.A. All four nominal gaps meet JLCPCB 0.20 mm capability floor, not production approval. 0.25 mm preferred target and 0.001 mm numerical review guard are project-owned, not JLCPCB requirements or recommendations. Any manufacturing disposition remains a separate gate; no production exception granted.",owner:"G1 / PO review; implementation owner unassigned",source:"Rev.M1 DFM policy",href:"../hardware/rev-m1/dfm-policy.md"},
    {kind:"risk",title:"Historical JITX downstream thickness handoff",detail:"Retained JITX path evidence/limitation, not the primary NO-GO reason. PASS_WITH_LIMITATIONS: generated CAD/Gerber-job overall thickness metadata is misleading (1.6 mm); independently confirm 1.2 mm if this historical handoff is reused.",owner:"Only if historical JITX handoff is reconsidered",source:"EDA-002C4B4B report",href:"../hardware/jitx/physical/EDA-002C4B4B.md"},
    {kind:"risk",title:"pitch / キーキャップ干渉",detail:"17.0 / 16.5 / 16.0 mmで使用感・磁気・switch/keycap干渉を比較。100 x 100 mmはcost targetのみ。",owner:"M1 measurement owner unassigned; G2 PO decision",source:"Rev.M1 evaluation plan",href:"../hardware/rev-m1/evaluation-plan.md"},
    {kind:"risk",title:"磁束レンジと個体差",detail:"Main + Evaluation Wingでスイッチ・センサ・距離・interconnectを一組として実測する。",owner:"M1 measurement owner unassigned; G2 PO decision",source:"Rev.M1 evaluation plan",href:"../hardware/rev-m1/evaluation-plan.md"},
    {kind:"risk",title:"42センサの電力",detail:"Accepted DRV5055 at 5 V: 3 mA typical / 5 mA maximum; approximately 127 mA per 21-key Wing / 254 mA for 42 sensors-two Wings. Planning estimates only; final USB/system power budget, other loads and startup/inrush qualification remain open.",owner:"Technical owner unassigned; PO decides G2",source:"Rev.M1 main/Wing interface",href:"../hardware/rev-m1/main-wing-interface.md"},
    {kind:"risk",title:"中央部のねじり荷重",detail:"Main/Wingの接続・固定と筐体補強は後続mechanical gateで検証する。",owner:"Mechanical owner unassigned",source:"Rev.M1 architecture",href:"../hardware/rev-m1/architecture.md"},
    {kind:"risk",title:"JITX RuntimeDesign stability",detail:"EDA-002C0 is accepted PASS for the challenger/parity workflow. RuntimeDesign query and net-resolution methods remain documented but explicitly experimental; this is not current-candidate evidence.",owner:"Only if JITX is reconsidered",source:"JITX evaluation",href:"../docs/jitx-evaluation.md"},
    {kind:"risk",title:"KiCad importer reuse",detail:"EDA-003A accepted UPSTREAM_FIX_CANDIDATE. Both copper-pour keepouts silently lost without material-loss warnings; rounded-pad corner radius incorrect. Reuse NOT approved; native TSX authoritative at that earlier decision.",owner:"Only if importer reuse is reconsidered",source:"Importer requalification report",href:"../docs/tscircuit-kicad-importer-requalification.md"},
    {kind:"risk",title:"Historical alternate-method evaluation",detail:"EDA-004B through EDA-004E are completed reports with different targets and results. Their CI, partial checks, or historical success do not qualify the current Rev.M1 design path.",owner:"Historical context; current planning owner is PO",source:"EDA path history",href:"../docs/eda-path-history.md"}
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
    ["EDA-004E","EDA","Native KiCad authoring feasibility and history","done","Codex","#79 / PR #80: 固定小規模試験基板の保存・再読込で確認対象の形状と接続情報の保持を確認。初回受入は予期しないDRC警告2件で不成立。実物Main・配線・製造・再生成は未認定。"],
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
