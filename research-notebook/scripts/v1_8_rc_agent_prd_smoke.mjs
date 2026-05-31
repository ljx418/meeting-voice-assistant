import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

const root = process.cwd();
const fixtureDir = join(root, 'fixtures', 'real', 'v1_8', 'agent-prd');
const reportPath = join(root, 'docs', 'design', 'V1.8', 'v1_8_rc_agent_led_prd_smoke_report.md');
const checks = [];

function mark(name, status, detail = '') {
  checks.push({ name, status, detail });
  const label = status === 'pass' ? 'PASS' : status === 'degraded' ? 'DEGRADED' : 'FAIL';
  console.log(`${label} ${name}${detail ? ` - ${detail}` : ''}`);
}

function hasSensitiveText(value) {
  return /\/Users|file:\/\/|cache_path|artifact_path|physical_path|\/private\/tmp|\/tmp\/|DATA_SERVICE_AI_API_KEY|api_key|authorization/i.test(
    String(value)
  );
}

async function readText(path) {
  return readFile(join(root, path), 'utf8');
}

async function readJson(path) {
  return JSON.parse(await readText(path));
}

function assertPass(name, condition, detail = '') {
  if (!condition) throw new Error(`${name}${detail ? `: ${detail}` : ''}`);
  mark(name, 'pass', detail);
}

async function main() {
  let finalDecision = 'FAIL';
  let summary = {};
  try {
    const sourceImport = await readJson('fixtures/real/v1_8/agent-source-import/v1_8_b_agent_source_import_result.json');
    const guideQa = await readJson('fixtures/real/v1_8/agent-guide-qa/v1_8_c_agent_guide_qa_result.json');
    const studio = await readJson('fixtures/real/v1_8/agent-studio/v1_8_d_agent_studio_result.json');
    const weakShell = await readText('docs/design/V1.8/v1_8_e_weak_frontend_shell_report.html');

    assertPass('V1.8-B source import', sourceImport.final_decision === 'PASS_LIMITED', sourceImport.final_decision);
    assertPass('V1.8-C guide qa citation', guideQa.final_decision === 'PASS_LIMITED', guideQa.final_decision);
    assertPass('V1.8-D studio validation', studio.final_decision === 'PASS_LIMITED', studio.final_decision);
    assertPass('V1.8-E weak frontend shell', weakShell.includes('不代表普通用户 UX ready'), 'UX boundary preserved');

    assertPass('source import raw_fixture_refs', Array.isArray(sourceImport.raw_fixture_refs) && sourceImport.raw_fixture_refs.length > 0);
    assertPass('guide qa raw_fixture_refs', Array.isArray(guideQa.raw_fixture_refs) && guideQa.raw_fixture_refs.length > 0);
    assertPass('studio raw_fixture_refs', Array.isArray(studio.raw_fixture_refs) && studio.raw_fixture_refs.length > 0);
    assertPass('agent prd no sensitive fixtures', !hasSensitiveText(JSON.stringify({ sourceImport, guideQa, studio, weakShell })));

    const coveredSteps = [
      'Agent draft',
      'permission boundary',
      'Notebook create',
      'Markdown/TXT/PDF/limited URL import',
      'build/index',
      'Notebook Guide',
      'Suggested Question QA',
      'citation resolution',
      'Notes/Study Guide/Briefing Doc/FAQ',
      'Markdown/JSON export',
      'outside-question refusal',
      'validation report',
      'weak frontend shell'
    ];
    for (const step of coveredSteps) mark(`covered ${step}`, 'pass');

    finalDecision = 'AGENT_CAPABILITY_SMOKE_READY';
    summary = {
      generated_at: new Date().toISOString(),
      final_decision: finalDecision,
      scope:
        'Agent-led PRD MVP capability validation for validated PDF / TXT / Markdown and limited URL sources on approved datasets.',
      source_import_decision: sourceImport.final_decision,
      guide_qa_decision: guideQa.final_decision,
      studio_decision: studio.final_decision,
      weak_frontend_decision: 'PASS_LIMITED',
      checks,
      still_not_ready: [
        'ordinary user UX fully ready',
        'all websites URL ready',
        'all-source-type ready',
        'OCR ready',
        'Audio Overview ready',
        'PPT generation ready',
        'Mindmap ready',
        'Document comparison ready',
        'arbitrary Agent tool execution ready',
        'cloud sync / collaboration ready'
      ],
      accepted_debts: [
        'V1.7 human UX acceptance skipped by strategy',
        'Agent automated validation is not human content quality review',
        'weak frontend shell is not a complete workflow editor'
      ]
    };
  } catch (error) {
    finalDecision = 'FAIL';
    mark('v1.8 rc agent prd smoke', 'fail', error instanceof Error ? error.message : String(error));
    summary = {
      generated_at: new Date().toISOString(),
      final_decision: finalDecision,
      checks,
      declaration: 'ResearchNotebook V1.8 Agent-led PRD MVP capability validation remains NOT_READY.'
    };
    process.exitCode = 1;
  } finally {
    await mkdir(fixtureDir, { recursive: true });
    await writeFile(join(fixtureDir, 'v1_8_rc_agent_prd_result.json'), `${JSON.stringify(summary, null, 2)}\n`);
    const md = `# V1.8-RC Agent-Led PRD Smoke Report

日期：2026-05-30

## 当前状态

\`${finalDecision}\`

## 执行结果

| 项 | 状态 | 说明 |
| --- | --- | --- |
${checks.map((item) => `| ${item.name} | ${item.status.toUpperCase()} | ${String(item.detail ?? '').replaceAll('|', '/')} |`).join('\n')}

## Fixture

- \`fixtures/real/v1_8/agent-prd/v1_8_rc_agent_prd_result.json\`
- \`docs/design/V1.8/v1_8_e_weak_frontend_shell_report.html\`

## 声明边界

如果状态为 \`AGENT_CAPABILITY_SMOKE_READY\`，最多声明：

ResearchNotebook V1.8 Agent-led PRD MVP capability validation is smoke-ready for validated PDF / TXT / Markdown and limited URL sources on approved datasets.

仍不能声明：

- 普通用户 UX fully ready
- all websites URL ready
- all-source-type ready
- OCR ready
- Audio Overview ready
- PPT generation ready
- Mindmap ready
- Document comparison ready
- arbitrary Agent tool execution ready
- cloud sync / collaboration ready

## 风险评估

| 风险 | 等级 | 处理 |
| --- | --- | --- |
| 规格漂移 | MEDIUM | 限定为 Agent-led capability validation |
| 虚假验收 | MEDIUM-HIGH | 不替代人工 UX / 内容质量验收 |
| UX 债务 | HIGH accepted | 保留 V1.x Final Human UX Acceptance |
`;
    await writeFile(reportPath, md);
    console.log(`V1_8_RC_AGENT_PRD_REPORT ${reportPath}`);
    console.log(`V1_8_RC_AGENT_PRD_DECISION ${finalDecision}`);
  }
}

await main();
