import React from 'react';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Cell
} from 'recharts';
import type { ReportSla } from '../../types';

interface Props {
    data: ReportSla | null;
}

export const SlaChart: React.FC<Props> = ({ data }) => {
    if (!data || !data.unidades || data.unidades.length === 0) {
        return (
            <div className="glass-panel" style={{ padding: '48px', textAlign: 'center', color: 'var(--text-secondary)' }}>
                Dados de SLA não encontrados.
            </div>
        );
    }

    // Sort logically or just take the top/bottom
    const chartData = [...data.unidades].sort((a, b) => a.uptime_percent - b.uptime_percent);

    return (
        <div className="glass-panel" style={{ padding: '24px', width: '100%', boxSizing: 'border-box' }}>
            <h3 style={{ marginBottom: '24px', color: 'var(--text-primary)' }}>
                Uptime por Unidade (Últimos {data.periodo_dias} dias)
            </h3>
            <div style={{ width: '100%', height: '400px' }}>
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                        data={chartData}
                        layout="vertical"
                        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                    >
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" horizontal={false} />
                        <XAxis type="number" domain={[0, 100]} stroke="var(--text-secondary)" />
                        <YAxis
                            dataKey="cliente_nome"
                            type="category"
                            width={150}
                            stroke="var(--text-secondary)"
                            tick={{ fontSize: 12 }}
                        />
                        <Tooltip
                            contentStyle={{ background: 'var(--bg-surface)', border: 'var(--glass-border)', borderRadius: '8px' }}
                            formatter={(val: any) => [`${Number(val).toFixed(2)}%`, 'Uptime']}
                        />
                        <Bar dataKey="uptime_percent" radius={[0, 4, 4, 0]}>
                            {chartData.map((entry, index) => (
                                <Cell
                                    key={`cell-${index}`}
                                    fill={entry.uptime_percent >= 95 ? 'var(--success)' : entry.uptime_percent >= 90 ? 'var(--warning)' : 'var(--error)'}
                                />
                            ))}
                        </Bar>
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};
