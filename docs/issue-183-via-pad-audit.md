# Issue #183 — Main Rev.2／Wing Rev.1 の via–パッド重なり監査

[Issue #183](https://github.com/ihsinoky/he-piantor-42/issues/183)、2026-11-06 UTC。
**3基板とも、現状は「全 via の annulus 外周–パッド銅間隔 ≥ 0.10mm」を満たさない。Main は D-022 の POFV を維持する。Wing は裸基板・手はんだの現仕様と将来の標準PCBAを区別し、標準PCBAでPOFV不要とは判定しない。** 移設・局所再配線で解消できる候補はあるが、全体同時成立を確認する改版が必要である。

このIssueは監査と見通しまで。設計データ、製造仕様、決定記録は変更していない。発注・課金・メーカーへの設計アップロード・問い合わせ・merge は行っていない。

以下 `E/` は [証跡フォルダ](../hardware/kicad/qualification/issue-183-via-pad-audit/) を指す。

## 対象と引き継ぎ

`.issue183-runtime/instructions-183.md` を全文読み、GitHubのIssue本文・コメントを再確認した。再開時点で3基板の `summary.json`、全via一覧、pad一覧、重なりペア一覧は完了していた。保存済み一覧の集計・CSV整合性、圧縮snapshotと元Git blobの一致を検証して引き継ぎ、**完了済みの全via幾何監査は再実行していない**。既存監査ファイルのhash保持は [E/resume-integrity.json](../hardware/kicad/qualification/issue-183-via-pad-audit/resume-integrity.json) に記録した。

| 基板 | 読み取ったブランチと固定commit | 最終基板のパス（ブランチ内） |
| --- | --- | --- |
| Main Rev.2 | `issue-175-main-dual-wing-final2` / `dcf5c61d9b8480da9698f71c5209d516d6231898` | `hardware/kicad/qualification/issue-175-main-dual-wing-final2/inspection/final/main.kicad_pcb` |
| Wing Rev.1 16mm | `issue-149-wing-silkscreen` / `8a7d76651a064ec71160e84c07682aff8bd8beb4` | `hardware/kicad/qualification/issue-149-wing-silkscreen/16mm/wing-16mm-silk149.kicad_pcb` |
| Wing Rev.1 17mm | 同上 | `hardware/kicad/qualification/issue-149-wing-silkscreen/17mm/wing-17mm-silk149.kicad_pcb` |

| 基板 | PCB SHA256（展開後） | 銅層／via寸法 |
| --- | --- | --- |
| Main | `acab039f3b5f5ea30500d2f8537e320e198f881c227a3c3042753fc021c30f1c` | 4層／全113個 0.60/穴0.30mm |
| Wing 16mm | `b193fddb7c7c3795c33da75d578164bc231bf0eda2ca1495d973730b17c7b354` | 2層／全196個 同寸法 |
| Wing 17mm | `4bd99f30ebdfe0588beff57c98e6e717e6650ee4d7effa3a53552916cd925ffd` | 2層／全198個 同寸法 |

[E/sources.json](../hardware/kicad/qualification/issue-183-via-pad-audit/sources.json) にcommit、blob、SHA256、snapshotパスを固定した。`E/inputs/*.kicad_pcb.gz` は元データとbyte一致する保存用コピーであり、新しい設計基板ではない。作業用展開データは `.issue183-runtime/` 内の読み取り専用ファイルである。

## 測定方法と全via集計

物差しは [#182](https://github.com/ihsinoky/he-piantor-42/issues/182) の **全部品パッド（テストパッド含む）に対して annulus 外周から 0.10mm 以上**。同ネットでも免除しない。KiCad 9.0.9のnative effective copper shapeで共通銅層のパッドを走査し、via中心からパッド銅までの距離 `d` とvia半径 `r` から、符号付き間隔 `g = d − r` を求めた。NPTHはパッド銅の集計から除外する。

分類は優先順に、中心がパッド内＝`center`、中心は外だがdrill円がパッド銅に接触・重複＝`drill-edge`、drillは外だがvia銅円が接触・重複＝`annulus-only`、それ以外＝`none`。複数パッドに当たるviaもviaとして1回だけ数える。実装部品／テストパッドの区分は、`TP`で始まるReferenceを裸テストパッドとし、それ以外を実装部品としている（手はんだ対象のコネクタも実装部品）。

| 基板 | 全via | 中心 | drill縁 | annulusのみ | 重なりなし | 重なりvia計 | 0.10mm未達計 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Main Rev.2 | 113 | 24 | 5 | 3 | 81 | **32** | **35** |
| Wing Rev.1 16mm | 196 | 18 | 5 | 5 | 168 | **28** | **32** |
| Wing Rev.1 17mm | 198 | 32 | 9 | 5 | 152 | **46** | **52** |

| 基板 | 実装部品に重なるvia（中心／drill縁／annulus） | テストパッドに重なるvia（同順） | 重なりペア／ユニークパッド | 重なりなしの最小間隔 | 重なりなしでも0.10mm未達 |
| --- | --- | --- | ---: | ---: | ---: |
| Main | 31（23／5／3） | 1（1／0／0） | 33／33 | 0.025000mm | 3 |
| Wing 16mm | 25（15／5／5） | 3（3／0／0） | 28／28 | 0.005164mm | 4 |
| Wing 17mm | 42（31／8／3） | 4（1／1／2） | 46／46 | 0.011131mm | 6 |

3基板とも全via中の最小 `g` は **−0.300000mm**、実銅間の物理的最小距離 `max(0,g)` は **0mm**。中心がパッド内の場合は `d=0` のため `g=−r` に飽和する。これはパッド内への実際の侵入深さを示す値ではない。`none` でも0.10mm未満なら #182 基準には不合格であり、重なりviaだけの移設では完了しない。

Mainの32候補のUUID集合は #175 のPOFV再分類と完全一致する。#175の「実装中心23＋裸テストパッド1」を今回の4分類では「中心24」と表すため、数字の差は分類軸による。Mainはvia1個が2パッドに重なり、33ペアになる。全重なりペアは同ネットだった。同ネットの接続用viaでも、はんだ吸い上がりや #182 の幾何基準からは除外しない。

境界近傍も記録した。Mainにはちょうど0.100000mmのペアが7件あり、名目寸法では合格だが製造余裕を証明しない。Wing 17mmの `82379079-db4f-480c-a2b0-6ca804749f3d` は C_HB6.2 まで0.150001mmで、drill半径0.15mmより **1nm外側**のため名目分類はannulusのみ。実製造でdrillと重ならないことの保証ではない。全境界ペアは各 `summary.json` に残した。

テストパッドの内訳は Main `TP4.1`（中心）、Wing 16mm `TP_H_DIAG_RAW.1`、`TP_W_MUXB.1`、`TP_W_MUXA.1`（すべて中心）。Wing 17mmは `TP_W_MUXA.1`（中心）、`TP_H_DIAG_RAW.1`（drill縁）、`TP_W_MUXB.1`、`TP_H_CTR_RAW.1`（annulusのみ）。

各基板フォルダの `all-vias.json/csv` に全viaのUUID、座標、ネット、4分類、最近傍パッド、最小間隔、0.10mm合否を保存し、`pad-hits.csv` に重なるパッドのReference／番号／UUID／種別／層／距離を保存した。`pads.json` は対象の全銅パッド一覧。

配置の俯瞰図（灰＝パッド銅、赤＝中心、橙＝drill縁、黄＝annulusのみ、緑＝重なりなし、紫枠＝重なりなしだが0.10mm未達）：[Main](../hardware/kicad/qualification/issue-183-via-pad-audit/main-rev2/overview.svg)、[Wing 16mm](../hardware/kicad/qualification/issue-183-via-pad-audit/wing-rev1-16mm/overview.svg)、[Wing 17mm](../hardware/kicad/qualification/issue-183-via-pad-audit/wing-rev1-17mm/overview.svg)。配線・zone・mask・pasteの描画は省略した診断図であり、製造データではない。

## 配置固定での移設・再配線の見通し

各基板の0.10mm未達viaだけを対象に、**他via・全パッド・既存配線を固定し、1個ずつ仮想移設先を探索**した。最大3mm、半径0.05mm刻み、角度5°刻みの4,320点／via。部品・配線の移動、基板保存は行っていない。

移設先では全部品パッドとの間隔 ≥0.10mm、異ネットの既存配線との間隔 ≥0.10mm、他viaとの銅間隔 ≥0.10mm（同ネットも固定して距離を確保）、外形からの銅離隔0.30mm、NPTHから0.25mm、およびvia禁止領域を確認する。幾何近似に20nmの探索ガードを置き、採用候補のパッド／異ネット配線はnative shapeで再確認した。

直線接続の探索では、元via銅円と接触する同ネット配線の最近点、および同ネットの重なるパッドの中心から、移設先まで各層でstubを引く。配線の幅は既存接触配線を維持し、パッドからの新規stubは同層の接触配線の最大幅（なければ0.10mm）、WingのHALL_5V／GNDは最低0.30mmとする。異ネットパッド／配線／viaとの0.10mm、外形・NPTH・track禁止領域を検査した。候補座標とstubは別スクリプトでもnative copper shapeで検査した。

全119件にパッド・固定銅箔を避ける移設先候補が見つかった。うち90件に直線stubの接続候補があり、29件は直線stubが見つからず迂回等の追加検討が必要だった。

| 基板 | 0.10mm未達対象 | 固定パッド・銅箔を避ける移設先あり | 直線stubの接続候補あり | 移設先あり・直線stubなし | グリッド内に移設先なし | 直線候補の最大変位 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Main Rev.2 | 35 | 35 | **33** | **2** | 0 | 2.05mm |
| Wing Rev.1 16mm | 32 | 32 | **22** | **10** | 0 | 0.90mm |
| Wing Rev.1 17mm | 52 | 52 | **35** | **17** | 0 | 1.60mm |

Mainの33件には、重なりのない0.10mm未達3件も含む。残る2件は **C5.2／GND**（via `6bf1ec76-373b-473d-8a4f-1220e3ffc25f`、元 `(94.5,102.0)mm`）と **C4.1／V3V3**（`83b6e9ed-f13d-4984-8aac-1d3fee6bd3fb`、元 `(93.5,99.2)mm`）。最寄り移設候補はそれぞれ約1.40mm／1.25mm先にあるが、そこへ直線で接続すると、前者はXOUT、後者はMUX_OUT_Cの既存配線に0.10mmクリアランスで干渉する。局所迂回や周辺配線の引き直しを調べる必要がある。

Wing 16mmの直線stubなし10件は `U_MUX_A.1/.2/.4/.13/.15`、`U_MUX_B.2/.14`、`U_MUX_C.13`、`C_MUX_C.2`、`TP_W_MUXA.1`。MUX周囲の既存RAW／制御信号や電源配線を跨ぐ経路が難所である。たとえば `U_MUX_A.13`（HALL_5V）から最寄り候補への0.30mm stubは、同部品の別パッドやMUX_A2／H_A5_RAW配線に干渉する。

Wing 17mmは直線stubなし17件で、中心15、drill縁1、annulusのみ1。6件の「重なりなし・0.10mm未達」にはすべて直線接続候補がある。一方、MUX・センサ周囲などの17件には迂回や周辺配線を含む再検討が必要であり、16mmの22件という範囲をそのまま流用できない。

29件すべてのUUID・元座標・ネット・対象パッド・移設先・妨げるネット／パッド／層は [E/feasibility-details.md](../hardware/kicad/qualification/issue-183-via-pad-audit/feasibility-details.md) に一覧化した。全候補の座標・元銅箔への接続アンカーは各基板の `move-probes.json/csv`、集計は [E/feasibility-summary.json](../hardware/kicad/qualification/issue-183-via-pad-audit/feasibility-summary.json)。全119件の候補は別スクリプトのnative pad／track／via検査を通過し、採用した90件の直線stubにnativeクリアランス違反は0件だった（各 `move-native-check.json`）。

**探索の限界：** 各候補は単独移設の結果であり、候補同士やstub同士の同時競合、全ネットの接続、電源／GNDインピーダンス、zone再fill、全DRC、mask／paste・実装工程は未資格確認。MainのIn1.Cu GND面は再fillしておらず、候補座標へのplane接続も保証しない。グリッドに候補がないことは連続平面上の不可能証明ではない。「直線stubなし」はこの接続方法で見つからなかったという意味であり、部品配置変更が必須だと断定しない。via移設には接続の引き直しを伴うため、銅箔を全く変更せず座標だけ変えて製造できるとは扱わない。

再開時の未完了 `feasibility.py` には、他via禁止領域の半径を作る際のIU→mm換算漏れがあった。完了監査の分類には影響しない。誤った探索結果は成果物から除外し、換算を修正し、元viaに面接触する配線とパッド中心からのstubを探索するようにした。Wing電源stubの0.30mm条件も明示し、該当候補を再評価した。

## 基板ごとのPOFV判断と次の判断材料

| 基板 | 現状の結論 | POFVを不要にする改版の見通し／残る確認 |
| --- | --- | --- |
| Main Rev.2 | **現状のままはPOFV必要としてD-022を維持。** 31個が実装パッドに重なり、そのうち中心23＋drill縁5。発注仕様から外せる証拠はない | 配置固定での移設候補はある。35個を対象に局所再配線し、同時成立・zone再fill・独立4指標0・全via間隔 ≥0.10mmを確認してから不要化を判断。今回は **不要化の確定は要追加検討** |
| Wing Rev.1 16mm | **裸基板・手はんだにPOFV必須とは断定しない。将来の標準PCBAでは要対策／要追加検討。** 実装25個（中心15＋drill縁5＋annulus5） | 全32個の0.10mm未達を対象に配置固定の移設・局所再配線を検討。候補の同時成立、既存0.30mm給電条件、アナログ・電源特性、DRC／接続を再資格確認。解消前の標準PCBAはPOFV工程または業者が認める対策の受入れが必要 |
| Wing Rev.1 17mm | **裸基板・手はんだと標準PCBAを区別し、標準PCBAでPOFV不要とは判定しない。要追加検討。** 実装42個（中心31＋drill縁8＋annulus3） | 全52個の0.10mm未達を解消する改版が必要。16mmより対象が多く、同じ配置・移設手順が流用できるとは限らない。候補と難所を個別に引き継ぎ、再配線と全体検証の結果で不要化を判断 |

JLCPCBの [Via-in-Padガイド](https://jlcpcb.com/help/article/via-in-pad-pofv-guide) は、リフローではんだがviaへ流れ込み接合量が不足するリスクと、充填・平坦化・銅キャップによる処理を説明している。[via coveringの説明](https://jlcpcb.com/help/article/pcb-via-covering) ではtented、ink plugged、epoxy-filled & cappedを区別している。従って、銅の接触があるだけで全候補を同じリスクとせず、drill重なりとannulusのみ、裸テストパッドと実装ランドを分けて業者へ判断材料を渡す。今回の幾何監査はメーカーの受入れやPOFV料金の確定を代行しない。公開資料の匿名GET記録と保存HTMLは `E/manufacturer-sources/`。

また、#182の0.10mmは本プロジェクトの**設計監査基準**であり、「これを満たせば全表面処理・全実装工程でPOFV不要」というメーカー保証ではない。実際のmask開口・paste、via露出・tented条件、仕上げ、製造公差、数量・工程に対するDFM受入れが必要。未重複の裸テストパッドを理由にPOFVを全基板へ追加したり、annulusのみをdrill-in-padと同一視して一括判断したりしない。新規見積、アップロード、注文は行っていない。

配置変更が必須だと証明された基板はない。次の改版ではまず配置固定で局所再配線を試し、競合や電源／信号特性を含めて成立しない範囲が残った場合に、広域再配線・他viaの協調移設、それでも不足する場合の配置変更を別Issueで判断する。今回は3基板とも **POFV不要化を承認できる段階には達していない** という監査結論である。

## 再現と検証

既設KiCad／geometryランタイムを読み取り使用し、TMPDIR・XDG・展開基板・Git管理情報は `.issue183-runtime/` に置いた。通常worktreeの読み取り専用 `.git` は変更せず、作業用Gitメタデータを同ディレクトリへ複製して提出する。原基板と既存追跡ファイルは変更していない。

```bash
E=hardware/kicad/qualification/issue-183-via-pad-audit
# 保存済み監査の整合性確認。全viaの幾何監査を再実行しない
python3 "$E/verify.py"
# 移設探索の再開。完了基板・checkpoint済みviaは再探索しない
bash "$E/run-local-analysis.sh" resume
# 候補のnative geometry再確認（基板保存なし）
bash "$E/run-local-analysis.sh" check
# 全via監査を明示的に再生成する場合のみ
bash "$E/run-local-analysis.sh" audit
```

ランタイムのパスはこの環境向け。`KICAD_RUNTIME_ROOT` で変更できる。KiCad 9.0.9 pcbnew、Python・Shapely・NumPyの実使用版は `E/runtime.json`。`check-move-candidates.py` と `render-overviews.py` は同じPython環境を必要とする。別環境では `run-local-analysis.sh` 内と同等の環境変数を設定し、Pythonで直接実行できる。

[E/verification.json](../hardware/kicad/qualification/issue-183-via-pad-audit/verification.json) はsnapshot／Git blob一致、既存監査hash保持、全507viaの分類・CSV・件数・間隔整合、#175候補UUID一致、全119未達viaの移設探索証跡とnative検査を確認する。これは改版後の独立4指標・DRC合格を意味しない。提出する変更は本報告書と `E/` の監査証跡・再現スクリプトのみ。作業ブランチは `issue-183-via-pad-audit`、Draft PRで提出し、mergeは行わない。
