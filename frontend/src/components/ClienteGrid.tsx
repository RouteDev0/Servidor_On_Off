import React from 'react';
import type { ClienteStatus } from '../types';
import { Camera } from 'lucide-react';
import { Link } from 'react-router-dom';

interface Props {
    clientes: ClienteStatus[];
}

export const ClienteGrid: React.FC<Props> = ({ clientes }) => {
    if (!clientes || clientes.length === 0) {
        return (
            <div style={{ textAlign: 'center', padding: '48px', color: 'var(--text-secondary)' }}>
                Nenhum cliente encontrado.
            </div>
        );
    }

    return (
        <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
            gap: '16px'
        }}>
            {clientes.map((cliente) => {
                const totalCameras = cliente.cameras.length;
                const percent = totalCameras > 0
                    ? ((cliente.cameras_online / totalCameras) * 100).toFixed(1)
                    : '0.0';

                // Determine colors based on offline status
                let strokeColor = 'rgba(255,255,255,0.05)';
                let glowColor = 'transparent';
                let iconColor = '#888';
                let valueColor = '#888';

                if (cliente.cameras_offline > 0) {
                    const offlineRatio = cliente.cameras_offline / totalCameras;
                    if (offlineRatio > 0.1 || cliente.cameras_offline > 10) {
                        strokeColor = '#ef4444'; // Red
                        glowColor = 'rgba(239, 68, 68, 0.15)';
                        iconColor = '#ef4444';
                        valueColor = '#ef4444';
                    } else {
                        strokeColor = '#f59e0b'; // Yellow/Orange
                        glowColor = 'rgba(245, 158, 11, 0.15)';
                        iconColor = '#f59e0b';
                        valueColor = '#f59e0b';
                    }
                }

                return (
                    <div key={cliente.codigo_moni} style={{
                        padding: '24px',
                        display: 'flex',
                        flexDirection: 'column',
                        position: 'relative',
                        background: 'linear-gradient(180deg, rgba(30,30,30,0.4) 0%, rgba(20,20,20,0.6) 100%)',
                        border: `1px solid ${strokeColor}`,
                        boxShadow: cliente.cameras_offline > 0 ? `inset 0 0 20px -10px ${glowColor}, 0 0 15px -5px ${glowColor}` : 'none',
                        borderRadius: '8px',
                        transition: 'all 0.2s',
                        cursor: 'pointer'
                    }} className="hover-brightness">
                        <div style={{ display: 'flex', gap: '16px' }}>
                            <div style={{ color: iconColor, filter: cliente.cameras_offline > 0 ? `drop-shadow(0 0 8px ${iconColor})` : 'none' }}>
                                <Camera size={32} />
                            </div>

                            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 500, color: '#e5e5e5' }}>
                                    {cliente.cliente_nome}
                                </h3>

                                <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px' }}>
                                    <span style={{ fontSize: '1.5rem', fontWeight: 700, color: valueColor, lineHeight: 1 }}>
                                        {cliente.cameras_offline}
                                    </span>
                                    <span style={{ fontSize: '0.9rem', color: valueColor }}>
                                        offline
                                    </span>
                                </div>

                                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '16px' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                        <span style={{ fontSize: '0.8rem', color: '#888', display: 'flex', alignItems: 'center', gap: '6px' }}>
                                            <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#666' }} />
                                            Total: {totalCameras}
                                        </span>
                                        <span style={{ fontSize: '0.8rem', color: '#888' }}>
                                            {totalCameras > 0 ? `${percent.replace('.', ',')}% online` : '--'}
                                        </span>
                                    </div>
                                    {totalCameras > 0 && (
                                        <div style={{ width: '100%', height: '4px', background: '#333', borderRadius: '2px', overflow: 'hidden', display: 'flex' }}>
                                            <div style={{ width: `${percent}%`, background: '#22c55e', height: '100%' }} />
                                            <div style={{ width: `${100 - parseFloat(percent)}%`, background: '#ef4444', height: '100%' }} />
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>

                        <div style={{ marginTop: '24px', paddingTop: '16px', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
                            <Link to={`/cliente/${encodeURIComponent(cliente.codigo_moni)}`} style={{ color: '#888', fontSize: '0.8rem', textDecoration: 'none', display: 'flex', alignItems: 'center', transition: 'color 0.2s' }} className="hover-white">
                                Ver detalhes &rarr;
                            </Link>
                        </div>
                    </div>
                );
            })}
        </div>
    );
};
