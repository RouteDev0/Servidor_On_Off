import React from 'react';
import { useStatus } from '../hooks/useStatus';
import { StatusCard } from '../components/StatusCard';
import { ClienteGrid } from '../components/ClienteGrid';
import { RefreshCw } from 'lucide-react';

export const Dashboard: React.FC = () => {
    const { status, loading, error } = useStatus();

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
                <div>
                    <h1 style={{ fontSize: '1.875rem', marginBottom: '8px' }}>Visão Geral</h1>
                    <p style={{ color: 'var(--text-secondary)', margin: 0 }}>
                        {status?.total_clientes || 0} clientes encontrados
                    </p>
                </div>
                {loading && (
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        color: 'var(--accent-primary)',
                        fontSize: '0.875rem',
                        fontWeight: 500
                    }}>
                        <RefreshCw size={16} className="animate-pulse" style={{ animation: 'spin 1s linear infinite' }} />
                        Atualizando...
                    </div>
                )}
            </div>

            {error ? (
                <div style={{ padding: '24px', background: 'var(--bg-surface-glass)', color: 'var(--error)', borderRadius: '16px', border: '1px solid var(--error)' }}>
                    Erro ao carregar dados: {error.message}
                </div>
            ) : status ? (
                <>
                    <StatusCard
                        total={status.total_cameras}
                        online={status.cameras_online}
                        offline={status.cameras_offline}
                    />
                    <ClienteGrid clientes={status.clientes} />
                </>
            ) : (
                <div style={{ textAlign: 'center', padding: '48px', color: 'var(--text-secondary)' }}>
                    Nenhum dado disponível.
                </div>
            )}
        </div>
    );
};
