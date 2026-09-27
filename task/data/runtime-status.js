// Optional, non-authoritative Dashboard context. Never use as project truth and
// never update it merely as a heartbeat. See docs/governance.md.
window.RUNTIME_STATUS = {
  schemaVersion: 1,
  state: "INFORMATIONAL",
  milestone: "M1",
  work: "See docs/ and GitHub for current project state",
  lastCheckpoint: null,
  checkpoint: "Optional display context only",
  blocker: null,
  nextAction: "Follow the Issue-driven workflow in docs/development-workflow.md",
  waitingForUser: false
};
