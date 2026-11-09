# Main Rev.5 — Gerber フレーム CPL（Issue #221）

発注時の配置ビューアで新生成の Gerber と組み合わせる候補は
[CPL-jlcpcb-gerber-frame.csv](CPL-jlcpcb-gerber-frame.csv)。
元の [CPL.csv](CPL.csv) から PR #220 / Issue #219 と同じ方式で平行移動した。

- mm、X右・Y上。`X_order=X_original+62.107318`、`Y_order=Y_original−137.900000`。
- 新 Edge_Cuts の線中心外接範囲は `[62.107317,-137.900000,137.892682,-72.267949]` mm。
  PCB全3線分の `(X,−Y)` と独立CAM読戻しが一致。線幅0.05mmは寸法に加算しない。
- 移動量は55個全フットプリント直下の原点と元CPLから導出し、全行で同一。
  全55点で軸ごとの誤差0mm（許容0.000001mm）、全1,485部品対の符号付き相対ベクトルも一致。
  native絶対座標pos出力との二次照合も55点一致。
- 行順・Designator・Layer・Rotation文字列を保持。反転／角度補正なし。
  CPL.csvの理論原点X=62.107317799と6桁の移動量の差は0.000000201mm。
- J4は新しい `Rev5:J4` の原点 `(100,90)`、上面180°。
  GerberフレームCPLでは `(100,−90)`。pin1銅パッド中心は `(101.8,−91.875)`。
  補強ランドは無番号・無ネット。メーカー実装モデルのpin1／重心／回転はPMOが業者previewで確認する。

生成コード：[gerber-frame-cpl.py](../gerber-frame-cpl.py)。入力・出力hash、全点の照合結果：
[cpl-frame-check.json](../cpl-frame-check.json)。アップロード・カート投入・注文は実施していない。
