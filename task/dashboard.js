(() => {
  const project = window.PROJECT_STATUS;
  const runtime = window.RUNTIME_STATUS;
  const el = (id) => document.getElementById(id);
  const badge = (state) => `<span class="badge ${state.toLowerCase().replaceAll(" ", "-")}">${state}</span>`;

  el("updated").textContent = `Evidence updated ${project.updatedAt}`;
  el("milestone").textContent = `${project.milestone.id} · ${project.milestone.name}`;
  el("title").textContent = project.pullRequest.title;
  el("summary").textContent = "PR、CI、設計ゲートを証拠と実行時状態に分離して表示します。";
  el("runtime-state").innerHTML = badge(runtime.state);
  el("pull-request").innerHTML = `<p><b>#${project.pullRequest.number}</b> ${project.pullRequest.title}</p><p>${badge(project.pullRequest.state)} ${project.pullRequest.disposition}</p>`;
  el("runtime").innerHTML = `<dl><dt>Work</dt><dd>${runtime.work}</dd><dt>Blocker</dt><dd>${runtime.blocker ?? "None"}</dd><dt>User action</dt><dd>${runtime.waitingForUser ? "Required" : "Not required"}</dd><dt>Checkpoint</dt><dd>${runtime.checkpoint}</dd><dt>Next action</dt><dd>${runtime.nextAction}</dd></dl>`;
  el("checks").innerHTML = `<p>${badge(project.ci.state)} <span class="muted">${project.ci.source}</span></p>` + project.ci.checks.map((check) => `<div class="row"><div><b>${check.name}</b>${check.details ? `<ul>${check.details.map((detail) => `<li>${detail}</li>`).join("")}</ul>` : ""}</div>${badge(check.state)}</div>`).join("");
  el("gates").innerHTML = project.gates.map((gate) => `<div class="row"><div><b>${gate.name}</b><small>${gate.evidence}</small></div>${badge(gate.state)}</div>`).join("");
  el("tasks").innerHTML = project.tasks.map((task) => `<div class="row"><div><code>${task.id}</code><small>${task.title}</small></div>${badge(task.state)}</div>`).join("");
})();
