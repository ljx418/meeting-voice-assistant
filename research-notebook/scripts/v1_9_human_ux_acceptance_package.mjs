import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

const root = process.cwd();
const reportPath = join(root, 'docs', 'design', 'V1.9', 'v1_9_c_human_ux_acceptance_report.html');

function escapeHtml(value) {
  return String(value ?? '').replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
}

function hasSensitiveText(value) {
  return /\/Users|file:\/\/|cache_path|artifact_path|physical_path|\/private\/tmp|\/tmp\/|DATA_SERVICE_AI_API_KEY|api_key|authorization/i.test(String(value));
}

async function readMaybe(path) {
  try {
    return await readFile(join(root, path), 'utf8');
  } catch {
    return '';
  }
}

async function main() {
  const v18 = await readMaybe('docs/design/V1.8/v1_8_rc_agent_led_prd_smoke_report.md');
  const v19a = await readMaybe('fixtures/real/v1_9/research-quality/v1_9_a_research_quality_result.json');
  const v19b = await readMaybe('fixtures/real/v1_9/conflict-labeling/v1_9_b_conflict_labeling_result.json');
  const html = `<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>ResearchNotebook V1.9 人工 UX 验收包</title>
  <style>
    body { margin: 0; font-family: "PingFang SC", "Microsoft YaHei", Arial, sans-serif; background: #f6f8fb; color: #17202a; }
    main { width: min(1180px, calc(100vw - 32px)); margin: 24px auto 48px; display: grid; gap: 16px; }
    header, section { background: #fff; border: 1px solid #d9e2ec; border-radius: 8px; padding: 18px; }
    header { border-radius: 0; border-left: 0; border-right: 0; }
    h1, h2 { margin: 0 0 10px; }
    li { margin: 8px 0; }
    .grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
    .badge { display: inline-block; padding: 3px 8px; border-radius: 999px; background: #edf2f7; font-weight: 700; font-size: 12px; }
    textarea { width: 100%; min-height: 120px; border: 1px solid #cbd5e1; border-radius: 8px; padding: 10px; }
    @media (max-width: 820px) { .grid { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <header>
    <h1>ResearchNotebook V1.9 人工 UX 验收包</h1>
    <p>该页面用于人工验收，不自动声明 PASS。请验收者逐项填写 PASS / FAIL / NEEDS_FIX。</p>
  </header>
  <main>
    <section>
      <h2>验收路径</h2>
      <ol>
        <li>创建 Notebook。</li>
        <li>导入 Markdown / TXT / PDF。</li>
        <li>查看 Notebook Guide。</li>
        <li>点击 Suggested Question。</li>
        <li>查看引用问答并点击 citation。</li>
        <li>确认 SourcePreview / DocumentUnit / EvidenceSpan 定位。</li>
        <li>生成 Notes / Study Guide / Briefing Doc / FAQ。</li>
        <li>下载 Markdown / JSON。</li>
        <li>执行 Research 补源和冲突标注。</li>
        <li>确认 Phase 2/3 disabled。</li>
      </ol>
    </section>
    <div class="grid">
      <section>
        <h2>自动化证据</h2>
        <p><span class="badge">V1.8 RC</span></p>
        <pre>${escapeHtml(v18.slice(0, 1600))}</pre>
        <p><span class="badge">V1.9-A</span></p>
        <pre>${escapeHtml(v19a.slice(0, 1200))}</pre>
        <p><span class="badge">V1.9-B</span></p>
        <pre>${escapeHtml(v19b.slice(0, 1200))}</pre>
      </section>
      <section>
        <h2>人工结论填写</h2>
        <p>Guide 质量：PASS / FAIL / NEEDS_FIX</p>
        <p>引用问答质量：PASS / FAIL / NEEDS_FIX</p>
        <p>Studio 输出质量：PASS / FAIL / NEEDS_FIX</p>
        <p>Research 质量：PASS / FAIL / NEEDS_FIX</p>
        <p>冲突标注质量：PASS / FAIL / NEEDS_FIX</p>
        <p>页面可操作性：PASS / FAIL / NEEDS_FIX</p>
        <textarea placeholder="人工验收备注"></textarea>
      </section>
    </div>
    <section>
      <h2>不能声明</h2>
      <ul>
        <li>all-domain Research ready</li>
        <li>all-source-type ready</li>
        <li>OCR ready</li>
        <li>Audio / PPT / Mindmap / Document comparison ready</li>
        <li>cloud sync / collaboration ready</li>
      </ul>
    </section>
  </main>
</body>
</html>`;
  if (hasSensitiveText(html)) throw new Error('human UX package contains sensitive text');
  await mkdir(join(root, 'docs', 'design', 'V1.9'), { recursive: true });
  await writeFile(reportPath, html);
  await writeFile(
    join(root, 'docs', 'design', 'V1.9', 'v1_9_c_human_ux_acceptance_result.json'),
    `${JSON.stringify({ generated_at: new Date().toISOString(), final_decision: 'READY_FOR_HUMAN_ACCEPTANCE', report: 'docs/design/V1.9/v1_9_c_human_ux_acceptance_report.html' }, null, 2)}\n`
  );
  console.log(`V1_9_C_HUMAN_UX_PACKAGE ${reportPath}`);
  console.log('V1_9_C_HUMAN_UX_DECISION READY_FOR_HUMAN_ACCEPTANCE');
}

await main();
