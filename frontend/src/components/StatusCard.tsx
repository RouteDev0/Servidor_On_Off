import React from 'react';
import { Camera } from 'lucide-react';

interface Props {
    total: number;
    online: number;
    offline: number;
}

export const StatusCard: React.FC<Props> = ({ total, online, offline }) => {
    // Calcular a porcentagem de online vs total. 
    // A imagem mostra 84,7% para 934 de 1102.
    const onlinePerc = total > 0 ? ((online / total) * 100).toFixed(1) : '0.0';

    return (
        <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '16px',
            marginBottom: '32px'
        }}>
            {/* Total Cameras Card */}
            <div className="glass-panel" style={{
                padding: '24px 24px 16px 24px',
                display: 'flex',
                flexDirection: 'column',
                position: 'relative',
                background: 'linear-gradient(180deg, rgba(30,30,30,0.5) 0%, rgba(20,20,20,0.8) 100%)',
                border: '1px solid rgba(255,255,255,0.05)',
                boxShadow: '0 4px 20px rgba(0,0,0,0.5)'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '8px' }}>
                    <Camera size={24} color="#888" />
                    <h3 style={{ color: '#bbb', fontSize: '0.9rem', fontWeight: 500 }}>Total de Câmeras</h3>
                </div>
                <p style={{ fontSize: '2.5rem', fontWeight: 600, margin: 0, paddingLeft: '40px' }}>{total}</p>

                {/* Glowing bottom line */}
                <div style={{ position: 'absolute', bottom: 0, left: '20%', right: '20%', height: '2px', background: 'linear-gradient(90deg, transparent, rgba(255,150,50,0.8), transparent)', boxShadow: '0 -2px 10px rgba(255,150,50,0.5)' }} />
            </div>

            {/* Online Card */}
            <div className="glass-panel" style={{
                padding: '24px 24px 16px 24px',
                display: 'flex',
                flexDirection: 'column',
                position: 'relative',
                background: 'linear-gradient(180deg, rgba(30,30,30,0.5) 0%, rgba(20,20,20,0.8) 100%)',
                border: '1px solid rgba(255,255,255,0.05)',
                boxShadow: '0 4px 20px rgba(0,0,0,0.5)'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '8px' }}>
                    <div style={{
                        width: '24px', height: '24px', borderRadius: '50%',
                        background: 'radial-gradient(circle, rgba(34,197,94,0.3) 0%, transparent 60%)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center'
                    }}>
                        <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#22c55e', boxShadow: '0 0 10px #22c55e' }} />
                    </div>
                    <h3 style={{ color: '#bbb', fontSize: '0.9rem', fontWeight: 500 }}>Online</h3>
                </div>
                <p style={{ fontSize: '2.5rem', fontWeight: 600, margin: 0, paddingLeft: '40px' }}>{online}</p>

                {/* Glowing bottom line */}
                <div style={{ position: 'absolute', bottom: 0, left: '30%', right: '30%', height: '2px', background: 'linear-gradient(90deg, transparent, rgba(34,197,94,0.8), transparent)', boxShadow: '0 -2px 10px rgba(34,197,94,0.5)' }} />
            </div>

            {/* Offline Card */}
            <div className="glass-panel" style={{
                padding: '24px 24px 16px 24px',
                display: 'flex',
                justifyContent: 'space-between',
                position: 'relative',
                background: 'linear-gradient(180deg, rgba(30,30,30,0.5) 0%, rgba(20,20,20,0.8) 100%)',
                border: '1px solid rgba(255,255,255,0.05)',
                boxShadow: '0 4px 20px rgba(0,0,0,0.5)'
            }}>
                <div style={{ display: 'flex', flexDirection: 'column' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '8px' }}>
                        <div style={{
                            width: '24px', height: '24px', borderRadius: '50%',
                            background: 'radial-gradient(circle, rgba(239,68,68,0.3) 0%, transparent 60%)',
                            display: 'flex', alignItems: 'center', justifyContent: 'center'
                        }}>
                            <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#ef4444', boxShadow: '0 0 10px #ef4444' }} />
                        </div>
                        <h3 style={{ color: '#bbb', fontSize: '0.9rem', fontWeight: 500 }}>Offline</h3>
                    </div>
                    <p style={{ fontSize: '2.5rem', fontWeight: 600, margin: 0, paddingLeft: '40px' }}>{offline}</p>
                </div>
                <div style={{ display: 'flex', alignItems: 'center' }}>
                    <span style={{ fontSize: '2rem', fontWeight: 600, color: '#4ade80' }}>
                        {onlinePerc.replace('.', ',')}%
                    </span>
                </div>

                {/* Glowing bottom line */}
                <div style={{ position: 'absolute', bottom: 0, left: '20%', right: '20%', height: '2px', background: 'linear-gradient(90deg, transparent, rgba(255,150,50,0.8), transparent)', boxShadow: '0 -2px 10px rgba(255,150,50,0.5)' }} />
            </div>
        </div>
    );
};
