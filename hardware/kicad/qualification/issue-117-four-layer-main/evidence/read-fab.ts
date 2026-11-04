// Read public parser only. This script contains no route/routeDsn invocation.
import { readFileSync, writeFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
const [source, input, output] = process.argv.slice(2);
const api = await import(pathToFileURL(source + "/src/api.ts").href);
const parsed = api.readDsn(readFileSync(input, "utf8"));
if (!parsed.ok) throw new Error(JSON.stringify(parsed));
const l = parsed.layout;
const data = { routingStarted: false, stack: l.stack, nets: l.nets,
  netGroups: l.netGroups, frame: l.frame, parts: l.parts, pads: l.pads,
  padForms: l.padForms, viaDefs: l.viaDefs, viaRules: l.viaRules,
  tracks: l.tracks, pours: l.pours, fences: l.fences, diagnostics: parsed.diagnostics,
  spacingKinds: l.spacing.kinds,
  spacing: l.stack.map(s => l.spacing.kinds.map((_, a) => l.spacing.kinds.map((_, b) => l.spacing.get(a, b, s.id)))) };
writeFileSync(output, JSON.stringify(data, (_, v) => v instanceof Map ? Object.fromEntries(v) : v, 2) + "\n");
