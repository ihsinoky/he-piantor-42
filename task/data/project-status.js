// Non-authoritative Dashboard read model. See docs/governance.md.
window.PROJECT_STATUS = {
  schemaVersion: 2,
  source: {
    "confirmedAt": "2026-10-14T22:23:18.672066Z",
    "reference": "Issue87限定再開/利用制限復旧のSTOP提案、Draft PR88。productionはmerged main。",
    "statusUrl": "https://github.com/ihsinoky/he-piantor-42/pull/88",
    "reportUrl": "../docs/issue-87-native-main-routing.md#resume-01",
    "historyUrl": "../docs/eda-path-history.md"
  },
  current: {
    "heading": "実物Rev.M1の設計前",
    "location": "DSN復元・個別入力・小規模往復が限定成立。Main初回は未完了で実効pass契約も未認定。利用制限は技術結果と分離。",
    "blocker": "Main35未接続はrouter値、物理4指標未測定。実512passes vs宣言100。追加試行なし。"
  },
  nextAction: {
    "status": "Main未完了/実行契約のSTOPレビュー",
    "owner": "PMO: ChatGPT、判断: PO",
    "action": "限定DSN/small成功を残し、未完了Main・実効pass上限・時間境界をレビュー。POが次投資か保留を判断。",
    "target": "Issue87 Main初回未認定結果と次の投資範囲",
    "startCondition": "次対象/方法/担当/独立受入/投資の別途承認。利用枠resetは試行・時間・scope拡張でない。"
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
      status:"Issue87限定再開: Main未完了/実効契約未認定・レビュー待ち",
      purpose:"実物基板の設計データを作り、接続・配線・間隔・製造出力を確かめ、同じ条件で再現できる方法を成立させる。",
      output:"回路・基板データと、接続・配線・間隔・製造出力・再生成の確認記録。",
      completion:"DSN typed.05→.20だけ復元、独立diff/実効行列/個別Main照合と小規模1が成立。Main初回1未完了、実512 vs100passes、確認0。Main4物理指標null。",
      owner:"Issue #87実装・評価: Codex。PMO: ChatGPT。記録受入と次範囲/投資判断: PO。次実施担当は未定。",
      establishedSummary:"2層・厚さ1.2 mm・配線間隔0.20 mmを維持。D-018はMain先行・初回Main評価の技術作業上限2人日を定めた限定計画で、次の実験許可ではありません。",
      establishedDetail:"D-015/D-017: 2層・1.2 mmの基板基準。D-018: 0.20 mmの材料間隔、Main合格後にWing/出力へ進む順序、初回Main配線1回と初回合格時のみ新規確認1回、初回Main評価の技術作業上限2人日。候補Bの限定計画に対する条件で、他候補や次回実験へ自動適用・実施許可しません。候補Bは優先された評価候補であり、採用済み方式ではありません。EDA-004B〜Eは過去の報告。EDA-004FはPR #84で小規模結果を受入。resume01の独立期待表不一致STOPは保持。resume02 fresh Main/ERC/DRCはPOが明示した最大1時間の保存証拠再照合範囲を超過。別途許可は確認できず、PO-authorized表記を撤回。初回STOP・過去結果と予算不明を維持し、過去許可は継承しません。PR #86は受入済み過去STOP。Issue #87と現在PO指示だけが、新6hと既知印刷61件/glyphの配線停止条件からの分離を許可。初回工程C STOP後、POが限定typed修正と利用制限復旧を別途許可。最新結果はMain未完了/実効pass契約未認定STOPで、追加試験権限はありません。",
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
    "id": "ISSUE-87",
    "title": "Issue87限定再開：DSN修正・小規模成立、Main未完了",
    "purpose": "印刷課題を製造前事項として残し、固定0.20mm条件でMainを安全に自動配線できるか評価。",
    "issue": {
      "id": "87",
      "url": "https://github.com/ihsinoky/he-piantor-42/issues/87"
    },
    "acceptedRecord": {
      "id": "88",
      "url": "https://github.com/ihsinoky/he-piantor-42/pull/88",
      "status": "Draft STOP報告・未受入。PR86過去STOP受入済み。"
    },
    "workStatus": "利用制限から既存実行を読み取り復旧。技術STOP記録・同じDraft PR88へ提出。",
    "technicalStatus": "ROUTING_BLOCKED / MAIN_OUTPUT_INCOMPLETE / RUN_CONTRACT_UNQUALIFIED / MAIN_UNQUALIFIED",
    "currentSummary": "typed.05→.20mmだけ復元、独立diff/実効行列/個別Main DSN照合成立。小規模1は4指標0。Main初回1はrouter35未接続、実行512passes vs宣言100。確認0、Main4物理指標null。",
    "currentProblem": {
      "title": "Main未完了・実効pass上限未認定",
      "basis": "既存wrapperはexit0/SES保存。最終router35未接続。宣言100passesに対し実ログ512。",
      "impact": "Main未認定。固定100pass条件の有効な配線結果でもない。",
      "proof": "実効実行条件と、必要物理端子/実銅箔/材料/戻しの独立照合。",
      "handling": "最新PO復旧指示CによりSTOP。追加配線/途中再開/新規Main取込検査/確認なし。",
      "owner": "PMO: ChatGPT、次範囲/投資/merge判断: PO。次担当未定。",
      "source": "Issue87 resume01/recovery evidence",
      "href": "../docs/issue-87-native-main-routing.md#resume-01"
    },
    "learned": "限定DSN復元と公開headless読込の実効条件・個別形状照合、小規模往復が成立。公開設定parser100はruntime上限の証明でなかった。",
    "unknown": "Main戻しの4物理指標/完全配線/確認、512passへ進んだ厳密原因、全環境資格と利用制限待ち境界。",
    "impact": "方式採用/製品/製造/Human Gateなし。固定配置や方式全体の不成立と一般化しない。",
    "nextCondition": "PMO/POが不完全Mainと実行契約をレビューし、次の範囲/方法/担当/受入/投資を別途判断。",
    "testedQuestion": "限定DSN修正は要求を保ち、固定Mainの1回の実行は条件を満たすか。",
    "evidenceBoundary": "DSN入力と小規模のみ限定成立。Main incomplete/契約未認定。exit0・SES存在・router clearance0は技術合格でない。",
    "coverage": [
      {
        "stepId": "circuit",
        "result": "限定成立・再利用",
        "detail": "既存hash/個別対応とERC0を再利用。"
      },
      {
        "stepId": "board",
        "result": "入力照合成立",
        "detail": "197物理pad/NC/重複/穴障害物/層/外形/USB局所銅箔を個別DSN/公開読込で確認。"
      },
      {
        "stepId": "route",
        "result": "小規模成立・Main未完了",
        "detail": "小規模1/Main初回1/確認0。Main最終router35、実512 vs宣言100。"
      },
      {
        "stepId": "verify",
        "result": "小規模限定成立・Main未測定",
        "detail": "小規模4指標0。復旧CのSTOPでMain新規取込/DRC/graphなし、Main4指標null。"
      },
      {
        "stepId": "manufacture",
        "result": "対象外",
        "detail": "baseline印刷61/glyph/USB DFM未解決。製造・Wing・例外なし。"
      },
      {
        "stepId": "reproduce",
        "result": "未実施",
        "detail": "Main初回全条件合格なし。新規生成/確認は0。"
      }
    ],
    "evidence": [
      {
        "label": "DSNルール復元・実効条件",
        "result": "限定成立",
        "detail": "各1数値のみ、独立AST/byte diff、両層matrix.20mm。"
      },
      {
        "label": "Main個別DSN入力",
        "result": "限定成立",
        "detail": "接続/NC/重複/形状/配置/層/穴障害物/局所銅箔一致。native保持情報とDSN非表現情報を区別。"
      },
      {
        "label": "小規模往復1回",
        "result": "成功（fixture限定）",
        "detail": "native nonroute保持、KiCad DRC/未接続0、独立graph4指標0。"
      },
      {
        "label": "Main初回1回",
        "result": "未完了・契約未認定",
        "detail": "exit0、SES保存、router35。100上限に対し512。Main物理検査未測定・確認0。"
      },
      {
        "label": "利用制限と時間",
        "result": "境界不確かさ保持",
        "detail": "無人router加算。待ち候補39m52sの下限/上限を記録し、上限で6hを管理。"
      }
    ]
  },
  uncertainties: [
    {
      "title": "Main未完了・実効pass上限未認定",
      "basis": "既存wrapperはexit0/SES保存。最終router35未接続。宣言100passesに対し実ログ512。",
      "impact": "Main未認定。固定100pass条件の有効な配線結果でもない。",
      "proof": "実効実行条件と、必要物理端子/実銅箔/材料/戻しの独立照合。",
      "handling": "最新PO復旧指示CによりSTOP。追加配線/途中再開/新規Main取込検査/確認なし。",
      "owner": "PMO: ChatGPT、次範囲/投資/merge判断: PO。次担当未定。",
      "source": "Issue87 resume01/recovery evidence",
      "href": "../docs/issue-87-native-main-routing.md#resume-01"
    },
    {
      "title": "Main物理/戻し未認定",
      "basis": "最終router35 incomplete、caseC STOPでMain SES取込/DRC/graphは未実施。",
      "impact": "物理未接続/異net/材料/戻し差分はnull。",
      "proof": "4物理指標と実効実行契約の別途証拠。",
      "handling": "未測定を0にしない。追加実験なし。",
      "owner": "PMO/PO",
      "source": "Issue87 latest report",
      "href": "../docs/issue-87-native-main-routing.md#resume-01"
    },
    {
      "title": "印刷・製品・環境",
      "basis": "baseline印刷61/glyphとUSB DFM未解決。Main戻しDRC未実施、全環境再構築未認定。",
      "impact": "製造/採用/製品着手は未承認。",
      "proof": "別途製造前の実物条件確認。",
      "handling": "印刷保持、抑制/例外/材料緩和なし。",
      "owner": "PO、次製品担当未定",
      "source": "retained product risks",
      "href": "../docs/issue-87-native-main-routing.md#resume-01"
    },
    {
      "title": "利用制限・予算境界",
      "basis": "prior13min継承。無人routerを加算、待ち候補39m52sを下限/上限で区別。",
      "impact": "正確な活動境界と過去予算は未認定。",
      "proof": "新ledger/PR終了観測。",
      "handling": "保守的上限で6h管理、最後30分確保。resetによる自動延長なし。",
      "owner": "PO/PMO",
      "source": "resume01 effort ledger",
      "href": "../docs/issue-87-native-main-routing.md#resume-01"
    }
  ],
  decision: {
    "status": "同じDraft PR88でSTOPレビュー待ち",
    "question": "限定成功とMain未完了/契約逸脱を受け入れ、次投資か保留をどう判断するか。",
    "evidence": "DSN/small限定成立。Main最終router35、実512 vs100、物理指標null。",
    "owner": "PMOが材料整理、POが判断。",
    "planStatus": "新試行/確認/実効pass補正の対象/方法/担当/受入/予算は未計画。",
    "proposal": "本報告は再試行・別設定・採用・製品設計・製造例外を許可しない。"
  },
  history: [
    {"name": "Issue87 limited resume / utilization recovery", "tested": "typed間隔復元・実効行列・個別DSN・小規模1・Main初回1", "stopped": "Main incomplete35はrouter値、512passes vs100。復旧caseC STOP、Main物理4指標null、確認0。", "reuse": "DSN/small限定成立と過去gap/via証拠。原STOP/失敗は保持。", "retry": "PMO/POが実効契約と次投資を別途判断。自動追加試行なし。", "refs": "Issue87 / same Draft PR88", "href": "../docs/issue-87-native-main-routing.md#resume-01"},
    {"name": "Issue #87 fixed native Main", "tested": "保存Main再利用・新ERC/DRC・実効gap/実PCB via負例・公開DSN", "stopped": "工程C:small/Main DSNがtyped smd_smd.05mm。Main0/0、小規模往復0、export2。", "reuse": "固定入力、.10mm gap検出、実PCB via/欠落/short検出。完全受け渡し/配線は未認定。", "retry": "新しい限定修正/証明の範囲と投資をPOが別途決定。", "refs": "Issue #87（STOP提案）", "href": "../docs/issue-87-native-main-routing.md"},
    { name: "初期KiCad", tested: "旧4キー回路図とPCBの修正・CI検査", stopped: "繰り返したファイル形式修正の記録があり、PR #10 CIのPCB DRCは587違反・未接続40件。個々の原因とwriterは不明。", reuse: "既存シンボル・footprint・要求を検証済み参照として再利用。", retry: "異なる保存/検証方式と、現在の電気・形状の証拠が必要。", refs: "PR #6 / #10、D-014、Issue #79", href: "https://github.com/ihsinoky/he-piantor-42/pull/10" },
    { name: "JITX", tested: "部品モデル、電気的整合、headless物理・後工程", stopped: "PO判断D-016でRev.M1/Rev.Aの物理backendはNO-GO。完全な対応済みheadless多層配線は実証されず。", reuse: "受入済みの部品・電気・DFM・後工程の知見。", retry: "対応済みの完全配線手順と、投資・保守範囲の別途承認が必要。", refs: "D-016、Issue #55、C4B5", href: "../docs/eda-path-history.md" },
    { name: "stock tscircuit", tested: "native stock物理配線とMainのclearance介入", stopped: "評価した内部router探索は終了。介入A/Bで誤配線回帰があり、backendは未採用。", reuse: "native electrical source、固定モデル、独立物理検証。", retry: "対応済み機構で接続性と0.20 mm間隔を同時に示す必要。", refs: "D-018、Issue #61–#71、EDA-003B–F", href: "../docs/eda-path-history.md" },
    { name: "Circuit JSON → KiCad", tested: "bounded converter repairと小規模/Main前段の検査", stopped: "別々の試行でGND landのnet欠落/short、footprint library ID衝突、schematic ERC未成立。配線試行なし。", reuse: "raw fixture、固定環境、capture手順と限られたcheckerの知見。", retry: "正確なfootprint identityと接続済みschematic/ERC等の条件が必要。", refs: "EDA-004B–D、Issue #73 / #75 / #77、PR #76 / #78", href: "../docs/eda-path-history.md" },
    { name: "native KiCad objects", tested: "KiCad 9.0.9の固定小規模基板を作成・保存し、別のプログラム実行で開き直し", stopped: "初回DRCに予期しない警告2件。回路図経路がなく、Mainへ進む前にSTOP。", reuse: "試験対象内で確認した基板データの保存・再読込と形状・接続情報の保持。", retry: "PO/PMOが具体的な回路図経路を承認し、限定した修正・実効ルール試験・条件付き再評価を許可した場合のみ。", refs: "EDA-004E、Issue #79、PR #80、D-014", href: "../docs/native-kicad-authoring-feasibility.md" },
    { name:"external kicad-sch-api", tested:"固定KiCad 9.0.9で小規模回路図作成・検査", stopped:"停止条件なし、限定試験完了。初回受入は設定警告6件で失敗、同一ファイル設定修正後に候補成立。", reuse:"独立端子表、公開API生成、固定CLI検査とfault検出。", retry:"Main以降は別途計画・PO許可が必要。", refs:"EDA-004F / Issue #83 / merged PR #84（受入済み）", href:"../docs/headless-schematic-qualification.md" },
    { name:"public native Main prerequisite", tested:"固定Main入力・4限定symbol対応・fresh native形状・Main生成/raw検査", stopped:"resume02のfresh Main/ERC/DRCは指示範囲超過。技術結果はERC0/個別照合成立、印刷警告61件によるPRE_ROUTE_PHYSICAL_DRC_STOP。実効間隔/受け渡し/配線未実施、0/0/0。", reuse:"入力hashと部分対応表、版・公開pin表観察。完全Mainへ結果を一般化しない。", retry:"PR #86受入済み。Issue #87は別途新規許可され、そのSTOPは最新評価に分離。", refs:"EDA-004G / Issue #85 / merged PR #86（過去STOP受入）", href:"../docs/native-main-routing-qualification.md" }
  ],
  evidenceLinks: {
    "latestReport": "../docs/issue-87-native-main-routing.md#resume-01",
    "pathHistory": "../docs/eda-path-history.md",
    "githubActions": "https://github.com/ihsinoky/he-piantor-42/actions",
    "issue79": "https://github.com/ihsinoky/he-piantor-42/issues/79",
    "pr80": "https://github.com/ihsinoky/he-piantor-42/pull/80",
    "issue83": "https://github.com/ihsinoky/he-piantor-42/issues/83",
    "pr84": "https://github.com/ihsinoky/he-piantor-42/pull/84",
    "issue85": "https://github.com/ihsinoky/he-piantor-42/issues/85",
    "issue87": "https://github.com/ihsinoky/he-piantor-42/issues/87"
  },
  milestones: [
    {id:"M0",name:"設計方針・基本形状",status:"done",deliverable:"過去の42キー要件・17 mm配置・取得方針（D-015でpitch再評価）",exit:"主要要件・キー中心座標・評価方針が文書化済み"},
    {id:"M1",name:"磁気方式・評価基板",status:"current",deliverable:"再利用Main + pitch/磁気Evaluation Wing(s)、計測FW、実測レポート（hardware未実装）",exit:"ERC/DRC合格、実測で磁気・pitch・analog pathをG2判断"},
    {id:"M2",name:"42キー Rev.A",status:"next",deliverable:"accepted Main再利用 + Left 21-key Wing + Right 21-key Wing + production FW（G2判断後）",exit:"Main/Wing ERC/DRC・製造性検査とFW buildが合格"},
    {id:"M3",name:"統合・筐体・試験",status:"todo",deliverable:"筐体、統合機、組立・校正・試験手順",exit:"実機操作、全キー校正、USB、Vial、筐体適合の試験に合格"},
    {id:"M4",name:"完成版リリース",status:"todo",deliverable:"再現可能なv1.0製造・FW・筐体パッケージ",exit:"最終成果物を固定しユーザーが完成版を承認"}
  ],
  streams: [
    {
      "name": "Hardware",
      "cells": [
        "設計方針 完了",
        "Issue87再開: DSN修正/実効行列/個別入力と小規模1成立。Main初回1未完了、実512 vs100、確認0。Main物理指標null。印刷61は製造前事項。",
        "Main再利用 + Left/Right Wings",
        "統合改版",
        "製造版"
      ]
    },
    {
      "name": "Firmware",
      "cells": [
        "要件 完了",
        "計測FW",
        "Hall + Vial",
        "統合・校正",
        "v1.0"
      ]
    },
    {
      "name": "Enclosure / Mechanical",
      "cells": [
        "形状条件 完了",
        "PCB条件待ち",
        "外形連携",
        "STEP / STL",
        "製造版"
      ]
    },
    {
      "name": "Verification / Test",
      "cells": [
        "計画 完了",
        "磁気・電力実測",
        "Rev.A bring-up",
        "統合試験",
        "受入試験"
      ]
    }
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
    ["EDA-004F","EDA","Headless小規模回路図作成・検査","done","Codex","#83 / merged PR #84受入記録: SMALL_SCHEMATIC_CANDIDATE_PASS。初回受入FAIL、設定修正後全個別試験成立。Main/PCB/製造未実施。"],
    ["EDA-004G","EDA","代表Mainの公開モデル・整合・headless配線限定評価","done","Codex","#85/PR #86再開STOP: 4限定symbol対応、Main生成/raw ERC0 errors。新規raw役割/ERC0/core照合成立、印刷DRC61件で完全受入STOP。配線0/0/transport0、配線指標null。"],
    ["EVT-002","EVT","Rev.M1 Main + Evaluation Wing physical implementation","hold","Codex","製品Main実装未承認。EDA-004G再開STOP報告のPMO/POレビュー待ち。詳細: ../docs/native-main-routing-qualification.md"],
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
