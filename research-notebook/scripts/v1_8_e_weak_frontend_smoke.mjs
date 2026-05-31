import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

const root = process.cwd();
const reportPath = join(root, 'docs', 'design', 'V1.8', 'v1_8_e_weak_frontend_shell_report.html');
const fixtureRoot = join(root, 'fixtures', 'real', 'v1_8');
const results = [];

function mark(name, status, detail = '') {
  results.push({ name, status, detail });
  const label = status === 'pass' ? 'PASS' : status === 'degraded' ? 'DEGRADED' : 'FAIL';
  console.log(`${label} ${name}${detail ? ` - ${detail}` : ''}`);
}

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function hasSensitiveText(value) {
  return /\/Users|file:\/\/|cache_path|artifact_path|physical_path|\/private\/tmp|\/tmp\/|DATA_SERVICE_AI_API_KEY|api_key|authorization/i.test(
    String(value)
  );
}

async function readJson(relativePath) {
  const text = await readFile(join(fixtureRoot, relativePath), 'utf8');
  return JSON.parse(text);
}

function statusBadge(status) {
  const normalized = String(status ?? 'unknown').toUpperCase();
  const kind = normalized.includes('PASS') || normalized === 'COMPLETED' ? 'pass' : normalized.includes('DEGRADED') ? 'degraded' : 'neutral';
  return `<span class="badge ${kind}">${escapeHtml(normalized)}</span>`;
}

function resultRows(items = []) {
  return items
    .slice(0, 18)
    .map(
      (item) => `<tr><td>${escapeHtml(item.name ?? item.step_id)}</td><td>${statusBadge(item.status)}</td><td>${escapeHtml(item.detail ?? item.output_summary?.detail ?? '')}</td></tr>`
    )
    .join('\n');
}

function assertionsRows(items = []) {
  return items
    .slice(0, 18)
    .map(
      (item) =>
        `<tr><td>${escapeHtml(item.name)}</td><td>${statusBadge(item.status)}</td><td>${escapeHtml(item.expected)}</td><td>${escapeHtml(item.actual)}</td><td>${escapeHtml(item.evidence_ref ?? '')}</td></tr>`
    )
    .join('\n');
}

function buildHtml(sourceImport, guideQa, studio) {
  const generatedAt = new Date().toISOString();
  const sourceDecision = sourceImport.final_decision;
  const guideDecision = guideQa.final_decision;
  const studioDecision = studio.final_decision;
  const sourceSteps = sourceImport.step_results ?? [];
  const guideSteps = guideQa.step_results ?? [];
  const studioSteps = studio.step_results ?? [];
  const sourceAssertions = sourceImport.assertions ?? [];
  const guideAssertions = guideQa.assertions ?? [];
  const studioAssertions = studio.assertions ?? [];
  const rawFixtureRefs = [
    ...(sourceImport.raw_fixture_refs ?? []).map((item) => `agent-source-import/${item}`),
    ...(guideQa.raw_fixture_refs ?? []).map((item) => `agent-guide-qa/${item}`),
    ...(studio.raw_fixture_refs ?? []).map((item) => `agent-studio/${item}`)
  ];

  return `<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>ResearchNotebook V1.8-E Agent 验收展示壳</title>
  <style>
    :root {
      color-scheme: light;
      font-family: Inter, "PingFang SC", "Microsoft YaHei", Arial, sans-serif;
      color: #17202a;
      background: #f6f8fb;
    }
    body { margin: 0; }
    header {
      padding: 28px clamp(20px, 4vw, 48px);
      background: #ffffff;
      border-bottom: 1px solid #d9e2ec;
    }
    main {
      width: min(1280px, calc(100vw - 32px));
      margin: 24px auto 48px;
      display: grid;
      gap: 16px;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 16px;
      align-items: start;
    }
    section {
      background: #ffffff;
      border: 1px solid #d9e2ec;
      border-radius: 8px;
      padding: 16px;
      min-width: 0;
    }
    h1, h2, h3 { margin: 0 0 10px; line-height: 1.25; }
    p { line-height: 1.65; margin: 0 0 10px; }
    .muted { color: #5c6f82; }
    .badge {
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      padding: 2px 8px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 700;
      background: #edf2f7;
      color: #2d3748;
      white-space: nowrap;
    }
    .badge.pass { background: #e3f5ea; color: #176a3a; }
    .badge.degraded { background: #fff3d6; color: #8a5a00; }
    .badges { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0 0; }
    table { width: 100%; border-collapse: collapse; table-layout: fixed; }
    th, td { border-bottom: 1px solid #e6edf5; padding: 8px; text-align: left; vertical-align: top; overflow-wrap: anywhere; }
    th { font-size: 12px; color: #526273; background: #f8fafc; }
    .full { grid-column: 1 / -1; }
    .timeline { display: grid; gap: 8px; }
    .timeline div { border-left: 3px solid #2274a5; padding: 4px 0 4px 10px; }
    .callout { background: #f8fafc; border-color: #cbd5e1; }
    @media (max-width: 960px) {
      .grid { grid-template-columns: 1fr; }
      main { width: min(100vw - 20px, 760px); }
    }
  </style>
</head>
<body>
  <header>
    <h1>ResearchNotebook V1.8-E Agent 验收展示壳</h1>
    <p class="muted">生成时间：${escapeHtml(generatedAt)}。该页面用于展示 Agent-led validation results，不是完整 workflow editor，也不代表普通用户 UX ready。</p>
    <div class="badges">
      <span>Source Import ${statusBadge(sourceDecision)}</span>
      <span>Guide / QA ${statusBadge(guideDecision)}</span>
      <span>Studio ${statusBadge(studioDecision)}</span>
    </div>
  </header>
  <main>
    <section class="full callout">
      <h2>Agent 计划与授权</h2>
      <p>任务：递归处理数字人资料，导入 Markdown / TXT / PDF / limited URL，验证 Guide、引用问答、Studio 输出和导出。</p>
      <p>授权：fixtures 只保存 target_path_labels / target_path_refs；未授权前不得 scan / import / source read。</p>
      <p>边界：弱前端只展示 draft、运行状态、结果摘要和失败原因，不承担完整工作流编辑器职责。</p>
    </section>
    <div class="grid">
      <section>
        <h2>来源导入汇总</h2>
        <p>最终结论：${statusBadge(sourceDecision)}</p>
        <div class="timeline">
          <div>Markdown / TXT / PDF / limited URL 导入</div>
          <div>失败 URL 稳定降级，不中断 workflow</div>
          <div>fixture 脱敏保存</div>
        </div>
      </section>
      <section>
        <h2>Guide / QA 验证</h2>
        <p>最终结论：${statusBadge(guideDecision)}</p>
        <div class="timeline">
          <div>Notebook Guide 结构与 evidence_refs</div>
          <div>Suggested Question 与覆盖型 QA</div>
          <div>资料外问题 source-grounded refusal</div>
        </div>
      </section>
      <section>
        <h2>Studio 验证</h2>
        <p>最终结论：${statusBadge(studioDecision)}</p>
        <div class="timeline">
          <div>Notes / Study Guide / Briefing Doc / FAQ</div>
          <div>DocumentUnit / EvidenceSpan citation 解析</div>
          <div>Markdown / JSON export</div>
        </div>
      </section>
    </div>
    <section class="full">
      <h2>运行状态</h2>
      <table>
        <thead><tr><th>Step</th><th>Status</th><th>Detail</th></tr></thead>
        <tbody>${resultRows([...sourceSteps, ...guideSteps, ...studioSteps])}</tbody>
      </table>
    </section>
    <section class="full">
      <h2>断言与证据入口</h2>
      <table>
        <thead><tr><th>Assertion</th><th>Status</th><th>Expected</th><th>Actual</th><th>Evidence</th></tr></thead>
        <tbody>${assertionsRows([...sourceAssertions, ...guideAssertions, ...studioAssertions])}</tbody>
      </table>
    </section>
    <section class="full">
      <h2>错误与恢复建议</h2>
      <p>已记录 provider/schema 波动、stable failing URL、弱前端 UX debt。若任一 validation report 为 FAIL，应回到对应阶段重新执行，不得直接进入 RC。</p>
      <p>恢复建议：先复跑对应 smoke；若仍失败，定位到 source import、Guide/QA、Studio 或 provider schema prompt 修复。</p>
    </section>
    <section class="full">
      <h2>Fixture 索引</h2>
      <p class="muted">${escapeHtml(rawFixtureRefs.slice(0, 40).join(' | '))}</p>
    </section>
  </main>
</body>
</html>`;
}

function assertHtml(html) {
  const checks = [
    ['Agent 计划', html.includes('Agent 计划与授权')],
    ['授权确认', html.includes('未授权前不得 scan')],
    ['运行状态', html.includes('运行状态')],
    ['来源导入汇总', html.includes('来源导入汇总')],
    ['Guide / QA 验证', html.includes('Guide / QA 验证')],
    ['Studio 验证', html.includes('Studio 验证')],
    ['错误与恢复建议', html.includes('错误与恢复建议')],
    ['证据入口', html.includes('断言与证据入口')],
    ['不声明 UX ready', html.includes('不代表普通用户 UX ready')]
  ];
  for (const [name, ok] of checks) {
    if (!ok) throw new Error(`weak frontend shell missing ${name}`);
    mark(`weak shell contains ${name}`, 'pass');
  }
  if (hasSensitiveText(html)) throw new Error('weak frontend shell contains sensitive path or secret marker');
  mark('weak shell hygiene', 'pass', 'sanitized');
}

async function main() {
  try {
    const sourceImport = await readJson(join('agent-source-import', 'v1_8_b_agent_source_import_result.json'));
    const guideQa = await readJson(join('agent-guide-qa', 'v1_8_c_agent_guide_qa_result.json'));
    const studio = await readJson(join('agent-studio', 'v1_8_d_agent_studio_result.json'));
    const html = buildHtml(sourceImport, guideQa, studio);
    assertHtml(html);
    await mkdir(join(root, 'docs', 'design', 'V1.8'), { recursive: true });
    await writeFile(reportPath, html);
    console.log(`V1_8_E_WEAK_FRONTEND_REPORT ${reportPath}`);
    console.log('V1_8_E_WEAK_FRONTEND_DECISION PASS_LIMITED');
  } catch (error) {
    mark('v1.8-e weak frontend smoke', 'fail', error instanceof Error ? error.message : String(error));
    console.log('V1_8_E_WEAK_FRONTEND_DECISION FAIL');
    process.exitCode = 1;
  }
}

await main();
