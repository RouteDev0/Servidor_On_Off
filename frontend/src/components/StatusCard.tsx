import React from 'react';
import { Activity, ServerCrash, CheckCircle2 } from 'lucide-react';

interface Props {
    total: number;
    online: number;
    offline: number;
}

export const StatusCard: React.FC<Props> = ({ total, online, offline }) => {
    const onlinePerc = total > 0 ? ((online / total) * 100).toFixed(1) : '0.0';
    const offlinePerc = total > 0 ? ((offline / total) * 100).toFixed(1) : '0.0';

    return (
        <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '24px',
            marginBottom: '32px'
        }}>
            {/* Total Cameras Card */}
            <div className="glass-panel" style={{ padding: '24px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
                    <h3 style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Total Cameras</h3>
                    <Activity size={20} color="var(--accent-primary)" />
                </div>
                <p style={{ fontSize: '2rem', fontWeight: 700, margin: 0 }}>{total}</p>
            </div>

            {/* Online Cameras Card */}
            <div className="glass-panel" style={{ padding: '24px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
                    <h3 style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Online</h3>
                    <CheckCircle2 size={20} color="var(--success)" />
                </div>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
                    <p style={{ fontSize: '2rem', fontWeight: 700, margin: 0, color: 'var(--success)' }}>{online}</p>
                    <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>({onlinePerc}%)</span>
                </div>
            </div>

            {/* Offline Cameras Card */}
            <div className="glass-panel" style={{ padding: '24px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
                    <h3 style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Offline</h3>
                    <ServerCrash size={20} color="var(--error)" />
                </div>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
                    <p style={{ fontSize: '2rem', fontWeight: 700, margin: 0, color: 'var(--error)' }}>{offline}</p>
                    <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>({offlinePerc}%)</span>
                </div>
            </div>
        </div>
    );
};
