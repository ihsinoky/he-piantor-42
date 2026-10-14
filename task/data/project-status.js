// Non-authoritative Dashboard read model. See docs/governance.md.
window.PROJECT_STATUS = {
  schemaVersion: 2,
  source: {
    "confirmedAt": "2026-10-14T13:40:11Z",
    "reference": "Issue #85 resume02 印刷DRC STOP（PR #86未受入。productionはmerged main）",
    "statusUrl": "https://github.com/ihsinoky/he-piantor-42/pull/86",
    "reportUrl": "../docs/native-main-routing-qualification.md",
    "historyUrl": "../docs/eda-path-history.md"
  },
  current: {
    "heading": "実物Rev.M1の設計前",
    "location": "実物Rev.M1設計前。EDA-004G resume02は4モデル・生定義役割・ERC0・core PCB照合が成立、印刷DRC61件で停止。EDA-004FはPR #84受入済み。",
    "blocker": "完全な印刷形状/物理受入・実効0.20 mm・DSN/SES・Main配線は未認定。"
  },
  nextAction: {
    "status": "resume02 印刷DRC/形状・時間記録をレビュー・追加実験は未承認",
    "owner": "PMO/reviewer: ChatGPT、判断: PO（ユーザー）",
    "action": "PMOが61印刷違反、glyph同等性と物理受入の範囲、残る検査と時間計上をレビュー。POが記録受入・投資・次の権限を判断。",
    "target": "EDA-004G resume02の物理DRC STOPと未認定範囲",
    "startCondition": "停止後の追加実験は未承認。次対象・方法・担当・個別受入条件・投資範囲は未計画で、別途POの実施権限が必要。"
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
      status:"resume02物理DRC STOP・報告レビュー待ち",
      purpose:"実物基板の設計データを作り、接続・配線・間隔・製造出力を確かめ、同じ条件で再現できる方法を成立させる。",
      output:"回路・基板データと、接続・配線・間隔・製造出力・再生成の確認記録。",
      completion:"4部品/193生定義役割、ERC0、core197pads/2holes/USB実銅箔、4synthetic負例が限定成立。印刷61違反で工程2受入停止。実効ルール/工程3〜5は未実施、配線0/0/0。",
      owner:"今回の実装・評価: Codex。PMO/reviewer: ChatGPT。記録受入と次回実施判断: PO。次回実施担当は未定。",
      establishedSummary:"2層・厚さ1.2 mm・配線間隔0.20 mmを維持。D-018はMain先行・初回Main評価の技術作業上限2人日を定めた限定計画で、次の実験許可ではありません。",
      establishedDetail:"D-015/D-017: 2層・1.2 mmの基板基準。D-018: 0.20 mmの材料間隔、Main合格後にWing/出力へ進む順序、初回Main配線1回と初回合格時のみ新規確認1回、初回Main評価の技術作業上限2人日。候補Bの限定計画に対する条件で、他候補や次回実験へ自動適用・実施許可しません。候補Bは優先された評価候補であり、採用済み方式ではありません。EDA-004B〜Eは過去の報告。EDA-004FはPR #84で小規模結果を受入。Issue #85の6時間枠内でPOが限定対応再開を承認。独立期待表不一致で再停止。初回STOP・過去結果と予算を維持し、過去許可は継承しません。",
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
    "id": "EDA-004G",
    "title": "代表Mainのモデル・回路図・PCB整合とheadless配線の前提を確認する",
    "purpose": "固定Mainを公開回路図/PCB経路で忠実に作成し、成立後に正しい接続と0.20 mm間隔の配線を限定評価。",
    "issue": {
      "id": "85",
      "url": "https://github.com/ihsinoky/he-piantor-42/issues/85"
    },
    "acceptedRecord": {
      "id": "86",
      "url": "https://github.com/ihsinoky/he-piantor-42/pull/86",
      "status": "Draft PR提案・未受入"
    },
    "workStatus": "resume02限定検証と新規Main生成・印刷DRCで停止、証拠報告提出",
    "technicalStatus": "PRE_ROUTE_PHYSICAL_DRC_STOP / MAIN_UNQUALIFIED。4モデルと新規raw役割/ERC0/core PCB照合は成立。61印刷違反とglyph未認定で完全物理受入停止。旧STOP/凍結表は失敗のまま保持。方式全体不成立・大規模実装必須の証明ではない。",
    "currentSummary": "新規v2を生成前固定。49部品・37nets・193論理pins・197物理pads（167必要/30NC）・2NPTHを個別確認、USB4lands実銅箔接続、557補助primitiveパラメータ一致。ERC0。印刷高さ44/重なり12/銅箔上5でSTOP、route0/0/0。",
    "currentProblem": {
      "title": "Mainの印刷形状・物理DRC受入が未成立",
      "basis": "新規最終PCBに61印刷DRC違反。例:source高さ0.4000mm vs active最小0.8000mm。native KiCad glyphとsource tscircuit2024の形状同等性は未認定。",
      "impact": "完全物理受入前に停止、実効0.20 mm/DSN/SES/Main配線へ進めない。回路変換・4モデル不成立の意味ではない。",
      "proof": "印刷・glyph・物理条件の範囲と忠実性、違反の正当な扱い。実効ルール/受け渡し/実銅箔配線は別の未確認事項。",
      "handling": "61件をwarning/既存という理由で除外しない。検査抑制・文字サイズ/形状変更・追加試験なし。PMO/POレビューに戻す。",
      "owner": "PMO/reviewer: ChatGPT、PO: ユーザー。次回技術担当未定。",
      "source": "docs/native-main-routing-qualification.md",
      "href": "../docs/native-main-routing-qualification.md"
    },
    "learned": "公開pretty-print/明示footprint I/Oでライブラリ警告を解消しERC0。raw inherited pinsで旧cache fallbackを回避。4負例とUSB同番号landの実銅箔を確認。",
    "unknown": "完全glyph形状/印刷条件、実効0.20 mm、DSN/SES、routed-via/spacing、初回・確認、全環境資格。",
    "impact": "Main成立・製品設計・方式採用・Human Gateは認定/承認されていません。",
    "nextCondition": "PMO/POが印刷/物理条件・検査・投資をレビューし次の範囲/権限を判断。停止後の追加試験は推論で開始しない。",
    "testedQuestion": "受入済み小規模経路と限定した対応で、Main全端子を忠実に表せるか。",
    "evidenceBoundary": "新規193roles/ERC0、core geometry/実局所銅箔と4synthetic負例、557補助primitiveパラメータ。glyph/完全物理受入は未認定、印刷DRC61件で停止。",
    "coverage": [
      {
        "stepId": "circuit",
        "result": "限定成立",
        "detail": "新規v2の193raw typed pins/net/NC照合、ERC0 violations。旧v1期待表FAILは保持。"
      },
      {
        "stepId": "board",
        "result": "core成立・完全受入STOP",
        "detail": "197pads/2holes/pose/layer/outline/USB実銅箔と557補助primitiveパラメータ照合。glyph未認定、61印刷違反。"
      },
      {
        "stepId": "route",
        "result": "成功（synthetic限定）",
        "detail": "Main初回/確認0/0、小規模受け渡し0。"
      },
      {
        "stepId": "verify",
        "result": "未認定",
        "detail": "4synthetic faults検出。実効ルール/DSNSES/配線検査は未実施。0 target baselineだけで合格にしない。"
      },
      {
        "stepId": "manufacture",
        "result": "成功（synthetic限定）",
        "detail": "対象外。Wing・製造を開始していません。"
      },
      {
        "stepId": "reproduce",
        "result": "未認定",
        "detail": "初回合格なし、条件付き確認未実施。初回環境再準備は全環境再構築確認ではありません。"
      }
    ],
    "evidence": [
      {
        "label": "不変入力と現在mainのhash",
        "result": "成功",
        "detail": "5ファイルを個別照合。source/production依存は不変。"
      },
      {
        "label": "独立したMain期待表",
        "result": "新規v2確認・旧v1失敗保持",
        "detail": "生成前に193生定義roleとsource shape/NC対応を新規固定。old cache fallback失敗を事後修復しない。"
      },
      {
        "label": "4部品の限定公開追加",
        "result": "成功（限定範囲）",
        "detail": "4定義を再照合/公開登録。旧default footprint不採用。AP raw NC pin4とphysical NPTH enumを新規ターゲットで正しく照合。"
      },
      {
        "label": "Mainの4種の誤り検出",
        "result": "成功（synthetic限定）",
        "detail": "実銅箔短絡・必要pad欠落・同番号shield分離・material設定欠落を意図した理由で検出。実効DRC注入とは別。"
      },
      {
        "label": "Main生成と配線・確認",
        "result": "新規生成/core照合成立・印刷STOP",
        "detail": "最終PCB印刷DRC61件。rule注入/DSNSES/初回・確認未実施、routes0/0/0、配線metrics null。"
      }
    ]
  },
  uncertainties: [
    {
      "title": "Mainの印刷形状・物理DRC受入が未成立",
      "basis": "新規最終PCBに61印刷DRC違反。例:source高さ0.4000mm vs active最小0.8000mm。native KiCad glyphとsource tscircuit2024の形状同等性は未認定。",
      "impact": "完全物理受入前に停止、実効0.20 mm/DSN/SES/Main配線へ進めない。回路変換・4モデル不成立の意味ではない。",
      "proof": "印刷・glyph・物理条件の範囲と忠実性、違反の正当な扱い。実効ルール/受け渡し/実銅箔配線は別の未確認事項。",
      "handling": "61件をwarning/既存という理由で除外しない。検査抑制・文字サイズ/形状変更・追加試験なし。PMO/POレビューに戻す。",
      "owner": "PMO/reviewer: ChatGPT、PO: ユーザー。次回技術担当未定。",
      "source": "docs/native-main-routing-qualification.md",
      "href": "../docs/native-main-routing-qualification.md"
    },
    {
      "title": "Mainの実銅箔・間隔検査が未認定",
      "basis": "core reader/4synthetic faultは成立。実効rule注入・転送・routed-via/spacingは未実施。",
      "impact": "routerの表示やnet名でMain合格にできない。",
      "proof": "完全な物理形状表、実銅箔と層間接続、NC/穴/境界と0.20 mmの有効な検査。",
      "handling": "停止後に追加実験を開始しない。",
      "owner": "次回担当未定、PMO/PO",
      "source": "EDA-004G checker coverage",
      "href": "../docs/native-main-routing-qualification.md"
    },
    {
      "title": "モデル・環境・受け渡しの保守範囲",
      "basis": "tmp環境を固定入力/依存から再準備。公開serializer/enum/継承/I/O依存とfont問題。router/Java hash準備、実行は0。",
      "impact": "後工程と保守工数が不明。",
      "proof": "限定性・完全モデル/環境とDSN/SES保持の別途証拠。",
      "handling": "不足作業の限定性をPMOがレビュー、POが投資判断。",
      "owner": "PMO/PO、次回技術担当未定",
      "source": "EDA-004G report",
      "href": "../docs/native-main-routing-qualification.md"
    },
    {
      "title": "評価投資と製品への進行",
      "basis": "既知AI推定3.286h/以前のallowance4.036h保持。prior work保守予約2.25h＋今回wallを6h内計上。待機・engineer不明時間別記。旧wall cutoffはexecutor規約という解釈を開示。",
      "impact": "正確な残予算と製品着手時期は不明。",
      "proof": "POが投資・続行/保留/方向を判断。",
      "handling": "予算リセットなし。名目11.964 hは残予算認定ではない。",
      "owner": "PO / PMO",
      "source": "EDA-004G effort ledger",
      "href": "../docs/native-main-routing-qualification.md"
    }
  ],
  decision: {
    "status": "再開STOPの記録受入判断待ち・追加試験は未承認",
    "question": "EDA-004Gの限定STOPをどう受け入れ、不足作業への投資・続行/保留/方向をどう判断するか。",
    "evidence": "モデル/完全期待表/checkerが未成立。代替の小規模モデル準備を網羅的に試しておらず、大規模実装・予算超過の実測証拠はない。",
    "owner": "PMOが技術材料を整理し、POが判断。次回実施担当未定。",
    "planStatus": "Issue #85再開でMainファイル生成、完全工程1/2未成立。工程3〜5未実施。次回の独立期待表/coverage/担当/個別受入/投資は未計画。D-014〜18維持。",
    "proposal": "この報告で再試行・別候補・方式採用・製品設計を承認しません。"
  },
  history: [
    { name: "初期KiCad", tested: "旧4キー回路図とPCBの修正・CI検査", stopped: "繰り返したファイル形式修正の記録があり、PR #10 CIのPCB DRCは587違反・未接続40件。個々の原因とwriterは不明。", reuse: "既存シンボル・footprint・要求を検証済み参照として再利用。", retry: "異なる保存/検証方式と、現在の電気・形状の証拠が必要。", refs: "PR #6 / #10、D-014、Issue #79", href: "https://github.com/ihsinoky/he-piantor-42/pull/10" },
    { name: "JITX", tested: "部品モデル、電気的整合、headless物理・後工程", stopped: "PO判断D-016でRev.M1/Rev.Aの物理backendはNO-GO。完全な対応済みheadless多層配線は実証されず。", reuse: "受入済みの部品・電気・DFM・後工程の知見。", retry: "対応済みの完全配線手順と、投資・保守範囲の別途承認が必要。", refs: "D-016、Issue #55、C4B5", href: "../docs/eda-path-history.md" },
    { name: "stock tscircuit", tested: "native stock物理配線とMainのclearance介入", stopped: "評価した内部router探索は終了。介入A/Bで誤配線回帰があり、backendは未採用。", reuse: "native electrical source、固定モデル、独立物理検証。", retry: "対応済み機構で接続性と0.20 mm間隔を同時に示す必要。", refs: "D-018、Issue #61–#71、EDA-003B–F", href: "../docs/eda-path-history.md" },
    { name: "Circuit JSON → KiCad", tested: "bounded converter repairと小規模/Main前段の検査", stopped: "別々の試行でGND landのnet欠落/short、footprint library ID衝突、schematic ERC未成立。配線試行なし。", reuse: "raw fixture、固定環境、capture手順と限られたcheckerの知見。", retry: "正確なfootprint identityと接続済みschematic/ERC等の条件が必要。", refs: "EDA-004B–D、Issue #73 / #75 / #77、PR #76 / #78", href: "../docs/eda-path-history.md" },
    { name: "native KiCad objects", tested: "KiCad 9.0.9の固定小規模基板を作成・保存し、別のプログラム実行で開き直し", stopped: "初回DRCに予期しない警告2件。回路図経路がなく、Mainへ進む前にSTOP。", reuse: "試験対象内で確認した基板データの保存・再読込と形状・接続情報の保持。", retry: "PO/PMOが具体的な回路図経路を承認し、限定した修正・実効ルール試験・条件付き再評価を許可した場合のみ。", refs: "EDA-004E、Issue #79、PR #80、D-014", href: "../docs/native-kicad-authoring-feasibility.md" },
    { name:"external kicad-sch-api", tested:"固定KiCad 9.0.9で小規模回路図作成・検査", stopped:"停止条件なし、限定試験完了。初回受入は設定警告6件で失敗、同一ファイル設定修正後に候補成立。", reuse:"独立端子表、公開API生成、固定CLI検査とfault検出。", retry:"Main以降は別途計画・PO許可が必要。", refs:"EDA-004F / Issue #83 / merged PR #84（受入済み）", href:"../docs/headless-schematic-qualification.md" },
    { name:"public native Main prerequisite", tested:"固定Main入力・4限定symbol対応・fresh native形状・Main生成/raw検査", stopped:"再開CONVERSION_BLOCKED / ERC_UNQUALIFIED。4symbol検証とMain生成、61印刷違反/未認定glyph形状。配線0/0。", reuse:"入力hashと部分対応表、版・公開pin表観察。完全Mainへ結果を一般化しない。", retry:"限定STOPと不足作業の限定性をPMO/POがレビュー。追加試験権限はない。", refs:"EDA-004G / Issue #85（提案STOP）", href:"../docs/native-main-routing-qualification.md" }
  ],
  evidenceLinks: {
    "latestReport": "../docs/native-main-routing-qualification.md",
    "pathHistory": "../docs/eda-path-history.md",
    "githubActions": "https://github.com/ihsinoky/he-piantor-42/actions",
    "issue79": "https://github.com/ihsinoky/he-piantor-42/issues/79",
    "pr80": "https://github.com/ihsinoky/he-piantor-42/pull/80",
    "issue83": "https://github.com/ihsinoky/he-piantor-42/issues/83",
    "pr84": "https://github.com/ihsinoky/he-piantor-42/pull/84",
    "issue85": "https://github.com/ihsinoky/he-piantor-42/issues/85"
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
        "EDA-004G再開STOP。4symbol対応とMain生成、新規raw役割/core照合成立、印刷DRC61件STOP、配線0/0。EDA-004FはPR #84で受入済み。",
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
