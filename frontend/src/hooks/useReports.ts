import { useState, useEffect } from 'react';
import { api } from '../api/client';
import type { ReportSla, ReportFalhas } from '../types';
import { useEmpresa } from '../contexts/EmpresaContext';

export const useReports = (days: number = 7) => {
    const { selectedEmpresaId } = useEmpresa();

    const [slaReport, setSlaReport] = useState<ReportSla | null>(null);
    const [falhasReport, setFalhasReport] = useState<ReportFalhas | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        if (!selectedEmpresaId) {
            setSlaReport(null);
            setFalhasReport(null);
            return;
        }

        const fetchReports = async () => {
            try {
                setLoading(true);
                const [sla, falhas] = await Promise.all([
                    api.getReportSla(selectedEmpresaId, days),
                    api.getReportFalhas(selectedEmpresaId, days)
                ]);
                setSlaReport(sla);
                setFalhasReport(falhas);
            } catch (err: any) {
                setError(err);
            } finally {
                setLoading(false);
            }
        };

        fetchReports();
    }, [selectedEmpresaId, days]);

    return { slaReport, falhasReport, loading, error };
};
