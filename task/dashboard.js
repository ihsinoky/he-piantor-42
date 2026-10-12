(() => {
  "use strict";
  const P = window.PROJECT_STATUS;
  const $ = id => document.getElementById(id);
  const statusLabels = {done:"完了",current:"現在地",blocked:"未承認・停止中",next:"次の工程",todo:"未着手",hold:"保留",progress:"進行中",ready:"準備完了","not-ready":"未準備",waiting:"判断待ち",unconfirmed:"未認定",partial:"一部のみ確認",fail:"受入不成立",notEntered:"未実施"};
  const taskStatusLabels = {...statusLabels, done:"作業完了"};
  const esc = value => String(value ?? "").replace(/[&<>"']/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
  const badge = (status, label) => `<span class="badge s-${esc(status)}">${esc(label)}</span>`;
  const link = (label, href) => `<a href="${esc(href)}">${esc(label)}</a>`;
  const valueOr = (value, fallback = "現在の状態は未確認") => value || fallback;

  $("current-title").textContent = valueOr(P.current?.heading);
  $("source-date").textContent = `main記録の確認: ${P.source.confirmedAt.replace("T", " ").replace("Z", " UTC")} · ${P.source.reference}`;
  $("current-location").textContent = valueOr(P.current?.location);
  $("current-blocker").textContent = valueOr(P.current?.blocker);
  $("current-change").textContent = valueOr(P.latestEvaluation?.currentSummary);
  $("action-status").textContent = valueOr(P.nextAction?.status);
  $("action-status").className = "badge s-waiting";
  $("action-details").innerHTML = [
    ["担当", P.nextAction?.owner],
    ["具体的な行動", P.nextAction?.action],
    ["対象", P.nextAction?.target],
    ["着手条件", P.nextAction?.startCondition]
  ].map(([term, detail]) => `<dt>${esc(term)}</dt><dd>${esc(valueOr(detail))}</dd>`).join("");

  $("planning-note").textContent = P.plan.planningNote;
  $("product-path").innerHTML = P.plan.product.map((step, index) => `<article class="product-stage ${index === 0 ? "rev-m1-stage" : "later-stage"}">
    ${index === 0 ? `<span class="badge s-waiting">${esc(step.status)}</span>` : ""}
    <h3>${esc(step.name)}</h3>${index === 0 ? `<p><b>目的:</b> ${esc(step.purpose)}</p>` : ""}
    <p><b>得るもの:</b> ${esc(step.output)}</p><p><b>次へ進む確認:</b> ${esc(step.confirm)}</p>
    ${index === 0 ? `<p><b>完了条件:</b> ${esc(step.completion)}</p><p><b>担当:</b> ${esc(step.owner)}</p>` : ""}
    <p><b>依存:</b> ${esc(step.dependency)}</p>${index === 0 ? `<details><summary>根拠と詳細</summary><small>${esc(step.source)}</small></details>` : ""}
  </article>`).join("");

  const qualification = P.plan.qualification;
  $("qualification-status").textContent = qualification.status;
  $("qualification-purpose").textContent = qualification.purpose;
  $("qualification-output").textContent = `得るもの: ${qualification.output}`;
  $("qualification-completion").textContent = qualification.completion;
  $("qualification-owner").textContent = qualification.owner;
  $("qualification-established").innerHTML = `<b>既存の条件:</b> ${esc(qualification.establishedSummary)}`;
  $("qualification-established-detail").textContent = qualification.establishedDetail;
  $("qualification-established-source").innerHTML = `<b>出典:</b> ${(qualification.establishedSources || []).map(item => link(item.label, item.href)).join(" · ")}`;
  $("qualification-notice").textContent = qualification.notice;
  const evaluation = P.latestEvaluation;
  const coverage = new Map((evaluation?.coverage || []).map(item => [item.stepId, item]));
  $("qualification-map").innerHTML = qualification.steps.map(step => {
    const result = coverage.get(step.id) || { result:"未確認", detail:"最新評価にはこの範囲の証拠がありません。" };
    const resultClass = result.result.includes("一部確認") ? "partial" : "unconfirmed";
    const badgeStatus = result.result === "未実施" ? "notEntered" : result.result.includes("一部確認") ? "partial" : "unconfirmed";
    return `<article class="qualification-step ${resultClass}">
    ${badge(badgeStatus, result.result)}
    <h3>${esc(step.name)}</h3><p><b>得るもの:</b> ${esc(step.output)}</p>
    <p><b>確認方法:</b> ${esc(step.check)}</p><p><b>今回の証拠（${esc(evaluation?.id || "評価ID未確認")}）:</b> ${esc(result.detail)}</p>
  </article>`;
  }).join("");

  $("evaluation-title").textContent = valueOr(evaluation?.title);
  $("evaluation-id").textContent = evaluation?.id ? `評価 ${evaluation.id}` : "評価ID未確認";
  $("work-status").textContent = valueOr(evaluation?.workStatus);
  $("technical-status").textContent = valueOr(evaluation?.technicalStatus);
  $("evaluation-purpose").textContent = valueOr(evaluation?.purpose);
  $("tested-question").textContent = valueOr(evaluation?.testedQuestion);
  $("evidence-boundary").textContent = valueOr(evaluation?.evidenceBoundary);
  $("learned").textContent = valueOr(evaluation?.learned);
  $("unknown").textContent = valueOr(evaluation?.unknown);
  $("impact").textContent = valueOr(evaluation?.impact);
  $("next-condition").textContent = valueOr(evaluation?.nextCondition);
  $("evaluation-evidence").innerHTML = (evaluation?.evidence || []).map(item => {
    const status = item.result === "成功" ? "success" : item.result === "失敗" ? "fail" : item.result === "未確認" ? "unknown" : item.result === "一部のみ確認" ? "partial" : "notDone";
    return `<article class="evidence-item"><h4>${esc(item.label)}</h4>${badge(status, item.result)}<p>${esc(item.detail)}</p></article>`;
  }).join("");
  $("issue-link").href = evaluation.issue?.url || "#";
  $("issue-link").textContent = evaluation.issue?.id ? `Issue #${evaluation.issue.id}` : "Issue未確認";
  $("pr-link").href = evaluation.acceptedRecord?.url || "#";
  $("pr-link").textContent = evaluation.acceptedRecord?.id ? `PR #${evaluation.acceptedRecord.id}（${evaluation.acceptedRecord.status}）` : "受入記録未確認";
  $("report-link").href = P.source.reportUrl;
  $("report-link").textContent = `報告書（${evaluation?.id || "評価ID未確認"}）`;

  $("history-list").innerHTML = P.history.map(item => `<article class="history-item">
    <h3>${esc(item.name)}</h3><p><b>試した範囲:</b> ${esc(item.tested)}</p>
    <p><b>停止理由:</b> ${esc(item.stopped)}</p><p><b>再利用できる成果:</b> ${esc(item.reuse)}</p>
    <p><b>再検討に必要な違い:</b> ${esc(item.retry)}</p>
    <p><b>根拠:</b> ${link(item.refs, item.href)}</p>
  </article>`).join("");
  $("history-link").href = P.source.historyUrl;

  const riskCard = item => `<article class="risk-card">
    <h3>${esc(item.title)}</h3><p class="risk-impact">${esc(item.impact || item.consequence || "影響は未確認です。")}</p>
    <details><summary>根拠・必要な確認・担当・出典</summary>
      <p><b>根拠:</b> ${esc(item.basis || item.detail || "根拠未記載")}</p>
      <p><b>判断に必要な証拠:</b> ${esc(item.proof || "別途確認が必要")}</p>
      <p><b>対処状況:</b> ${esc(item.handling || "現在の対処状況は未確認")}</p>
      <p><b>担当:</b> ${esc(item.owner || "担当未定")}</p>
      <p><b>出典:</b> ${item.href ? link(item.source || item.title, item.href) : esc(item.source || "未記載")}</p>
      ${item.proposal ? `<p class="unapproved"><b>対策案:</b> ${esc(item.proposal)}</p>` : ""}
    </details>
  </article>`;
  $("current-problems").innerHTML = evaluation?.currentProblem ? riskCard(evaluation.currentProblem) : "<p>現在の評価に記録された問題はありません。</p>";
  $("uncertainties").innerHTML = P.uncertainties.map(riskCard).join("");
  $("later-risks").innerHTML = P.risks.map(item => riskCard({ ...item,
    title:`後工程・過去方式: ${item.title}`,
    basis:item.detail,
    impact:"現在のEDA経路に対する判定とは分けて扱う。",
    proof:"該当製品段階または過去方式を再検討する場合に出典の最新性を確認。",
    handling:"参考情報。現在の技術候補の合格・不合格には転用しない。",
    owner:item.owner||"該当段階の担当者（未定）",
    source:item.source||"project-status.md",
    href:item.href||"../../docs/project-status.md"
  })).join("");

  $("decision-question").textContent = P.decision.question;
  $("decision-status").textContent = P.decision.status;
  $("decision-details").innerHTML = [
    ["不足する判断材料", P.decision.evidence],
    ["判断・整理の担当", P.decision.owner],
    ["計画状態", P.decision.planStatus],
    ["提案の扱い", P.decision.proposal]
  ].map(([term, detail]) => `<dt>${esc(term)}</dt><dd>${esc(detail)}</dd>`).join("");
  $("decision-plan-status").textContent = P.nextAction.startCondition;

  $("roadmap").innerHTML = P.milestones.map(item => `<article class="milestone ${esc(item.status)}">
    ${badge(item.status, statusLabels[item.status] || item.status)}<h3>${esc(item.id)} · ${esc(item.name)}</h3>
    <p><b>成果物:</b> ${esc(item.deliverable)}</p><p><b>完了条件:</b> ${esc(item.exit)}</p>
  </article>`).join("");
  $("streams").innerHTML = `<div class="stream-grid"><div class="corner">分野</div>${P.milestones.map(item => `<div class="colhead">${esc(item.id)} ${esc(item.name)}</div>`).join("")}
    ${P.streams.map((stream, index) => `<div class="rowhead">${esc(stream.name)}</div>${stream.cells.map((cell, column) => `<div class="cell-${esc(P.streamStates[index][column])}">${esc(cell)}</div>`).join("")}`).join("")}</div>`;
  $("gates").innerHTML = P.gates.map(gate => `<article class="gate">${badge(gate.status, statusLabels[gate.status] || gate.status)}
    <h3>${esc(gate.name)}</h3><dl><dt>確認内容</dt><dd>${esc(gate.check)}</dd><dt>発生条件</dt><dd>${esc(gate.trigger)}</dd><dt>通過後</dt><dd>${esc(gate.unlocks)}</dd></dl></article>`).join("");
  [...new Set(P.tasks.map(task => task[1]))].sort().forEach(area => $("area").insertAdjacentHTML("beforeend", `<option>${esc(area)}</option>`));
  ["done","progress","blocked","todo","hold"].forEach(status => $("status").insertAdjacentHTML("beforeend", `<option value="${status}">${statusLabels[status] || status}</option>`));
  const renderTasks = () => {
    const query = $("query").value.toLowerCase(), area = $("area").value, status = $("status").value;
    $("task-rows").innerHTML = P.tasks.filter(task => (!query || task.join(" ").toLowerCase().includes(query)) && (!area || task[1] === area) && (!status || task[3] === status))
      .map(task => `<tr><td>${esc(task[0])}</td><td>${esc(task[1])}</td><td>${esc(task[2])}</td><td>${badge(task[3], taskStatusLabels[task[3]] || task[3])}</td><td>${esc(task[4])}</td><td>${esc(task[5])}</td></tr>`).join("");
  };
  ["query","area","status"].forEach(id => $(id).addEventListener(id === "query" ? "input" : "change", renderTasks));
  renderTasks();
  $("data-version").textContent = `状態記録の確認日時: ${P.source.confirmedAt} · 正本はdocs。静的データの更新にはレビュー済みPRが必要です。`;
})();
