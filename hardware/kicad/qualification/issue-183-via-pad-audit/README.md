# Issue #183 evidence

報告書: [docs/issue-183-via-pad-audit.md](../../../../docs/issue-183-via-pad-audit.md)。設計変更なし。発注・課金・mergeなし。

- `sources.json`: 固定commit、Git blob、入力SHA256、原基板パス。
- `inputs/*.kicad_pcb.gz`: 元Git blobとbyte一致する保存用snapshot。改版データではない。
- 各 `main-rev2/`, `wing-rev1-16mm/`, `wing-rev1-17mm/`:
  - `summary.json`, `all-vias.json/csv`: 全via監査。再開前に完了済みで、そのまま保持。
  - `pad-hits.csv`, `pads.json`: 重なりペアと全銅パッド。再開前の結果を保持。
  - `move-probes.json/csv`, `move-summary.json`: 0.10mm未達viaの独立した仮想移設探索。
  - `move-native-check.json`: 候補のnative pad／track／via copper形状検査。全体DRCではない。
  - `reroute-obstacles.json`: 直線接続候補なしのviaについて、最寄り移設先への直線を妨げる対象。
  - `overview.svg`: パッドとviaだけの俯瞰図。製造用データではない。
- `feasibility-summary.json`, `feasibility-details.md`: 候補数と難所の一覧。
- `resume-integrity.json`: 引き継いだ監査・入力・参考証跡のhash保持。
- `verification.json`: 保存済み結果の整合性確認。幾何監査を再実行しない。
- `reference-175/`: Mainの旧POFV再分類との照合用。今回の設計出力ではない。
- `manufacturer-sources/`: 公開仕様の匿名GET記録・HTML。業者受入れの証跡ではない。

```bash
E=hardware/kicad/qualification/issue-183-via-pad-audit
python3 "$E/verify.py"                         # 標準ライブラリと元Gitオブジェクトで検証
bash "$E/run-local-analysis.sh" resume        # 未完了の移設探索のみ再開
bash "$E/run-local-analysis.sh" check         # 保存候補をnative形状で再確認
bash "$E/run-local-analysis.sh" render        # 俯瞰SVG再生成
# 必要な場合だけ全via監査を再生成する（今回の継続runでは未実行）
bash "$E/run-local-analysis.sh" audit
```

`run-local-analysis.sh` の既定ランタイムはこの環境の既設KiCad 9.0.9。
`KICAD_RUNTIME_ROOT` で変更可。Python・Shapely・NumPyの使用版は `runtime.json`。
`diagnose-reroutes.py` はpcbnew環境で、`summarize-feasibility.py` は標準Pythonで実行する。

完了基板の探索を意図してやり直す場合は、その基板の `move-summary.json` を退避する。
途中探索は `move-checkpoint.json` から再開する。入力・方式・パラメータ・幅条件を変える場合は
対応する保存結果を退避してから再実行し、古い結果と混ぜない。
