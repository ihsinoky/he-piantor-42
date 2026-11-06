# Issue #178 — M1 16mm／17mm 一体18キー評価基板

16mmの3×3（9キー）と17mmの3×3（9キー）を、**128×80mmの1枚基板**に配置した。
ブロック間の最近接キー中心距離は **35mm**（目標34mm以上）。GH14は変更せず、
3 MUX×6入力とした。D-021条件の初回自動配線後、独立DRCで見つかったGNDの短い
不要枝1本を除去し、最終基板は**全27ネットで独立4指標0 / 0 / 0 / 0**となった。
Gerber／ドリル、PCBAペースト、JLCPCB形式BOM／CPL、実装図を生成・照合した。
発注・課金・mergeは行っていない。公開結果は証跡の `publication.json` を参照。

[Issue #178](https://github.com/ihsinoky/he-piantor-42/issues/178) の取得本文と
[訂正版指示](../hardware/kicad/qualification/issue-178-m1-matrix-board/instructions-178.md)に従う。
古いIssueタイトルに残る16.5mmは対象外。バージョン定義を[D-028](decisions.md#d-028---m1--vera-version-definition-and-dual-pitch-matrix-evaluation-board)に追記した。
M1はMain（2 Wing版）＋本評価基板、ver.Aは左右21キーWing。
目的は**複数キーを押した状態のホール効果の相互作用の検証とピッチ比較**であり、
この作業では磁気実測・製品ピッチ選定を行っていない。

以下の `E/` は
[`hardware/kicad/qualification/issue-178-m1-matrix-board/`](../hardware/kicad/qualification/issue-178-m1-matrix-board/)。

## 設計定義と幾何

起点は#127の `wing/definition.py`、既存 `pitch9-16mm`／`pitch9-17mm` と
`evaluation_wing.py`。新しい定義は
[`wing/matrix.py`](../hardware/jitx/wing/matrix.py) の `define_m1_matrix()`、
native JITXエントリは `he_piantor_42_jitx.evaluation_wing.M1Matrix18`。
JSON／placement／nets／BOM／配置SVGは
[`wing/generated/m1-matrix18-16-17mm/`](../hardware/jitx/wing/generated/m1-matrix18-16-17mm/)。
既存pitch9・代表21キー・load21の定義と生成物は保持した。

| 項目 | 16mmブロック | 17mmブロック |
| --- | --- | --- |
| 定義座標：中心X | −34mm | +34mm |
| 列A/B/CのX | −50 / −34 / −18mm | +17 / +34 / +51mm |
| 行0/1/2のY（+Y上） | +26 / +10 / −6mm | +27 / +10 / −7mm |
| MUXアドレス | 0 / 1 / 2 | 3 / 4 / 5 |
| キー数 | 9 | 9 |

KiCad変換は **X=100+定義X、Y=100−定義Y**。
ブロック中心間68mmから内側列の16mm・17mmを引き、水平中心差は最小35mm。
中央行同士はYが一致するので、その組で距離35mmを達成する。
全81組のブロック間距離をnative PCBから測り、最小値と各ブロックの全ペアの
列／行間隔を確認した。最近接例は `U_HC1`（82,90）と `U_HA4`（117,90）。
`E/native-design-readback.json` に全81距離と部品原点の測定値を保存した。
同一向きのHall部品／磁石ターゲット原点をキー中心とするpitch9の前提を維持する。

基板外形はKiCad X36–164／Y60–140、厚さ1.2mm、2層。
4個のØ2.2mm NPTHは定義座標X±61／Y±37（KiCadでは39/161、63/137の組合せ）。
両銅箔層にØ5mmの配線・via・pour禁止領域を置き、実銅箔との非干渉を別途確認した。
NPTHそのものを禁止銅箔パッドとして扱わない#131の修正を継承する。
スイッチ用のPCB固定穴は仮定せず、非磁性の別治具でキー／磁石を支持する。
35mmは幾何要件の達成値であり、磁気的な分離保証ではない。

## 電気構成・GH14

| バンク | 16mm行0–2 | 17mm行0–2 | 出力／GH14 |
| --- | --- | --- | --- |
| A（両ブロックの左列） | H_A0_RAW〜H_A2_RAW | H_A3_RAW〜H_A5_RAW | MUX_OUT_A／9 |
| B（両ブロックの中央列） | H_B0_RAW〜H_B2_RAW | H_B3_RAW〜H_B5_RAW | MUX_OUT_B／11 |
| C（両ブロックの右列） | H_C0_RAW〜H_C2_RAW | H_C3_RAW〜H_C5_RAW | MUX_OUT_C／13 |

各MUXのS1–S6を使用する。S7／S8（address6／7、物理pin10／9）と物理pin3 NCは未接続。
18 DRV5055A3QDBZR、3 TMUX1208PWR、21個の100nF／16V X7R 0603容量、GH14×1。
Hallごと／MUXごとの直近容量を維持し、両ブロックに中心／直交隣接／対角のraw TPを設けた。
全18 TPは購入部品ではない露出銅箔であり、BOM／CPL／ペーストから除外する。

GH14のpin1=HALL_5V、2/4/8/10/12/14=GND、3/5/6=MUX_A0/A1/A2、7=WING_EN、
9/11/13=MUX_OUT_A/B/Cを維持。補強ランドは機械NCのまま。
既存pitch9 PCBと全信号／補強ランドの番号・ネット・ローカル位置・寸法・形状をnativeで比較して一致した。
JITXでも実際のHall／MUX／GHポート接続と未使用端子の非接続を検査した。

測定ファームウェアはaddress0–5を走査し、0–2／3–5をブロック別に校正する必要がある。
キーの同時押下状態を維持したまま順次読み取る構成であり、18チャネルの同時サンプリングではない。
既存Main側のADC回路は変更していない。切替後の実際のsettling、raw TPのプローブ負荷、
供給／GND共有の影響は実機で切り分ける。

## 配線・独立資格確認

| 条件 | 固定値 |
| --- | --- |
| 銅箔層／厚さ | F.Cu・B.Cuの2層／1.2mm |
| 信号幅 | 0.10mm |
| HALL_5V／GND幅 | 0.30mm |
| クリアランス | 0.10mm |
| via径／drill | 0.60／0.30mm |
| KRT | v0.23.8、escalation off |

プロジェクトのDefault／PowerクラスとCLIで同じ値を指定し、配線前に公式resolverを
net選択前で停止してreadbackした。CLI／実効設定は `E/runs/KRT-M1-01/`。
KRT本体は変更していない。最大3回×1800秒の上限を先に固定したが、実際は**自動配線1回、約59秒**のみ。
27ネットが接続され、escalation=0。途中で条件を変えた再配線はない。

独立検査は#141／#131を踏襲する。入力プロジェクトによるKiCad 9.0.9 DRC、
#87の実銅箔graph（穴を差し引く形状、レイヤー接触、全ネット）と同じ述語を使用した。
保守的な境界箱による候補除外のみ継承し、判定の許容差は変更していない。
非配線AST／snapshot、プロジェクト全設定、全トラック幅／via寸法も比較した。

| 段階 | required unconnected | wrong-net contacts | material violations | unexplained transfer changes |
| --- | ---: | ---: | ---: | ---: |
| 元の保存済みKRT出力 | 0 | 0 | 1 | 0 |
| 最終基板 | **0** | **0** | **0** | **0** |

初回の1件はGND／F.Cuの0.1414mmの行き止まり枝
`3b526ba3-fcea-418c-ac55-dcc9733483be`。
この1本だけを除去し、元PCB／不合格結果を残した。再配線やDRC除外は行っていない。
キー枠・ブロック／部品識別・pin1表示を追加し、裸TPのF.Pasteを除去する同じ変更を、
最終の未配線入力と配線出力の両方に適用してから全ネットを再検査した。
初回は18 TPのライブラリ不一致も検出したため、専用 `PCBA.pretty/testpoint` を同期し、
不合格ログを保持して再検査した。違反カテゴリの除外による合格化はしていない。

最終は信号305本×0.10mm、電源282本×0.30mm、via146個×0.60/0.30mm。
幅不足・誤ったvia寸法は0。全587配線の層別本数はF.Cu445／B.Cu142。
`E/inspection/final/assessment.json`、`width-audit.json`、`copper-graph.json`、
`transfer-diff.json` に保存した。シルクを含めた全DRC違反と未接続も0。
`E/derivation-verification.json` は元の入力／出力からの差分を独立に列挙し、
TPペースト除去・同一シルク追加・指定枝1本除去以外のAST変更0を確認する。

## 製造・PCBA成果物

提出するPCBは [`E/board/m1-matrix18.kicad_pcb`](../hardware/kicad/qualification/issue-178-m1-matrix-board/board/m1-matrix18.kicad_pcb)。
最終資格確認済み出力とbyte一致し、同梱projectは固定入力のルールを使用する。

- [`E/manufacturing/`](../hardware/kicad/qualification/issue-178-m1-matrix-board/manufacturing/)：Gerber 7層、PTH／NPTHドリル、上下ペースト。
- `BOM.csv`：JLCPCB列名で4 MPNグループ／実装43部品。
- `CPL.csv`：43部品すべてtop、mm、CCW。BOMと参照番号集合が完全一致。
- `assembly-top.svg/pdf/png`：native pad番号・pin1・部品本体・CPL中心の実装図。
- `FABRICATION.md`／`all-vias.csv`：via処理等の製造条件。完全レビューZIPにも同梱する。
- `preview-review/`：出力されたGerber／ドリルを独立にレンダリングした全層／表裏配線／表シルク。

CPL原点は基板左下（KiCad36,140）、X右・Y上。
GH14は信号ランド列原点（100,133）から、承認済みJstGh14の本体矩形中心への
Y=+2.325mm補正を行い、CPL=(64,4.675)mmとした。他部品は対称本体中心を用いる。
設計上の全角度は0°。assemblerライブラリ固有の0°／中心との一致は実装図により
後日のDFMで確認する。今回メーカーへのupload／preview承認は行っていない。

型番とコードは[DRV5055 C266128](https://jlcpcb.com/partdetail/TexasInstruments-DRV5055A3QDBZR/C266128)、
[TMUX1208 C494728](https://jlcpcb.com/partdetail/TexasInstruments-TMUX1208PWR/C494728)、
[容量 C45000](https://jlcpcb.com/partdetail/MurataElectronics-GRM188R71C104KA01D/C45000)、
[GH14 C265384](https://www.lcsc.com/product-detail/C265384.html)を使用する。
[BOM形式](https://jlcpcb.com/help/article/bill-of-materials-for-pcb-assembly)と
[CPL形式](https://jlcpcb.com/help/article/pick-place-file-for-pcb-assembly)はJLCPCB公式資料を確認した。
価格・在庫・attrition・工場受入を保証するものではない。
Web閲覧は成功したが、直接ダウンロードは一部IncompleteRead／JST403となったため、その失敗も `E/references/sources.json` に記録した。

**全146 plated viasに樹脂充填＋銅キャップ／めっき（POFV／IPC-4761 Type VII）を要求する。**
実形状の分類はmounted centre-in-pad18、mounted drill-edge7、mounted annulus-only4、
bare-testpad2、pad非重複115。KiCad9はfill/capをviaごとに記録できないため、
製造注記と全via一覧が必要であり、Gerberだけを注文に回さない。
これは配線寸法の緩和ではない。2層・0.60/0.30mmの全数処理について、工場受入と費用は後日確認が必要。

Gerbonara 1.5.0で全配線の座標・幅・層、via銅箔、全SMD padの位置・寸法、外形、
全146 PTH／4 NPTHを元nativeデータと照合した。
maskは上178開口／下0、pasteは上160／下0、裸TPのpaste開口0。
ドリル座標は0.001mm量子化、最大位置差0.000075mmで全穴一意対応した。
G90のヘッダ位置に関するparser警告は残すが、データを編集せず絶対座標の照合で確認した。
`manufacturing/manufacturing-check.json` に結果・hashを保存した。
実装図／表シルク／全層プレートを視認し、両3×3、ブロック識別、pin1、4 NPTH、空の裏mask／silkを確認した。

## 検証・公開・残る実測

既存6 WingバリアントのJITX回帰4テスト、新M1の幾何・native接続2テストが成功。
M1Matrix18のJITX dry build、Ruff、全生成物の再生成一致を確認した。
dry buildは配線／製造出力ではなく、CAMは上記のKiCad資格確認済み基板から生成する。

保守的に開始11:52 UTC、期限15:52 UTCの4時間枠とした。
初回bootstrapがローカル時刻をUTCとして記した点は、clock／Python UTC照合後、
`E/start.json` に訂正根拠を記録した。その他の検証harnessの戻り値／import等の失敗も
processログに残し、基板の合格と混同していない。
最終経過時間は `E/verification.json`。

通常の `.git` を変更せず、`.issue178-runtime/git` の専用ブランチ
`issue-178-m1-matrix-board` を使用する。開始local baseはd2139ee、取得したremote mainは67111c7。
その間に今回の起点JITX定義の変更がないことを確認し、作業ツリーをcheckout／resetせず
Git管理情報のみ新mainを基点とした。既存の未コミットD-024〜D-027や他Issue成果物は保持し、
今回のcommitのdecisions.mdにはremote main既存分＋D-028だけを含める。
`git-base.json` と既存ファイルhash監査を参照。

残る実測は磁石／ストローク治具、複数押下時のraw応答とクロストーク、電源／GND／
ADC settlingと校正、ハーネス／コネクタの操作性。今回の資格確認はPCB接続・幾何・製造データの整合であり、
これらの磁気／アナログ特性、実機耐久、メーカーのPCBA受入、製造リリースを認定するものではない。
