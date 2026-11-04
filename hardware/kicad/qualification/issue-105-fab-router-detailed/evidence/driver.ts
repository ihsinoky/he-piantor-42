// SPDX-License-Identifier: GPL-3.0-only
// Test harness only. Imports unmodified public fab_router API; never uses routeSrj.
import { readFileSync, writeFileSync } from "node:fs";
import { resolve, join } from "node:path";
import { pathToFileURL } from "node:url";
const [source, input, output, mode] = process.argv.slice(2);
if (!source || !input || !output) throw new Error("usage: bun driver.ts SOURCE INPUT_DSN OUTPUT_DIR");
const api = await import(pathToFileURL(join(resolve(source), "src/api.ts")).href);
const save = (name: string, value: unknown) => writeFileSync(join(output, name), JSON.stringify(value, null, 2) + "\n");
// #105: documented tiles detailed mode; all other settings match #103.
const settings = { timeBudgetMs: 1800000, detailedRouter: "tiles" };
save("requested-settings.json", { settings, timeoutSecondsEquivalent: 1800, otherSettings: "#103 unchanged except detailedRouter; useFileSettings unset/false" });
const text = readFileSync(input, "utf8");
const before = api.readDsn(text);
save("parse.json", before.ok ? { ok: true, diagnostics: before.diagnostics, summary: api.parseSummary(before), frame: before.layout.frame, stack: before.layout.stack, netGroups: before.layout.netGroups, settingsFromFile: before.layout.settingsFromFile } : before);
if (!before.ok) process.exit(2);
const pipeline = await import(pathToFileURL(join(resolve(source), "src/pipeline/index.ts")).href);
const effective = pipeline.resolveSettings(settings, before.layout.settingsFromFile, before.layout.angleMode);
save("effective-settings-before.json", { readbackUtc: new Date().toISOString(), effectiveSettings: effective, mechanism: "unmodified resolveSettings; no routing call" });
if (mode === "readback-only") process.exit(0);
const preflight = JSON.parse(readFileSync(join(output, "../../main-preflight/effective-settings-before.json"), "utf8"));
if (JSON.stringify(preflight.effectiveSettings) !== JSON.stringify(effective)) throw new Error("preflight mismatch");
save("check-drc-before.json", api.checkDrc(before.layout));
const hooks = {
  onPass: (e: unknown) => console.log(JSON.stringify({ event: "pass", ...e as object })),
  onConnection: (e: unknown) => console.log(JSON.stringify({ event: "connection", ...e as object })),
  onLog: (level: string, message: string) => console.log(JSON.stringify({ event: "log", level, message })),
};
const result = api.routeDsn(text, settings, hooks);
if (!result.ok) { save("result.json", result); process.exit(2); }
if (JSON.stringify(result.report.effectiveSettings) !== JSON.stringify(effective)) throw new Error("report readback mismatch");
writeFileSync(join(output, "out.ses"), result.ses);
const { ses, ...report } = result;
save("result.json", report);
// Check the exact saved SES through the public readDsn/applySes/checkDrc path.
const returned = api.readDsn(text);
if (!returned.ok) throw new Error("re-read failed");
const applied = api.applySes(returned.layout, readFileSync(join(output, "out.ses"), "utf8"));
save("ses-apply.json", applied);
if (!applied.ok) process.exit(3);
const drc = api.checkDrc(returned.layout);
save("check-drc-after.json", drc);
save("stats-ses-roundtrip.json", api.layoutStats(returned.layout));
console.log(JSON.stringify({ event: "result", ok: result.ok, report: result.report, checkDrc: drc.counts }));
// Exit 0 means API/SES generation succeeded; completeness is recorded separately.
