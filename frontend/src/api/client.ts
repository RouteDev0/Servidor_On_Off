import axios from 'axios';
import type {
    Empresa,
    Cliente,
    StatusGeral,
    ReportSla,
    ReportFalhas
} from '../types';

const apiClient = axios.create({
    baseURL: 'http://localhost:51235/api', // Adjust in production
    headers: {
        'Content-Type': 'application/json',
    },
});

export const api = {
    getEmpresas: async (): Promise<Empresa[]> => {
        const { data } = await apiClient.get('/empresas');
        return data;
    },

    getClientes: async (empresa_id?: number): Promise<Cliente[]> => {
        const { data } = await apiClient.get('/clientes', {
            params: { empresa_id }
        });
        return data;
    },

    getStatus: async (empresa_id?: number): Promise<StatusGeral> => {
        const url = empresa_id ? `/status/${empresa_id}` : '/status';
        const { data } = await apiClient.get(url);
        return data;
    },

    getReportSla: async (empresa_id: number, days: number = 7): Promise<ReportSla> => {
        const { data } = await apiClient.get('/reports/sla', {
            params: { empresa_id, days }
        });
        return data;
    },

    getReportFalhas: async (empresa_id: number, days: number = 7): Promise<ReportFalhas> => {
        const { data } = await apiClient.get('/reports/failures', {
            params: { empresa_id, days }
        });
        return data;
    }
};
