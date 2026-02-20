import { useState, useEffect } from 'react';
import { api } from '../api/client';
import type { Empresa } from '../types';

export const useEmpresas = () => {
    const [empresas, setEmpresas] = useState<Empresa[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        const fetchEmpresas = async () => {
            try {
                setLoading(true);
                const data = await api.getEmpresas();
                setEmpresas(data);
            } catch (err: any) {
                setError(err);
            } finally {
                setLoading(false);
            }
        };

        fetchEmpresas();
    }, []);

    return { empresas, loading, error };
};
