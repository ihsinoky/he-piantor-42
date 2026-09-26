window.PROJECT_STATUS = {
  updatedAt: "2026-09-26",
  milestone: { id: "M1", name: "磁気方式・評価基板" },
  pullRequest: {
    number: 3,
    title: "Integrate sensor-test RP2040 schematic",
    state: "DRAFT",
    disposition: "work in progress"
  },
  ci: { state: "PASSED", source: "GitHub Actions", checks: [
    { name: "Layout generator", state: "PASS" },
    { name: "Sensor-test firmware", state: "PASS" },
    { name: "KiCad ERC / DRC", state: "PASS", details: [
      "he-piantor-sensor-test.kicad_sch: 0 violations",
      "usb-power.kicad_sch: 0 violations",
      "hall-front-end.kicad_sch: 0 violations",
      "integrated-sensor-test.kicad_sch: 0 violations"
    ] }
  ] },
  gates: [
    { name: "Dashboard review", state: "APPROVED", evidence: "Evidence-aware dashboard merged to main" }
  ],
  tasks: [
    { id: "EVT-001", title: "4キー評価基板 回路図", state: "IN PROGRESS" },
    { id: "EVT-004", title: "評価FW・CSV計測", state: "IN PROGRESS" }
  ]
};
