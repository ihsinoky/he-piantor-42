// Codex/AI self-report. Update only at start, meaningful checkpoints, blockers,
// human gates, and milestone completion — never as a periodic heartbeat.
window.RUNTIME_STATUS = {
  schemaVersion: 1,
  state: "WAITING_FOR_USER",
  milestone: "M1",
  work: "Project dashboard review",
  lastCheckpoint: "2026-09-26T10:17:49+00:00",
  checkpoint: "Evidence-aware health, roadmap, workstreams and human gates implemented",
  blocker: null,
  nextAction: "User reviews the dashboard PR; after approval, resume the M1 evaluation PCB",
  waitingForUser: true
};
