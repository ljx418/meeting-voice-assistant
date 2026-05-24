import { NavLink, Outlet, useLocation } from 'react-router-dom';
import { BookOpen, CircleHelp, GitBranch, Home, MessageSquareText } from 'lucide-react';

const navItems = [
  { to: '/', label: '首页', icon: Home, end: true },
  { to: '/workbench', label: '会话工作台', icon: BookOpen },
  { to: '/graph', label: '知识图谱', icon: GitBranch },
  { to: '/feedback', label: '反馈', icon: MessageSquareText }
];

function statusLabel(pathname: string) {
  if (pathname.includes('/workbench')) return '会话工作台';
  if (pathname.includes('/graph')) return '知识图谱上下文';
  if (pathname.startsWith('/workspaces/')) return '工作区';
  if (pathname.startsWith('/feedback')) return '轻量反馈';
  return '工作区首页';
}

export function AppShell() {
  const location = useLocation();

  return (
    <div className="app-shell">
      <aside className="app-sidebar" aria-label="主导航">
        <div className="brand-block">
          <div className="brand-mark" aria-hidden="true">R</div>
          <div>
            <div className="brand-title">研究笔记</div>
            <div className="brand-subtitle">基于来源的个人研究工作区</div>
          </div>
        </div>
        <nav className="nav-list">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
              >
                <Icon size={18} aria-hidden="true" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
        <div className="sidebar-note">
          <CircleHelp size={16} aria-hidden="true" />
          <span>当前版本支持来源预览、证据定位、只读图谱上下文和轻量反馈；评估、治理、协作仍为后续能力。</span>
        </div>
      </aside>
      <main className="app-main">
        <header className="app-topbar">
          <div>
            <div className="eyebrow">研究笔记</div>
            <h1>{statusLabel(location.pathname)}</h1>
          </div>
          <div className="service-status" role="status">
            数据服务已连接
          </div>
        </header>
        <section className="app-canvas">
          <Outlet />
        </section>
      </main>
    </div>
  );
}
