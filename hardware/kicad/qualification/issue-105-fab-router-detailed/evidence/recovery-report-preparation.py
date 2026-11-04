from pathlib import Path
E=Path('hardware/kicad/qualification/issue-105-fab-router-detailed/evidence')
s=(E/'summarize.py').read_text().replace("main_invocations=1,smoke_invocations=1", "main_invocations=2,main_completed_invocations=1,main_interrupted_invocations=1,recovery_invocations=1,smoke_invocations=1")
(E/'summarize-recovery.py').write_text(s)
s=(E/'write-report.py').read_text()
s=s.replace('詳細ルーター `tiles` を有効にした1条件を1回だけ実行した。','詳細ルーター `tiles` を有効にした単一条件で、外部中断からの回復後に1回の完了実行を得た。')
s=s.replace('Main 再実行・追加条件・追加調整は実施していない。','Main の起動は中断試行1回と、その回復1回。完了実行は1回だけであり、追加条件・追加調整は実施していない。')
s=s.replace('## Stage 1：唯一の Main と #103 比較','## 外部中断の保存と回復\n\n前回の Main は **2026-11-03T23:44:47.507650+00:00** に起動し、ユーザーから報告されたランタイム再起動という外部要因で中断された。result.json・out.ses・完了 record.json は存在せず、ルーターが正常終了して返した結果ではない。途中ログは pass 6・未接続17件までを含むが、本テストの最終結果として採用しない。中断原因の帰属はユーザーのランタイム再起動報告に基づく。\n\n元の processes/main/ 全ファイルを **processes/main-attempt-1-interrupted/** に移して byte/hash 同一で保存し、元 main-launch.json も同ディレクトリの launch-original.json に複製した。元 main-launch.json・スモーク証跡・条件特定・readback・既存スクリプトは変更していない。再開時の全証跡 hash と検証結果は recovery-preflight.json。\n\nユーザーの明示指示により、同一条件の回復 Main を **1回だけ** 実行した。これは設定探索ではなく、インフラ障害で未完了となった実行の回復である。起動回数は2回（外部中断1、回復1）、本テストの完了実行は1回。スモークおよび条件特定は再実行していない。Bun と clone は workspace に残っており /tmp の symlink を復旧しただけで、再導入や配線探索はない。ハーネス run-router-recovery.py の変更は launch 記録を main-recovery-launch.json に分ける1箇所だけで、driver.ts は元のままである。\n\n## Stage 1：単一の完了 Main と #103 比較')
s=s.replace("保守的開始 **2026-11-03 23:39:00 UTC**、2時間期限 **2026-11-04 01:39:00 UTC**。条件特定から Draft PR 作成までを含む。実 UTC と user context の日付差は `timebox.json` に記録。", "前回開始・期限は元の timebox.json に保存。今回の再開開始は **2026-11-03 23:48:06 UTC**、再開から2時間の期限は **2026-11-04 01:48:06 UTC**（recovery-preflight.json）。既存のスモーク・条件特定を引き継ぎ、回復・検査・記録・Draft PR 作成をこの期限内に行う。実環境 UTC を一貫して使用する。")
s=s.replace("base **{load('baseline-verification.json')['base']}**", "base **{load('recovery-preflight.json')['base_commit']}**")
s=s.replace("Main was run once only.","Main had one infrastructure-interrupted attempt and one recovery execution; exactly one completed run. See recovery-preflight.json and the analysis.")
(E/'write-report-recovery.py').write_text(s)
s=(E/'verify.py').read_text()
s=s.replace("base=load('baseline-verification.json')['base']", "base=load('recovery-preflight.json')['base_commit']")
s=s.replace("assert a['smoke_invocations']==a['main_invocations']==1", "assert a['smoke_invocations']==a['main_completed_invocations']==a['recovery_invocations']==1\nassert a['main_invocations']==2 and a['main_interrupted_invocations']==1")
s=s.replace("load('timebox.json')['deadline_utc']", "load('recovery-preflight.json')['deadline_utc']")
s=s.replace("now=datetime.datetime.now", """# Verify every file from before recovery, including relocated interrupted artifacts.
original=load('recovery-preflight.json')['original_evidence_sha256']
for name,sha in original.items():
 path=E/name
 if name.startswith('processes/main/'):path=E/'processes/main-attempt-1-interrupted'/name.removeprefix('processes/main/')
 assert h(path)==sha,name
interrupted=E/'processes/main-attempt-1-interrupted'
assert not any((interrupted/name).exists() for name in ['result.json','out.ses','record.json'])
assert h(interrupted/'launch-original.json')==h(E/'main-launch.json')
assert load('main-recovery-launch.json')['start_utc']==load('processes/main/record.json')['start_utc']
assert load('recovery-preflight.json')['verified_utc']<load('processes/main/record.json')['start_utc']
assert (E/'run-router-recovery.py').read_text()==(E/'run-router.py').read_text().replace(\"(stage+'-launch.json')\",\"(stage+'-recovery-launch.json')\")
now=datetime.datetime.now""")
s=s.replace("strict_single_configuration=True,", "strict_single_configuration=True,main_started_attempts=2,main_completed_runs=1,infrastructure_interrupted_attempts=1,original_evidence_unchanged=True,")
(E/'verify-recovery.py').write_text(s)
