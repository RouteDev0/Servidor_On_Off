// TypeScript interfaces based on the FastAPI Pydantic Schemas

export interface Empresa {
  id: number;
  nome: string;
  logo_arquivo?: string;
  cor_primaria?: string;
  cor_secundaria?: string;
  empresa_moni?: number;
  total_clientes?: number;
  total_cameras?: number;
}

export interface Cliente {
  codigo_moni: string;
  nome: string;
  latitude?: number;
  longitude?: number;
  uf?: string;
  empresa_id?: number;
  empresa_nome?: string;
  total_cameras?: number;
}

export interface CameraStatus {
  nome: string;
  status: 'ON' | 'OFF' | 'NO_CONFIG';
}

export interface ClienteStatus {
  cliente_nome: string;
  codigo_moni: string;
  empresa_id?: number;
  empresa_nome?: string;
  cameras: CameraStatus[];
  total_cameras: number;
  cameras_online: number;
  cameras_offline: number;
}

export interface StatusGeral {
  total_clientes: number;
  total_cameras: number;
  cameras_online: number;
  cameras_offline: number;
  clientes: ClienteStatus[];
}

export interface SlaUnidade {
  cliente_nome: string;
  codigo_moni: string;
  total_cameras: number;
  eventos_offline: number;
  eventos_online: number;
  uptime_percent: number;
}

export interface ReportSla {
  empresa_id: number;
  empresa_nome: string;
  periodo_dias: number;
  unidades: SlaUnidade[];
}

export interface FalhaRanking {
  camera_nome: string;
  uuid_camera: string;
  cliente_nome: string;
  dispositivo_ip?: string;
  total_falhas: number;
}

export interface ReportFalhas {
  empresa_id: number;
  empresa_nome: string;
  periodo_dias: number;
  ranking: FalhaRanking[];
}
