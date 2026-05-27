import type { Meta, StoryObj } from "@storybook/react";
import "./tokens.css";
import "./components.css";

const COLORS = [
  ["background.page", "var(--hos-bg-page)"],
  ["background.canvas", "var(--hos-bg-canvas)"],
  ["background.panel", "var(--hos-bg-panel)"],
  ["background.subtle", "var(--hos-bg-subtle)"],
  ["accent.blue", "var(--hos-accent-blue)"],
  ["accent.violet", "var(--hos-accent-violet)"],
  ["accent.cyan", "var(--hos-accent-cyan)"],
  ["status.running", "var(--hos-status-running)"],
  ["status.completed", "var(--hos-status-completed)"],
  ["status.failed", "var(--hos-status-failed)"],
  ["status.warning", "var(--hos-status-warning)"],
  ["status.waiting", "var(--hos-status-waiting)"],
];

function TokenPreview() {
  return (
    <main style={{ background: "var(--hos-bg-page)", minHeight: "100vh", padding: "var(--hos-space-6)" }}>
      <h1>Design Tokens Preview</h1>
      <section style={{ display: "grid", gap: "var(--hos-space-3)", gridTemplateColumns: "repeat(4, minmax(0, 1fr))" }}>
        {COLORS.map(([name, color]) => (
          <article key={name} className="hos-card">
            <div style={{ background: color, border: "1px solid var(--hos-border-default)", borderRadius: "var(--hos-radius-small)", height: 56 }} />
            <strong>{name}</strong>
            <p className="hos-muted hos-mono">{color}</p>
          </article>
        ))}
      </section>
      <section className="hos-card" style={{ marginTop: "var(--hos-space-6)" }}>
        <h2>Typography</h2>
        <p style={{ fontSize: "var(--hos-text-page-title)", lineHeight: "var(--hos-leading-page-title)", fontWeight: 600 }}>页面标题 20/28/600</p>
        <p style={{ fontSize: "var(--hos-text-section-title)", lineHeight: "var(--hos-leading-section-title)", fontWeight: 600 }}>区块标题 16/24/600</p>
        <p style={{ fontSize: "var(--hos-text-body)", lineHeight: "var(--hos-leading-body)" }}>正文 14/22/400：用于中文工作台主体内容。</p>
        <p className="hos-mono">artifact_id: art_folder_summary_001</p>
      </section>
    </main>
  );
}

const meta = {
  title: "Design System/Tokens",
  component: TokenPreview,
} satisfies Meta<typeof TokenPreview>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Preview: Story = {};
