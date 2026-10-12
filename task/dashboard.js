(() => {
  "use strict";
  const P = window.PROJECT_STATUS;
  const $ = id => document.getElementById(id);
  const statusLabels = {done:"完了",current:"現在地",blocked:"未承認・停止中",next:"次の工程",todo:"未着手",hold:"保留",progress:"進行中",ready:"準備完了","not-ready":"未準備",waiting:"判断待ち"};
  const taskStatusLabels = {...statusLabels, done:"作業完了"};
  const resultLabels = {success:"成功",fail:"失敗",unknown:"未確認",notDone:"未実施",partial:"一部のみ確認"};
  const esc = value => String(value ?? "").replace(/[&<>"']/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
  const badge = (status, label) => `<span class="badge s-${esc(status)}">${esc(label)}</span>`;
  const link = (label, href) => `<a href="${esc(href)}">${esc(label)}</a>`;
  const valueOr = (value, fallback = "現在の状態は未確認") => value || fallback;

  $("source-date").textContent = `main記録の確認: ${P.source.confirmedAt.replace("T", " ").replace("Z", " UTC")} · ${P.source.reference}`;
  $("current-location").textContent = valueOr(P.current?.location);
  $("current-blocker").textContent = valueOr(P.current?.blocker);
  $("current-change").textContent = valueOr(P.current?.change);
  $("action-status").textContent = valueOr(P.nextAction?.status);
  $("action-status").className = "badge s-waiting";
  $("action-details").innerHTML = [
    ["担当", P.nextAction?.owner],
    ["具体的な行動", P.nextAction?.action],
    ["対象", P.nextAction?.target],
    ["着手条件", P.nextAction?.startCondition]
  ].map(([term, detail]) => `<dt>${esc(term)}</dt><dd>${esc(valueOr(detail))}</dd>`).join("");

  const path = [
    {name:"設計方針",status:"done",detail:"M1の構成・インターフェース方針を記録済み。",condition:""},
    {name:"設計・配線方法の成立確認",status:"current",detail:"評価作業は終了。EDA-004Eの初回試験は受入不成立で、方法は未認定。",condition:"次の評価方針はPO/PMOの判断待ち"},
    {name:"実物Rev.M1の設計",status:"blocked",detail:"試験fixtureの完成とは別。製品Main/Wingは未実装。",condition:"承認された設計経路と必要な技術検証"},
    {name:"製造・組立",status:"todo",detail:"製造用データ・組立物は未作成。",condition:"設計と製造前レビューの完了"},
    {name:"実測",status:"todo",detail:"実物での磁気・電力等の測定は未実施。",condition:"評価基板の製造・組立"},
    {name:"Rev.A",status:"todo",detail:"量産設計は未着手。",condition:"M1実測結果と後続判断"}
  ];
  $("product-path").innerHTML = path.map((step, index) => `<article class="path-step ${esc(step.status)}">
    <span class="path-number">${index + 1}</span>${badge(step.status, statusLabels[step.status])}
    <h3>${esc(step.name)}</h3><p>${esc(step.detail)}</p>${step.condition ? `<small><b>次へ進む条件:</b> ${esc(step.condition)}</small>` : ""}
  </article>`).join("");

  const evaluation = P.latestEvaluation;
  $("evaluation-title").textContent = valueOr(evaluation?.title);
  $("evaluation-id").textContent = valueOr(evaluation?.id);
  $("work-status").textContent = valueOr(evaluation?.workStatus);
  $("technical-status").textContent = valueOr(evaluation?.technicalStatus);
  $("priority-reason").textContent = valueOr(evaluation?.priorityReason);
  $("learned").textContent = valueOr(evaluation?.learned);
  $("unknown").textContent = valueOr(evaluation?.unknown);
  $("impact").textContent = valueOr(evaluation?.impact);
  $("next-condition").textContent = valueOr(evaluation?.nextCondition);
  $("evaluation-evidence").innerHTML = (evaluation?.evidence || []).map(item => {
    const status = item.result === "成功" ? "success" : item.result === "失敗" ? "fail" : item.result === "未確認" ? "unknown" : item.result === "一部のみ確認" ? "partial" : "notDone";
    return `<article class="evidence-item"><h4>${esc(item.label)}</h4>${badge(status, item.result)}<p>${esc(item.detail)}</p></article>`;
  }).join("");
  $("issue-link").href = evaluation.issueUrl;
  $("issue-link").textContent = `Issue #79`;
  $("pr-link").href = evaluation.prUrl;
  $("pr-link").textContent = "PR #80（記録受入）";
  $("report-link").href = P.source.reportUrl;

  $("history-list").innerHTML = P.history.map(item => `<article class="history-item">
    <h3>${esc(item.name)}</h3><p><b>試した範囲:</b> ${esc(item.tested)}</p>
    <p><b>停止理由:</b> ${esc(item.stopped)}</p><p><b>再利用できる成果:</b> ${esc(item.reuse)}</p>
    <p><b>再検討に必要な違い:</b> ${esc(item.retry)}</p>
    <p><b>根拠:</b> ${link(item.refs, item.href)}</p>
  </article>`).join("");
  $("history-link").href = P.source.historyUrl;

  $("roadmap").innerHTML = P.milestones.map(item => `<article class="milestone ${esc(item.status)}">
    ${badge(item.status, statusLabels[item.status] || item.status)}<h3>${esc(item.id)} · ${esc(item.name)}</h3>
    <p><b>成果物:</b> ${esc(item.deliverable)}</p><p><b>完了条件:</b> ${esc(item.exit)}</p>
  </article>`).join("");
  $("streams").innerHTML = `<div class="stream-grid"><div class="corner">分野</div>${P.milestones.map(item => `<div class="colhead">${esc(item.id)} ${esc(item.name)}</div>`).join("")}
    ${P.streams.map((stream, index) => `<div class="rowhead">${esc(stream.name)}</div>${stream.cells.map((cell, column) => `<div class="cell-${esc(P.streamStates[index][column])}">${esc(cell)}</div>`).join("")}`).join("")}</div>`;
  $("gates").innerHTML = P.gates.map(gate => `<article class="gate">${badge(gate.status, statusLabels[gate.status] || gate.status)}
    <h3>${esc(gate.name)}</h3><dl><dt>確認内容</dt><dd>${esc(gate.check)}</dd><dt>発生条件</dt><dd>${esc(gate.trigger)}</dd><dt>通過後</dt><dd>${esc(gate.unlocks)}</dd></dl></article>`).join("");
  $("risks").innerHTML = P.risks.map(risk => `<article class="risk ${esc(risk.kind)}"><span class="label">後工程の参考リスク</span><h3>${esc(risk.title)}</h3><p>${esc(risk.detail)}</p></article>`).join("");

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
