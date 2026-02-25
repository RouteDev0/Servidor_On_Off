import React, { useState } from 'react';
import { useStatus } from '../hooks/useStatus';
import { StatusCard } from '../components/StatusCard';
import { ClienteGrid } from '../components/ClienteGrid';
import { RefreshCw, Filter, ChevronRight } from 'lucide-react';

export const Dashboard: React.FC = () => {
    const { status, loading, error } = useStatus();
    const [isFilterOpen, setIsFilterOpen] = useState(true); // Default to open or closed based on preference

    // Filtros
    const [filterStatus, setFilterStatus] = useState('Todos');
    const [filterTipo, setFilterTipo] = useState('Todos');
    const [filterOrdem, setFilterOrdem] = useState('Mais offline primeiro');

    // Filtering logic
    let filteredClientes = status?.clientes || [];

    if (filterStatus === 'Apenas Offline') {
        filteredClientes = filteredClientes.filter(c => c.cameras_offline > 0);
    }

    if (filterOrdem === 'Mais offline primeiro') {
        filteredClientes = [...filteredClientes].sort((a, b) => b.cameras_offline - a.cameras_offline);
    } else if (filterOrdem === 'Alfabética') {
        filteredClientes = [...filteredClientes].sort((a, b) => a.cliente_nome.localeCompare(b.cliente_nome));
    }

    return (
        <div style={{ display: 'flex', height: '100%', overflow: 'hidden' }}>
            {/* Dashboard Main Content */}
            <div style={{ flex: 1, padding: '32px', overflowY: 'auto' }} className="animate-fade-in">
                {error ? (
                    <div style={{ padding: '24px', background: 'var(--bg-surface-glass)', color: 'var(--error)', borderRadius: '16px', border: '1px solid var(--error)' }}>
                        Erro ao carregar dados: {error.message}
                    </div>
                ) : status ? (
                    <>
                        {/* Top action row */}
                        <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '16px' }}>
                            {!isFilterOpen && (
                                <button
                                    onClick={() => setIsFilterOpen(true)}
                                    style={{
                                        background: 'transparent', border: '1px solid var(--border-color)', borderRadius: '8px',
                                        padding: '8px 16px', color: '#fff', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px',
                                        transition: 'background 0.2s'
                                    }}
                                    className="hover-bg-surface"
                                >
                                    <Filter size={18} /> Filtros
                                </button>
                            )}
                        </div>

                        <StatusCard
                            total={status.total_cameras}
                            online={status.cameras_online}
                            offline={status.cameras_offline}
                        />
                        <ClienteGrid clientes={filteredClientes} />
                    </>
                ) : (
                    <div style={{ textAlign: 'center', padding: '48px', color: 'var(--text-secondary)' }}>
                        Nenhum dado disponível.
                    </div>
                )}
            </div>

            {/* Right Filter Sidebar */}
            <div style={{
                width: isFilterOpen ? '320px' : '0px',
                minWidth: isFilterOpen ? '320px' : '0px',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                borderLeft: isFilterOpen ? '1px solid rgba(255,255,255,0.05)' : 'none',
                background: '#151515',
                overflow: 'hidden',
                display: 'flex',
                flexDirection: 'column',
                height: '100%'
            }}>
                <div style={{ padding: '32px 24px', width: '320px', boxSizing: 'border-box' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
                        <h2 style={{ fontSize: '1.25rem', color: '#facc15', margin: 0, fontWeight: 500 }}>Filtros</h2>
                        <button
                            onClick={() => setIsFilterOpen(false)}
                            style={{ background: 'transparent', border: 'none', color: '#888', cursor: 'pointer', padding: '4px' }}
                        >
                            <ChevronRight size={20} />
                        </button>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                        {/* Status Select */}
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                            <label style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Status</label>
                            <select
                                value={filterStatus}
                                onChange={(e) => setFilterStatus(e.target.value)}
                                style={{
                                    width: '100%', padding: '12px 16px', background: 'transparent', border: '1px solid rgba(255,255,255,0.1)',
                                    borderRadius: '4px', color: '#fff', outline: 'none', fontSize: '14px',
                                    appearance: 'none', cursor: 'pointer'
                                }}
                            >
                                <option style={{ background: '#151515' }}>Todos</option>
                                <option style={{ background: '#151515' }}>Apenas Offline</option>
                            </select>
                        </div>

                        {/* Tipo Select */}
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                            <label style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Tipo</label>
                            <select
                                value={filterTipo}
                                onChange={(e) => setFilterTipo(e.target.value)}
                                style={{
                                    width: '100%', padding: '12px 16px', background: 'transparent', border: '1px solid rgba(255,255,255,0.1)',
                                    borderRadius: '4px', color: '#fff', outline: 'none', fontSize: '14px',
                                    appearance: 'none', cursor: 'pointer'
                                }}
                            >
                                <option style={{ background: '#151515' }}>Todos</option>
                            </select>
                        </div>

                        {/* Ordem Select */}
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                            <label style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Ordem</label>
                            <select
                                value={filterOrdem}
                                onChange={(e) => setFilterOrdem(e.target.value)}
                                style={{
                                    width: '100%', padding: '12px 16px', background: 'transparent', border: '1px solid rgba(255,255,255,0.1)',
                                    borderRadius: '4px', color: '#fff', outline: 'none', fontSize: '14px',
                                    appearance: 'none', cursor: 'pointer'
                                }}
                            >
                                <option style={{ background: '#151515' }}>Mais offline primeiro</option>
                                <option style={{ background: '#151515' }}>Alfabética</option>
                            </select>
                        </div>
                    </div>

                    <div style={{ marginTop: '48px', display: 'flex', alignItems: 'center', gap: '8px', color: '#888', fontSize: '0.875rem' }}>
                        <RefreshCw size={14} className={loading ? 'animate-pulse' : ''} style={{ animation: loading ? 'spin 1s linear infinite' : 'none' }} />
                        Atualizado há 30s
                    </div>
                </div>
            </div>
        </div>
    );
};
