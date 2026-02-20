import React from 'react';
import { ClienteStatus } from '../../types';
import { CameraStatusBadge } from '../CameraStatusBadge';
import { BuildingIcon } from 'lucide-react';

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
            gap: '24px'
        }}>
            {clientes.map((cliente) => (
                <div key={cliente.codigo_moni} className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <div style={{
                            padding: '10px',
                            background: 'rgba(99, 102, 241, 0.1)',
                            borderRadius: '12px',
                            color: 'var(--accent-primary)'
                        }}>
                            <BuildingIcon size={24} />
                        </div>
                        <div>
                            <h3 style={{ margin: 0, fontSize: '1rem', color: 'var(--text-primary)' }}>
                                {cliente.cliente_nome}
                            </h3>
                            <p style={{ margin: '4px 0 0 0', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                                {cliente.empresa_nome} • {cliente.codigo_moni}
                            </p>
                        </div>
                    </div>

                    <div style={{ padding: '12px 0', borderTop: 'var(--glass-border)', borderBottom: 'var(--glass-border)' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                            <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Status Geral</span>
                            <span style={{ fontSize: '0.875rem', fontWeight: 600 }}>
                                <span style={{ color: 'var(--success)' }}>{cliente.cameras_online}</span>
                                <span style={{ color: 'var(--text-secondary)', margin: '0 4px' }}>/</span>
                                <span style={{ color: 'var(--error)' }}>{cliente.cameras_offline}</span>
                            </span>
                        </div>
                    </div>

                    {cliente.cameras.length > 0 ? (
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                            {cliente.cameras.map((cam, idx) => (
                                <div key={idx} style={{
                                    display: 'flex',
                                    flexDirection: 'column',
                                    gap: '6px',
                                    background: 'rgba(0,0,0,0.2)',
                                    padding: '8px 12px',
                                    borderRadius: '8px',
                                    width: '100%',
                                    boxSizing: 'border-box'
                                }}>
                                    <span style={{ fontSize: '0.75rem', color: 'var(--text-primary)' }}>
                                        {cam.nome}
                                    </span>
                                    <CameraStatusBadge status={cam.status} />
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', fontStyle: 'italic' }}>
                            Nenhuma câmera configurada.
                        </p>
                    )}
                </div>
            ))}
        </div>
    );
};
