import React from 'react';

interface Props {
    status: 'ON' | 'OFF' | 'NO_CONFIG';
}

export const CameraStatusBadge: React.FC<Props> = ({ status }) => {
    let color = '#a0a0a0';
    let label = 'Configuração Pendente';
    let animationClass = '';
    let bgClass = 'rgba(160, 160, 160, 0.2)';

    if (status === 'ON') {
        color = '#10b981';
        label = 'Online';
        bgClass = 'rgba(16, 185, 129, 0.2)';
    } else if (status === 'OFF') {
        color = '#ef4444';
        label = 'Offline';
        animationClass = 'animate-pulse';
        bgClass = 'rgba(239, 68, 68, 0.2)';
    }

    return (
        <span style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            padding: '4px 8px',
            borderRadius: '999px',
            fontSize: '0.75rem',
            fontWeight: 500,
            color,
            background: bgClass,
            border: `1px solid ${color}40`
        }}>
            <span
                className={animationClass}
                style={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    backgroundColor: color,
                    display: 'inline-block'
                }}
            />
            {label}
        </span>
    );
};
