import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { join } from 'node:path';

const root = process.cwd();
const fixtureDir = join(root, 'fixtures', 'real', 'v1_9', 'rc');
const reportPath = join(root, 'docs', 'design', 'V1.9', 'v1_9_rc_final_prd_acceptance_report.md');
const checks = [];

function mark(name, status, detail = '') {
  checks.push({ name, status, detail });
  console.log(`${status === 'pass' ? 'PASS' : status === 'degraded' ? 'DEGRADED' : 'FAIL'} ${name}${detail ? ` - ${detail}` : ''}`);
}

async function readJson(path) {
  return JSON.parse(await readFile(join(root, path), 'utf8'));
}

function hasSensitiveText(value) {
  return /\/Users|file:\/\/|cache_path|artifact_path|physical_path|\/private\/tmp|\/tmp\/|DATA_SERVICE_AI_API_KEY|api_key|authorization/i.test(String(value));
}

let finalDecision = 'FAIL';

try {
  const research = await readJson('fixtures/real/v1_9/research-quality/v1_9_a_research_quality_result.json');
  const conflict = await readJson('fixtures/real/v1_9/conflict-labeling/v1_9_b_conflict_labeling_result.json');
  const human = await readJson('docs/design/V1.9/v1_9_c_human_ux_acceptance_result.json');
  mark('V1.9-A research quality', research.final_decision === 'PASS_LIMITED' ? 'pass' : 'fail', research.final_decision);
  mark('V1.9-B conflict labeling', conflict.final_decision === 'PASS_LIMITED' ? 'pass' : 'fail', conflict.final_decision);
  mark('V1.9-C human UX package', human.final_decision === 'READY_FOR_HUMAN_ACCEPTANCE' ? 'pass' : 'fail', human.final_decision);
  if (checks.some((item) => item.status === 'fail')) throw new Error('V1.9 prerequisite failed');
  if (hasSensitiveText(JSON.stringify({ research, conflict, human }))) throw new Error('V1.9 RC sensitive text detected');
  mark('V1.9 hygiene', 'pass', 'sanitized');
  finalDecision = 'V1_9_READY_FOR_FINAL_HUMAN_ACCEPTANCE';
} catch (error) {
  mark('V1.9 RC', 'fail', error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
}

await mkdir(fixtureDir, { recursive: true });
await writeFile(join(fixtureDir, 'v1_9_rc_result.json'), `${JSON.stringify({ generated_at: new Date().toISOString(), final_decision: finalDecision, checks }, null, 2)}\n`);
await writeFile(
  reportPath,
  `# V1.9-RC Final PRD Acceptance Report

日期：2026-05-30

## 当前状态

\`${finalDecision}\`

## 检查结果

| 项 | 状态 | 说明 |
| --- | --- | --- |
${checks.map((item) => `| ${item.name} | ${item.status.toUpperCase()} | ${String(item.detail ?? '').replaceAll('|', '/')} |`).join('\n')}

## 声明边界

V1.9 完成后仍需人工填写 UX / 内容质量结论。自动化最多证明 Research quality、conflict labeling 和人工验收包已经准备就绪。

仍不能声明 all-domain、all-source-type、OCR、Audio、PPT、Mindmap、Document comparison、cloud sync / collaboration ready。
`
);
console.log(`V1_9_RC_DECISION ${finalDecision}`);
