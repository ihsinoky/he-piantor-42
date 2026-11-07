(() => {
  "use strict";
  const plan = window.PROJECT_STATUS;
  const byId = id => document.getElementById(id);
  if (!plan) {
    byId("current-title").textContent = "計画データを読み込めませんでした。正本の project-status を参照してください。";
    return;
  }
  const labels = { done: "完了", progress: "進行中", todo: "未着手" };
  byId("position").textContent = plan.current.position;
  byId("current-title").textContent = plan.current.heading;
  byId("next-gate").textContent = plan.current.gate;
  byId("plan-status").textContent = plan.source.planStatus;
  byId("source-date").textContent = `記録の確認日：${plan.source.confirmedOn}（閲覧時刻ではありません）`;
  byId("status-source").href = plan.source.document;
  byId("artifacts-source").href = plan.source.artifacts;
  for (const milestone of plan.milestones) {
    const item = document.createElement("li");
    item.className = `milestone ${milestone.status}`;
    const isCurrent = milestone.id === plan.current.milestoneId;
    if (isCurrent) item.setAttribute("aria-current", "step");
    const label = document.createElement("span");
    label.className = "badge";
    label.textContent = `${labels[milestone.status]}${isCurrent ? " · 現在位置" : ""}`;
    const heading = document.createElement("h3");
    heading.textContent = `${milestone.id} · ${milestone.name}`;
    const gate = document.createElement("p");
    gate.textContent = milestone.gate;
    item.append(label, heading, gate);
    byId("milestones").append(item);
  }
})();
