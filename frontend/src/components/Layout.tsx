import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { Camera, LayoutDashboard, BarChart3 } from 'lucide-react';
import { EmpresaSelector } from './EmpresaSelector';

export const Layout: React.FC = () => {
    return (
        <div style={{ display: 'flex', width: '100%', minHeight: '100vh' }}>
            {/* Sidebar */}
            <aside className="glass-panel" style={{
                width: 'var(--sidebar-width)',
                borderRadius: 0,
                borderRight: 'var(--glass-border)',
                display: 'flex',
                flexDirection: 'column',
                padding: '24px 0'
            }}>
                <div style={{ padding: '0 24px', marginBottom: '48px', display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{ background: 'var(--accent-primary)', padding: '8px', borderRadius: '12px' }}>
                        <Camera size={24} color="#fff" />
                    </div>
                    <h2 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 700, letterSpacing: '-0.05em' }}>
                        MoniCam
                    </h2>
                </div>

                <nav style={{ display: 'flex', flexDirection: 'column', gap: '8px', padding: '0 16px' }}>
                    <NavLink
                        to="/"
                        style={({ isActive }) => ({
                            display: 'flex',
                            alignItems: 'center',
                            gap: '12px',
                            padding: '12px 16px',
                            borderRadius: '12px',
                            color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
                            background: isActive ? 'rgba(255,255,255,0.1)' : 'transparent',
                            fontWeight: isActive ? 600 : 500,
                            transition: 'all 0.2s'
                        })}
                    >
                        <LayoutDashboard size={20} />
                        Dashboard
                    </NavLink>
                    <NavLink
                        to="/reports"
                        style={({ isActive }) => ({
                            display: 'flex',
                            alignItems: 'center',
                            gap: '12px',
                            padding: '12px 16px',
                            borderRadius: '12px',
                            color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
                            background: isActive ? 'rgba(255,255,255,0.1)' : 'transparent',
                            fontWeight: isActive ? 600 : 500,
                            transition: 'all 0.2s'
                        })}
                    >
                        <BarChart3 size={20} />
                        Relatórios
                    </NavLink>
                </nav>
            </aside>

            {/* Main Content */}
            <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                {/* Header */}
                <header className="glass-panel" style={{
                    height: 'var(--header-height)',
                    borderRadius: 0,
                    borderBottom: 'var(--glass-border)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'flex-end',
                    padding: '0 32px'
                }}>
                    <EmpresaSelector />
                </header>

                {/* Page Content */}
                <div className="animate-fade-in" style={{ padding: '32px', flex: 1, overflowY: 'auto' }}>
                    <Outlet />
                </div>
            </main>
        </div>
    );
};
