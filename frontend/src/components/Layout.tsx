import React from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import { Bell, Mail, Settings } from 'lucide-react';
import { EmpresaSelector } from './EmpresaSelector';

export const Layout: React.FC = () => {
    const location = useLocation();

    return (
        <div style={{ display: 'flex', flexDirection: 'column', width: '100%', height: '100vh', background: '#0a0a0a', overflow: 'hidden' }}>
            {/* Top Header */}
            <header style={{
                height: '64px',
                minHeight: '64px',
                borderBottom: '1px solid rgba(255,255,255,0.05)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '0 24px',
                background: '#111',
                zIndex: 10
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '32px' }}>
                    {/* Logo Approximation */}
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                        <div style={{ display: 'flex', flexDirection: 'column', lineHeight: 1 }}>
                            <div style={{ display: 'flex', alignItems: 'center', fontSize: '22px', fontWeight: 800, letterSpacing: '1px', color: '#fff' }}>
                                R
                                <svg width="22" height="22" viewBox="0 0 100 100" style={{ margin: '0 2px' }}>
                                    {/* Tail notch effect simulated with an inner overlapping element or carefully crafted path */}
                                    <path d="M 50 15 A 35 35 0 1 1 15 50 L 32 50 A 18 18 0 1 0 50 32 Z" fill="#facc15" />
                                    <polygon points="50,0 80,22.5 50,45" fill="#facc15" />
                                </svg>
                                UTE
                            </div>
                            <span style={{ fontSize: '9px', color: '#888', letterSpacing: '3px', textTransform: 'uppercase', marginTop: '2px' }}>
                                security
                            </span>
                        </div>
                        <div style={{ color: '#aaa', fontSize: '16px', marginLeft: '24px', borderLeft: '1px solid #333', paddingLeft: '24px' }}>
                            Security
                        </div>
                    </div>

                    {/* Top Navigation */}
                    <nav style={{ display: 'flex', gap: '24px', marginLeft: '16px' }}>
                        <NavLink to="/" style={{ 
                            color: location.pathname === '/' ? '#fff' : '#666', 
                            textDecoration: 'none', 
                            fontSize: '14px', 
                            fontWeight: 500,
                            padding: '22px 0',
                            borderBottom: location.pathname === '/' ? '2px solid #facc15' : '2px solid transparent',
                            transition: 'all 0.2s'
                        }}>Dashboard</NavLink>
                        
                        <NavLink to="/reports" style={{ 
                            color: location.pathname.includes('/reports') ? '#fff' : '#666', 
                            textDecoration: 'none', 
                            fontSize: '14px', 
                            fontWeight: 500,
                            padding: '22px 0',
                            borderBottom: location.pathname.includes('/reports') ? '2px solid #facc15' : '2px solid transparent',
                            transition: 'all 0.2s'
                        }}>Relatórios</NavLink>
                    </nav>
                </div>
                
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px', color: '#888' }}>
                    <EmpresaSelector />
                    <div style={{ height: '24px', width: '1px', background: '#333', margin: '0 8px' }} />
                    <Bell size={18} style={{ cursor: 'pointer', transition: 'color 0.2s' }} className="hover-white" />
                    <Mail size={18} style={{ cursor: 'pointer', transition: 'color 0.2s' }} className="hover-white" />
                    <Settings size={18} style={{ cursor: 'pointer', transition: 'color 0.2s' }} className="hover-white" />
                    <div style={{ 
                        background: '#facc15', color: '#000', width: '32px', height: '32px', 
                        borderRadius: '50%', display: 'flex', alignItems: 'center', 
                        justifyContent: 'center', fontWeight: 'bold', marginLeft: '8px', cursor: 'pointer'
                    }}>
                        A
                    </div>
                </div>
            </header>

            {/* Page Content */}
            <main style={{ flex: 1, display: 'flex', flexDirection: 'column', position: 'relative', overflow: 'hidden' }}>
                <Outlet />
            </main>
        </div>
    );
};
