import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';

const root = process.cwd();
const srcRoot = join(root, 'src');
const featuresRoot = join(srcRoot, 'features');
const allowedRouteFile = 'src/shared/api/dataServiceClient.ts';

function walk(dir) {
  const entries = [];
  for (const name of readdirSync(dir)) {
    const path = join(dir, name);
    const stat = statSync(path);
    if (stat.isDirectory()) {
      entries.push(...walk(path));
    } else if (/\.(ts|tsx)$/.test(name)) {
      entries.push(path);
    }
  }
  return entries;
}

const srcFiles = walk(srcRoot);
const featureFiles = statSync(featuresRoot, { throwIfNoEntry: false }) ? walk(featuresRoot) : [];
const failures = [];

for (const file of srcFiles) {
  const rel = relative(root, file);
  const text = readFileSync(file, 'utf8');
  if (text.includes('/api/v1/knowledge')) {
    failures.push(`${rel}: forbidden legacy route /api/v1/knowledge`);
  }
  if (rel !== allowedRouteFile && /['"`]\/api\//.test(text)) {
    failures.push(`${rel}: route string is only allowed in ${allowedRouteFile}`);
  }
}

for (const file of featureFiles) {
  const rel = relative(root, file);
  const text = readFileSync(file, 'utf8');
  if (/\bfetch\s*\(/.test(text)) {
    failures.push(`${rel}: feature modules must not call fetch directly`);
  }
  if (/correction-(rules|plan)|correction rules|correction plan/i.test(text)) {
    failures.push(`${rel}: correction rules/plan UI is not allowed in V1.0-M4`);
  }
  if (/graph (edit|editing|delete|merge|mutation)|edit graph|delete graph|merge graph/i.test(text)) {
    failures.push(`${rel}: graph mutation UI is not allowed in V1.0-M4`);
  }
}

if (failures.length > 0) {
  console.error(failures.join('\n'));
  process.exit(1);
}

console.log('Boundary checks passed');
