import { readFile } from 'node:fs/promises';

const checks = [];

function mark(name, pass, detail = '') {
  checks.push({ name, status: pass ? 'PASS' : 'FAIL', detail });
  console.log(`${pass ? 'PASS' : 'FAIL'} ${name}${detail ? ` - ${detail}` : ''}`);
}

function containsAny(text, patterns) {
  return patterns.some((pattern) => (typeof pattern === 'string' ? text.includes(pattern) : pattern.test(text)));
}

const workspacePage = await readFile('src/features/workspaces/WorkspacePage.tsx', 'utf8');
const evidenceList = await readFile('src/shared/components/EvidenceList.tsx', 'utf8');
const previewDrawer = await readFile('src/shared/components/SourcePreviewDrawer.tsx', 'utf8');
const css = await readFile('src/shared/design-system/global.css', 'utf8');
const v17Gap = await readFile('docs/design/V1.7/v1_7_current_gap_analysis.md', 'utf8');

mark('V1.7 docs exist', v17Gap.includes('V1.7'));
mark('main workspace has three-column layout', workspacePage.includes('notebook-three-column'));
mark('main Studio column uses user-facing output label', workspacePage.includes('id="studio-title">输出</h2>'));
mark('Notebook Guide label is Chinese', workspacePage.includes('资料导读'));
mark('Chat submit label is user-facing', workspacePage.includes('发送问题'));
mark('Agent workflow panel is not mounted in main workspace', !workspacePage.includes('<AgentWorkflowPanel'));
mark('source import only exposes validated source types', !containsAny(workspacePage, ['PPTX：', '视频：', '音频：', 'JSON：已验证']));
mark('Studio tools are Chinese', containsAny(workspacePage, ['title: \'笔记\'', 'title: \'学习导读\'', 'title: \'资料简报\'', 'title: \'常见问题\'']));
mark('Phase 2/3 tools are disabled-facing', workspacePage.includes('暂不可用') && workspacePage.includes('后续输出工具'));
mark('Evidence chips hide backend unit/evidence labels', !containsAny(evidenceList, ['文档单元：', '证据片段：']));
mark('SourcePreviewDrawer keeps backend ids inside debug details', previewDrawer.includes('<summary>调试信息</summary>'));
mark('desktop grid gives Chat a stable center column', css.includes('minmax(440px, 1fr)'));
mark('mobile layout falls back to one column', css.includes('@media (max-width: 760px)') && css.includes('grid-template-columns: 1fr'));

const failed = checks.filter((check) => check.status === 'FAIL');
if (failed.length) {
  console.error(`V1.7 UX smoke failed: ${failed.map((check) => check.name).join(', ')}`);
  process.exit(1);
}

console.log('V1_7_UX_SMOKE_DECISION PASS');
