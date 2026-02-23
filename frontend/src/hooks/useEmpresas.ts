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
                // ensure we always store an array to avoid .map errors
                setEmpresas(Array.isArray(data) ? data : []);
            } catch (err: any) {
                console.error('Failed to fetch empresas', err);
                setError(err);
            } finally {
                setLoading(false);
            }
        };

        fetchEmpresas();
    }, []);

    return { empresas, loading, error };
};
