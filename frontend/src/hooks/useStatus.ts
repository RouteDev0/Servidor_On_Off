import { useState, useEffect } from 'react';
import { api } from '../api/client';
import type { StatusGeral } from '../types';
import { useEmpresa } from '../contexts/EmpresaContext';

export const useStatus = () => {
    const { selectedEmpresaId } = useEmpresa();
    const [status, setStatus] = useState<StatusGeral | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        let isMounted = true;

        const fetchStatus = async () => {
            try {
                setLoading(true);
                const data = await api.getStatus(selectedEmpresaId || undefined);
                if (isMounted) setStatus(data);
            } catch (err: any) {
                if (isMounted) setError(err);
            } finally {
                if (isMounted) setLoading(false);
            }
        };

        fetchStatus();

        // Auto-refresh every 30 seconds
        const interval = setInterval(fetchStatus, 30000);
        return () => {
            isMounted = false;
            clearInterval(interval);
        };
    }, [selectedEmpresaId]);

    return { status, loading, error };
};
