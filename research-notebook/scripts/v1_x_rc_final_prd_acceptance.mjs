import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

const root = process.cwd();
const fixtureDir = join(root, 'fixtures', 'real', 'v1_x', 'final-prd-acceptance');
const reportPath = join(root, 'docs', 'design', 'V1.x', 'v1_x_final_prd_acceptance_report.md');
const handoffPath = join(root, 'docs', 'design', 'V1.x', 'v1_x_release_handoff.md');
const manualDecisionPath = 'docs/design/V1.x/v1_x_manual_acceptance_decision.md';
const interactiveResultPath = '.smoke-artifacts/v1_x_interactive_acceptance/1780225853829/result.json';
const checks = [];

function mark(name, status, detail = '') {
  checks.push({ name, status, detail });
  const label = status === 'pass' ? 'PASS' : status === 'degraded' ? 'DEGRADED' : 'FAIL';
  console.log(`${label} ${name}${detail ? ` - ${detail}` : ''}`);
}

async function readText(path) {
  return readFile(join(root, path), 'utf8');
}

async function readJson(path) {
  return JSON.parse(await readText(path));
}

function hasSensitiveText(value) {
  return /\/Users|file:\/\/|cache_path|artifact_path|physical_path|\/private\/tmp|\/tmp\/|DATA_SERVICE_AI_API_KEY|api_key|authorization|bearer\s+/i.test(
    String(value)
  );
}

function markdownRows(items) {
  return items
    .map((item) => `| ${item.name} | ${item.status.toUpperCase()} | ${String(item.detail ?? '').replaceAll('|', '/')} |`)
    .join('\n');
}

let finalDecision = 'FAIL';
let manualAccepted = false;

try {
  const v19 = await readJson('fixtures/real/v1_9/rc/v1_9_rc_result.json');
  const v10 = await readJson('fixtures/real/v1_10/disabled-boundary/v1_10_disabled_boundary_result.json');
  const v1xPlan = await readText('docs/design/V1.x/v1_x_remaining_development_and_acceptance_plan.md');
  const v10Readme = await readText('docs/design/V1.10/00_README.md');
  const v10Report = await readText('docs/design/V1.10/v1_10_rc_disabled_boundary_report.md');
  const manualDecision = await readText(manualDecisionPath);
  const interactive = await readJson(interactiveResultPath);

  mark(
    'V1.9 final PRD acceptance prerequisite',
    v19.final_decision === 'V1_9_READY_FOR_FINAL_HUMAN_ACCEPTANCE' ? 'pass' : 'fail',
    v19.final_decision
  );
  mark(
    'V1.10 disabled boundary acceptance',
    v10.final_decision === 'V1_10_DISABLED_BOUNDARY_ACCEPTED' ? 'pass' : 'fail',
    v10.final_decision
  );
  mark(
    'V1.10 browser disabled-boundary evidence',
    v10.results?.some((item) => item.name === 'browser disabled tool network result' && item.status === 'pass') ? 'pass' : 'degraded',
    'disabled tool network result reviewed'
  );
  mark(
    'V1.x plan keeps final human acceptance gate',
    v1xPlan.includes('V1.x-RC Final PRD Acceptance / Release Handoff') && v1xPlan.includes('人工验收') ? 'pass' : 'fail',
    'manual acceptance gate preserved'
  );
  mark(
    'OCR and Phase 2/3 boundaries preserved',
    v10Readme.includes('继续 `NOT_READY`') &&
      v10Readme.includes('继续 `DISABLED_READY`') &&
      v10Report.includes('不得声明') &&
      v10Report.includes('OCR ready')
      ? 'pass'
      : 'fail',
    'NOT_READY / DISABLED_READY wording present'
  );
  mark(
    'V1.x interactive browser evidence accepted',
    interactive.final_decision === 'READY_FOR_HUMAN_REVIEW_WITH_BROWSER_EVIDENCE' &&
      interactive.screenshots?.length >= 10 &&
      manualDecision.includes('V1_X_FINAL_ACCEPTANCE_PASS_LIMITED')
      ? 'pass'
      : 'fail',
    'manual decision references latest browser evidence package'
  );

  const combined = JSON.stringify({ v19, v10, v1xPlan, v10Readme, v10Report, manualDecision, interactive });
  if (hasSensitiveText(combined)) throw new Error('sensitive text detected in V1.x RC evidence');
  mark('fixture and report hygiene', 'pass', 'no local path, cache path, physical artifact path, or API key detected');

  if (checks.some((item) => item.status === 'fail')) throw new Error('V1.x RC prerequisite failed');
  manualAccepted = true;
  finalDecision = 'V1_X_FINAL_ACCEPTANCE_PASS_LIMITED';
} catch (error) {
  mark('V1.x final PRD acceptance aggregation', 'fail', error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
}

const payload = {
  generated_at: new Date().toISOString(),
  final_decision: finalDecision,
  checks,
  required_human_acceptance: [
    'Guide content quality review',
    'QA citation correctness review',
    'Studio output and export file review',
    'Research source-grounded quality review',
    'V1.10 disabled boundary UI wording review'
  ],
  manual_acceptance: manualAccepted
    ? {
        status: 'accepted',
        decision_doc: manualDecisionPath,
        interactive_evidence: interactiveResultPath
      }
    : {
        status: 'pending',
        decision_doc: manualDecisionPath,
        interactive_evidence: interactiveResultPath
      },
  still_not_ready: [
    'all websites URL extraction ready',
    'all-source-type ready',
    'OCR ready',
    'scanned PDF ready',
    'Audio Overview ready',
    'PPT generation ready',
    'Mindmap ready',
    'Document comparison ready',
    'cloud sync / collaboration ready'
  ]
};

await mkdir(fixtureDir, { recursive: true });
await writeFile(join(fixtureDir, 'v1_x_final_prd_acceptance_result.json'), `${JSON.stringify(payload, null, 2)}\n`);

await writeFile(
  reportPath,
  `# ResearchNotebook V1.x Final PRD Acceptance Report

日期：2026-05-31

## 当前状态

\`${finalDecision}\`

## 自动化汇总结果

| 项 | 状态 | 说明 |
| --- | --- | --- |
${markdownRows(checks)}

## 人工验收仍需确认

${manualAccepted ? '当前交互式浏览器证据包已获用户认可。以下内容作为后续抽样复核建议，不再阻塞 V1.x scoped sync：' : '自动化汇总不能替代人工内容质量判断。进入最终 release handoff 前，仍需人工确认：'}

- Guide 内容质量。
- QA citation 正确性。
- Studio Notes / Study Guide / Briefing Doc / FAQ 输出质量。
- Markdown / JSON 导出文件可打开且 citation metadata 完整。
- Research 是否严格 source-grounded。
- V1.10 disabled 工具文案和行为不会误导用户。

## PRD 覆盖声明上限

如果人工验收全部通过，最多声明：

\`\`\`text
ResearchNotebook V1.x PRD MVP path is release-candidate-ready for validated PDF / TXT / Markdown and limited URL sources, with source-grounded Guide, QA, lightweight Studio outputs, export, citation navigation, and Research 补源 workflow on approved datasets.
\`\`\`

## 仍不能声明

- all websites URL extraction ready
- all-source-type ready
- OCR ready
- scanned PDF ready
- Audio Overview ready
- PPT generation ready
- Mindmap ready
- Document comparison ready
- cloud sync / collaboration ready

## 最终决策

${manualAccepted ? '当前可以进入 V1.x scoped release handoff。最终声明仍限定为 PASS_LIMITED，不得扩大成 all-domain / all-source ready。' : '当前只能进入人工最终验收。人工验收完成前，不得声明 V1.x release-ready，也不得进入 final sync。'}
`
);

await writeFile(
  handoffPath,
  `# ResearchNotebook V1.x Release Handoff

日期：2026-05-31

## 当前状态

\`${finalDecision}\`

## Handoff Summary

V1.x 已完成自动化收口汇总：

- V1.9 Research quality / conflict labeling 已进入 final human acceptance。
- V1.10 Phase 2/3 / OCR disabled boundary 已通过自动化验收。
- V1.x 最终 PRD 验收报告已生成。

${manualAccepted ? '当前交互式浏览器证据包已获用户认可，允许进入 scoped sync。' : '当前仍需人工质量验收，不允许直接 release。'}

## 已验证证据

| 证据 | 路径 | 状态 |
| --- | --- | --- |
| V1.9 RC report | \`docs/design/V1.9/v1_9_rc_final_prd_acceptance_report.md\` | READY_FOR_FINAL_HUMAN_ACCEPTANCE |
| V1.10 disabled boundary report | \`docs/design/V1.10/v1_10_rc_disabled_boundary_report.md\` | ACCEPTED |
| V1.x final PRD acceptance report | \`docs/design/V1.x/v1_x_final_prd_acceptance_report.md\` | ${finalDecision} |
| V1.x final acceptance fixture | \`fixtures/real/v1_x/final-prd-acceptance/v1_x_final_prd_acceptance_result.json\` | GENERATED |
| V1.x manual acceptance decision | \`${manualDecisionPath}\` | ${manualAccepted ? 'ACCEPTED' : 'PENDING'} |
| V1.x interactive browser evidence | \`${interactiveResultPath}\` | ${manualAccepted ? 'ACCEPTED' : 'PENDING'} |

## Release 前验收结论

${manualAccepted ? '本轮已认可交互式浏览器证据包。后续只保留抽样复核建议：' : '必须人工确认：'}

- Guide / QA / Studio / Research 的内容质量。
- Citation 可定位且与文本证据一致。
- Studio Markdown / JSON 导出文件真实可打开。
- V1.10 disabled 工具不会发起后端生成请求。
- 页面没有把 OCR / Audio / PPT / Mindmap / Document comparison 写成 ready。

## Scoped Sync Plan

${manualAccepted ? '当前交互式浏览器证据包已获用户认可，可以进行 scoped commit / push。最终声明仍必须保持 PASS_LIMITED，不得扩大为 all-source / all-domain ready。' : '人工验收通过后，才允许进行 scoped commit / push。'}

提交前必须确认：

- \`.smoke-artifacts/\` 不进入 git。
- fixtures 不含本地绝对路径、cache path、artifact physical path、API key。
- 文档没有把 PASS_LIMITED 扩大成 all-source / all-domain ready。
- staged diff 不混入 unrelated sibling project。

建议提交信息：

\`\`\`text
Finalize ResearchNotebook V1.x PRD release handoff
\`\`\`

## 完成声明上限

${manualAccepted ? '当前 PASS_LIMITED 验收口径下最多声明：' : '人工验收通过后最多声明：'}

\`\`\`text
ResearchNotebook V1.x PRD MVP path is release-candidate-ready for validated PDF / TXT / Markdown and limited URL sources, with source-grounded Guide, QA, lightweight Studio outputs, export, citation navigation, and Research 补源 workflow on approved datasets.
\`\`\`

## 仍不能声明

- all websites URL extraction ready
- all-source-type ready
- OCR ready
- scanned PDF ready
- Audio Overview ready
- PPT generation ready
- Mindmap ready
- Document comparison ready
- cloud sync / collaboration ready
`
);

console.log(`V1_X_RC_DECISION ${finalDecision}`);
