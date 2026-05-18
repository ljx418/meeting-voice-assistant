import { NavLink, Outlet, useLocation } from 'react-router-dom';
import { BookOpen, CircleHelp, GitBranch, Home, MessageSquareText } from 'lucide-react';

const navItems = [
  { to: '/', label: 'Home', icon: Home, end: true },
  { to: '/workbench', label: 'Workbench', icon: BookOpen },
  { to: '/graph', label: 'Graph', icon: GitBranch },
  { to: '/feedback', label: 'Feedback', icon: MessageSquareText }
];

function statusLabel(pathname: string) {
  if (pathname.includes('/workbench')) return 'Workbench';
  if (pathname.includes('/graph')) return 'Graph Context';
  if (pathname.startsWith('/workspaces/')) return 'Workspace';
  if (pathname.startsWith('/feedback')) return 'Lightweight';
  return 'Workspace Home';
}

export function AppShell() {
  const location = useLocation();

  return (
    <div className="app-shell">
      <aside className="app-sidebar" aria-label="Primary navigation">
        <div className="brand-block">
          <div className="brand-mark" aria-hidden="true">R</div>
          <div>
            <div className="brand-title">ResearchNotebook</div>
            <div className="brand-subtitle">Source-grounded workspace</div>
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
          <span>M4 adds read-only graph context and lightweight feedback. M5+ preview, ingestion, assessment, sync, and collaboration remain future work.</span>
        </div>
      </aside>
      <main className="app-main">
        <header className="app-topbar">
          <div>
            <div className="eyebrow">V1.0-M4</div>
            <h1>{statusLabel(location.pathname)}</h1>
          </div>
          <div className="service-status" role="status">
            API adapter ready
          </div>
        </header>
        <section className="app-canvas">
          <Outlet />
        </section>
      </main>
    </div>
  );
}
