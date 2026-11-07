// Manual read model of docs/project-status.md; update together in one reviewed PR.
window.PROJECT_STATUS = {
  "source": {
    "document": "../docs/project-status.md",
    "artifacts": "../docs/artifacts-index.md",
    "confirmedOn": "2026-11-08",
    "planStatus": "PMO 案 · P3 の PO PR ゲートで確認"
  },
  "current": {
    "heading": "設計ベースライン確定、発注1の GO 待ち",
    "position": "MS1 完了 → MS2 未着手",
    "gate": "PO の発注 GO 待ち。前提確認：CPL 原点、UDB 上流抵抗の実測。",
    "milestoneId": "MS2"
  },
  "milestones": [
    {
      "id": "MS1",
      "name": "設計ベースライン確定",
      "status": "done",
      "gate": "Main Rev.4／Matrix Rev.3／Wing Rev.3／ケース最終データが揃い、版別の採択・検証記録あり。"
    },
    {
      "id": "MS2",
      "name": "発注1：Main Rev.4＋Matrix Rev.3 の製造",
      "status": "todo",
      "gate": "PO の発注 GO 待ち。前提確認：CPL 原点、UDB 上流抵抗の実測。"
    },
    {
      "id": "MS3",
      "name": "Matrix 実測",
      "status": "todo",
      "gate": "MS2 後、相互作用の大きさと工場実装／手実装の精度を比較する。"
    },
    {
      "id": "MS4",
      "name": "量産ピッチ決定（16mm／17mm）",
      "status": "todo",
      "gate": "MS3 の結果で PO 判断。"
    },
    {
      "id": "MS5",
      "name": "Wing 発注（Order 2）とケース印刷",
      "status": "todo",
      "gate": "MS4 後に Wing 発注判断。ケース印刷は PO 判断待ち。"
    },
    {
      "id": "MS6",
      "name": "組立・通電確認",
      "status": "todo",
      "gate": "基板・ケースを揃え、組立・通電と物理適合を確認する。"
    },
    {
      "id": "MS7",
      "name": "ファームウェア検証と完成",
      "status": "todo",
      "gate": "押下推定方式を確定し、実機でファームウェアを検証する。"
    },
    {
      "id": "MS8",
      "name": "成果公開（公開用リポジトリと Releases）",
      "status": "todo",
      "gate": "完成後の公開。詳細は別計画。"
    }
  ]
};
