'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';

const Sidebar = () => {
  const pathname = usePathname();
  const router = useRouter();

  // Hide sidebar on Auth pages
  if (pathname.includes('/login') || pathname.includes('/auth/callback')) {
    return null;
  }

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_email');
    router.push('/login');
  };

  const navItems = [
    { name: 'Dashboard',  href: '/',           icon: '📊' },
    { name: 'Campaigns',  href: '/campaigns',   icon: '✉️' },
    { name: 'Analytics',  href: '/campaign-dashboard', icon: '📈' },
    { name: 'Leads',      href: '/leads',       icon: '👥' },
    { name: 'Responses',  href: '/responses',   icon: '💬' },
    { name: 'Settings',   href: '/settings',    icon: '⚙️' },
  ];

  return (
    <aside className="sidebar">
      <div style={{ marginBottom: '2rem', padding: '0 1rem' }}>
        <h1 style={{ fontSize: '1.5rem', margin: 0, color: 'var(--primary)' }}>U-marketer</h1>
        <p style={{ fontSize: '0.75rem', marginTop: '0.25rem' }}>AI Marketing Agent</p>
      </div>
      
      <nav style={{ flex: 1 }}>
        <ul style={{ listStyle: 'none' }}>
          {navItems.map((item) => (
            <li key={item.href} style={{ marginBottom: '0.5rem' }}>
              <Link
                href={item.href}
                className={`btn btn-outline`}
                style={{
                  width: '100%',
                  justifyContent: 'flex-start',
                  border: pathname === item.href ? '1px solid var(--primary)' : '1px solid transparent',
                  background: pathname === item.href ? 'var(--accent)' : 'transparent',
                  color: pathname === item.href ? 'var(--primary)' : 'var(--foreground)',
                  padding: '0.75rem 1rem',
                  gap: '0.75rem'
                }}
              >
                <span>{item.icon}</span>
                {item.name}
              </Link>
            </li>
          ))}
        </ul>
      </nav>

      <div style={{ padding: '1rem', borderTop: '1px solid var(--border)', marginTop: 'auto' }}>
        <button 
          onClick={handleLogout}
          className="btn btn-outline" 
          style={{ width: '100%', fontSize: '0.875rem', borderColor: '#fee2e2', color: '#991b1b' }}
        >
          🚪 Logout
        </button>
        <p style={{ fontSize: '0.75rem', textAlign: 'center', marginTop: '1rem', color: 'var(--muted-foreground)' }}>v1.0.0</p>
      </div>
    </aside>
  );
};

export default Sidebar;
