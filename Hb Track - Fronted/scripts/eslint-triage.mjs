import fs from "node:fs";

const path = ".eslint-report.json";
if (!fs.existsSync(path)) {
  console.error(`eslint-triage: missing ${path}. Run: npx eslint . -f json -o ${path}`);
  process.exit(2);
}

const report = JSON.parse(fs.readFileSync(path, "utf8"));

function inc(map, key, by = 1) {
  map.set(key, (map.get(key) ?? 0) + by);
}

const ruleAll = new Map();
const ruleErr = new Map();
const fileAll = new Map();
const fileErr = new Map();

for (const file of report) {
  const filePath = file.filePath?.replaceAll("\\", "/") ?? "unknown";
  for (const m of file.messages ?? []) {
    const rule = m.ruleId ?? "(no-rule)";
    inc(ruleAll, rule);
    inc(fileAll, filePath);
    if (m.severity === 2) {
      inc(ruleErr, rule);
      inc(fileErr, filePath);
    }
  }
}

function top(map, n = 15) {
  return [...map.entries()].sort((a, b) => b[1] - a[1]).slice(0, n);
}

console.log("\nTop rules (errors only):");
for (const [k, v] of top(ruleErr, 15)) console.log(`${v}\t${k}`);

console.log("\nTop files (errors only):");
for (const [k, v] of top(fileErr, 15)) console.log(`${v}\t${k}`);

console.log("\nTop rules (all severities):");
for (const [k, v] of top(ruleAll, 15)) console.log(`${v}\t${k}`);

console.log("\nTop files (all severities):");
for (const [k, v] of top(fileAll, 15)) console.log(`${v}\t${k}`);