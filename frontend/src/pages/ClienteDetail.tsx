import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useStatus } from '../hooks/useStatus';
import { RefreshCw, ArrowLeft } from 'lucide-react';

export const ClienteDetail: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const { status, loading, error } = useStatus();

    // Find the specific client in the status data
    const cliente = status?.clientes.find(c => c.codigo_moni === decodeURIComponent(id || ''));

    if (loading && !cliente) {
        return (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--accent-primary)' }}>
                    <RefreshCw size={24} className="animate-pulse" style={{ animation: 'spin 1s linear infinite' }} />
                    Carregando detalhes...
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div style={{ padding: '24px', background: 'var(--bg-surface-glass)', color: 'var(--error)', borderRadius: '16px', border: '1px solid var(--error)' }}>
                Erro ao carregar dados: {error.message}
            </div>
        );
    }

    if (!cliente) {
        return (
            <div style={{ textAlign: 'center', padding: '48px', color: 'var(--text-secondary)' }}>
                <h2>Cliente não encontrado</h2>
                <Link to="/" style={{ color: 'var(--accent-primary)', textDecoration: 'underline' }}>Voltar ao Dashboard</Link>
            </div>
        );
    }

    const offlineCameras = cliente.cameras.filter(c => c.status === 'OFF' || c.status === 'SENHA_ERRADA');
    const onlineCameras = cliente.cameras.filter(c => c.status === 'ON');
    const totalCameras = cliente.cameras.length;
    const percent = totalCameras > 0
        ? ((onlineCameras.length / totalCameras) * 100).toFixed(1)
        : '0.0';

    return (
        <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto', width: '100%', boxSizing: 'border-box', overflowY: 'auto', height: '100%' }} className="animate-fade-in">
            {/* Header / Title Bar */}
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '24px' }}>
                <Link to="/" style={{
                    display: 'flex', alignItems: 'center', gap: '8px', color: '#888', textDecoration: 'none',
                    padding: '8px 16px', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px',
                    transition: 'all 0.2s', background: 'rgba(30,30,30,0.5)'
                }} className="hover-white">
                    <ArrowLeft size={16} /> Voltar
                </Link>
            </div>

            <div style={{ textAlign: 'center', marginBottom: '40px' }}>
                <h1 style={{ fontSize: '2rem', fontWeight: 800, color: '#facc15', margin: 0, letterSpacing: '0.5px' }}>
                    Status Ufv {cliente.cliente_nome}
                </h1>
            </div>

            {/* Progress Bar / Indicator */}
            {totalCameras > 0 && (
                <div style={{
                    margin: '0 auto 40px auto',
                    width: '60%',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '8px'
                }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: '#888', fontSize: '0.9rem' }}>
                        <span>Total: {totalCameras}</span>
                        <span>{percent.replace('.', ',')}% online</span>
                    </div>
                    <div style={{ width: '100%', height: '8px', background: '#333', borderRadius: '4px', overflow: 'hidden', display: 'flex', boxShadow: '0 0 15px rgba(0,0,0,0.5)' }}>
                        <div style={{ width: `${percent}%`, background: '#22c55e', height: '100%', boxShadow: 'inset 0 0 10px rgba(34,197,94,0.5)' }} />
                        <div style={{ width: `${100 - parseFloat(percent)}%`, background: '#ef4444', height: '100%', boxShadow: 'inset 0 0 10px rgba(239,68,68,0.5)' }} />
                    </div>
                </div>
            )}

            {/* Dual Column Layout */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)',
                gap: '32px',
                background: '#111',
                padding: '32px',
                borderRadius: '16px',
                border: '1px solid rgba(255,255,255,0.05)'
            }}>

                {/* Offline Column */}
                <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px', paddingBottom: '16px', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                        <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#ef4444', boxShadow: '0 0 10px #ef4444' }} />
                        <h2 style={{ fontSize: '1.25rem', color: '#ef4444', margin: 0, fontWeight: 600 }}>Câmeras Offline</h2>
                        <span style={{
                            background: '#ef4444', color: '#fff', padding: '2px 10px', borderRadius: '12px', fontSize: '0.85rem', fontWeight: 700
                        }}>
                            {offlineCameras.length}
                        </span>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        {offlineCameras.length === 0 ? (
                            <div style={{ color: '#666', fontStyle: 'italic', padding: '16px' }}>Nenhuma câmera offline.</div>
                        ) : (
                            offlineCameras.map((cam, idx) => (
                                <div key={idx} style={{
                                    background: 'rgba(239, 68, 68, 0.05)',
                                    border: '1px solid rgba(239, 68, 68, 0.2)',
                                    padding: '16px',
                                    borderRadius: '8px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '12px',
                                    color: '#e5e5e5'
                                }}>
                                    <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#ef4444' }} />
                                    {cam.nome}
                                    {cam.status === 'SENHA_ERRADA' && (
                                        <span style={{ marginLeft: 'auto', background: 'rgba(239, 68, 68, 0.2)', color: '#ef4444', padding: '4px 8px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 600 }}>
                                            Senha Incorreta
                                        </span>
                                    )}
                                </div>
                            ))
                        )}
                    </div>
                </div>

                {/* Online Column */}
                <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px', paddingBottom: '16px', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                        <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#22c55e', boxShadow: '0 0 10px #22c55e' }} />
                        <h2 style={{ fontSize: '1.25rem', color: '#22c55e', margin: 0, fontWeight: 600 }}>Câmeras Online</h2>
                        <span style={{
                            background: '#22c55e', color: '#fff', padding: '2px 10px', borderRadius: '12px', fontSize: '0.85rem', fontWeight: 700
                        }}>
                            {onlineCameras.length}
                        </span>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        {onlineCameras.length === 0 ? (
                            <div style={{ color: '#666', fontStyle: 'italic', padding: '16px' }}>Nenhuma câmera online.</div>
                        ) : (
                            onlineCameras.map((cam, idx) => (
                                <div key={idx} style={{
                                    background: 'transparent',
                                    border: '1px solid rgba(255, 255, 255, 0.05)',
                                    padding: '16px',
                                    borderRadius: '8px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '12px',
                                    color: '#a3a3a3'
                                }}>
                                    <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#22c55e' }} />
                                    {cam.nome}
                                </div>
                            ))
                        )}
                    </div>
                </div>

            </div>
        </div>
    );
};
