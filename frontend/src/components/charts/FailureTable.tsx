import React from 'react';
import type { ReportFalhas } from '../../types';

interface Props {
    data: ReportFalhas | null;
}

export const FailureTable: React.FC<Props> = ({ data }) => {
    if (!data || !data.ranking || data.ranking.length === 0) {
        return (
            <div className="glass-panel" style={{ padding: '48px', textAlign: 'center', color: 'var(--text-secondary)' }}>
                Nenhuma falha registrada no período.
            </div>
        );
    }

    return (
        <div className="glass-panel" style={{ overflow: 'hidden' }}>
            <div style={{ padding: '24px', borderBottom: 'var(--glass-border)' }}>
                <h3 style={{ margin: 0, color: 'var(--text-primary)' }}>
                    Ranking de Falhas (Últimos {data.periodo_dias} dias)
                </h3>
            </div>
            <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                    <thead>
                        <tr style={{ background: 'rgba(255,255,255,0.05)' }}>
                            <th style={{ padding: '16px 24px', fontWeight: 600, color: 'var(--text-secondary)' }}>Cliente</th>
                            <th style={{ padding: '16px 24px', fontWeight: 600, color: 'var(--text-secondary)' }}>Câmera</th>
                            <th style={{ padding: '16px 24px', fontWeight: 600, color: 'var(--text-secondary)' }}>IP / Disp.</th>
                            <th style={{ padding: '16px 24px', fontWeight: 600, color: 'var(--text-secondary)' }}>Total Falhas</th>
                        </tr>
                    </thead>
                    <tbody>
                        {data.ranking.map((item, idx) => (
                            <tr key={idx} style={{ borderBottom: 'var(--glass-border)' }}>
                                <td style={{ padding: '16px 24px' }}>{item.cliente_nome}</td>
                                <td style={{ padding: '16px 24px' }}>
                                    <div style={{ display: 'flex', flexDirection: 'column' }}>
                                        <span style={{ fontWeight: 500 }}>{item.camera_nome}</span>
                                        <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{item.uuid_camera}</span>
                                    </div>
                                </td>
                                <td style={{ padding: '16px 24px', color: 'var(--text-secondary)' }}>
                                    {item.dispositivo_ip || '-'}
                                </td>
                                <td style={{ padding: '16px 24px' }}>
                                    <span style={{
                                        background: 'rgba(239, 68, 68, 0.2)',
                                        color: 'var(--error)',
                                        padding: '4px 12px',
                                        borderRadius: '999px',
                                        fontWeight: 600
                                    }}>
                                        {item.total_falhas}
                                    </span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};
