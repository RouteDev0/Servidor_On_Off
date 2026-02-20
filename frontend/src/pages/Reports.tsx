import React, { useState } from 'react';
import { useReports } from '../hooks/useReports';
import { SlaChart } from '../components/charts/SlaChart';
import { FailureTable } from '../components/charts/FailureTable';
import { useEmpresa } from '../contexts/EmpresaContext';
import { Calendar } from 'lucide-react';

export const Reports: React.FC = () => {
    const { selectedEmpresaId } = useEmpresa();
    const [days, setDays] = useState(7);
    const { slaReport, falhasReport, loading, error } = useReports(days);

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
                <div>
                    <h1 style={{ fontSize: '1.875rem', marginBottom: '8px' }}>Relatórios Analíticos</h1>
                    <p style={{ color: 'var(--text-secondary)', margin: 0 }}>
                        Análise de disponibilidade e falhas
                    </p>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <Calendar size={20} color="var(--text-secondary)" />
                    <select
                        className="glass-panel"
                        value={days}
                        onChange={(e) => setDays(Number(e.target.value))}
                        style={{
                            padding: '8px 16px',
                            color: 'var(--text-primary)',
                            border: '1px solid var(--border-color)',
                            outline: 'none',
                            fontSize: '0.875rem',
                            appearance: 'none',
                            cursor: 'pointer'
                        }}
                    >
                        <option value={1} style={{ background: 'var(--bg-surface)' }}>Últimas 24 horas</option>
                        <option value={7} style={{ background: 'var(--bg-surface)' }}>Últimos 7 dias</option>
                        <option value={30} style={{ background: 'var(--bg-surface)' }}>Últimos 30 dias</option>
                    </select>
                </div>
            </div>

            {!selectedEmpresaId ? (
                <div className="glass-panel" style={{ padding: '48px', textAlign: 'center', color: 'var(--text-secondary)' }}>
                    Por favor, selecione uma empresa no seletor superior para visualizar os relatórios.
                </div>
            ) : loading ? (
                <div className="glass-panel" style={{ padding: '48px', textAlign: 'center', color: 'var(--accent-primary)' }}>
                    Carregando relatórios...
                </div>
            ) : error ? (
                <div style={{ padding: '24px', background: 'var(--bg-surface-glass)', color: 'var(--error)', borderRadius: '16px', border: '1px solid var(--error)' }}>
                    Erro ao carregar relatórios: {error.message}
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr)', gap: '32px' }}>
                    <SlaChart data={slaReport} />
                    <FailureTable data={falhasReport} />
                </div>
            )}
        </div>
    );
};
