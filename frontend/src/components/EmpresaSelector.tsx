import React from 'react';
import { useEmpresas } from '../hooks/useEmpresas';
import { useEmpresa } from '../contexts/EmpresaContext';
import { Building2 } from 'lucide-react';

export const EmpresaSelector: React.FC = () => {
    const { empresas, loading } = useEmpresas();
    const { selectedEmpresaId, setSelectedEmpresaId } = useEmpresa();

    if (loading) return <div style={{ opacity: 0.5 }}>Carregando empresas...</div>;

    return (
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <Building2 size={20} color="var(--text-secondary)" />
            <select
                className="glass-panel"
                style={{
                    padding: '8px 16px',
                    color: 'var(--text-primary)',
                    border: '1px solid var(--border-color)',
                    outline: 'none',
                    fontSize: '0.875rem',
                    appearance: 'none',
                    cursor: 'pointer',
                    minWidth: '200px',
                }}
                value={selectedEmpresaId || ''}
                onChange={(e) => {
                    const val = e.target.value;
                    setSelectedEmpresaId(val ? Number(val) : null);
                }}
            >
                <option value="">Todas as Empresas</option>
                {empresas.map((emp) => (
                    <option key={emp.id} value={emp.id} style={{ background: 'var(--bg-surface)' }}>
                        {emp.nome}
                    </option>
                ))}
            </select>
        </div>
    );
};
