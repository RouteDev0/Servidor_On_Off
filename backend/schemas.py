"""
Pydantic schemas para serialização de respostas da API
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# ── Empresa ─────────────────────────────────────────────────────────
class EmpresaSchema(BaseModel):
    id: int
    nome: str
    logo_arquivo: Optional[str] = None
    cor_primaria: Optional[str] = None
    cor_secundaria: Optional[str] = None
    empresa_moni: Optional[int] = None
    total_clientes: Optional[int] = 0
    total_cameras: Optional[int] = 0

    model_config = {"from_attributes": True}


# ── Cliente ─────────────────────────────────────────────────────────
class ClienteSchema(BaseModel):
    codigo_moni: str
    nome: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    uf: Optional[str] = None
    empresa_id: Optional[int] = None
    empresa_nome: Optional[str] = None
    total_cameras: Optional[int] = 0

    model_config = {"from_attributes": True}


# ── Dispositivo ─────────────────────────────────────────────────────
class DispositivoSchema(BaseModel):
    id: str
    tipo_dispositivo: Optional[str] = None
    marca: Optional[str] = None
    ip: Optional[str] = None
    porta: Optional[int] = None
    codigo_moni: Optional[str] = None
    total_cameras: Optional[int] = 0

    model_config = {"from_attributes": True}


# ── Ponto de Monitoramento (câmera) ────────────────────────────────
class CameraSchema(BaseModel):
    uuid_camera: str
    dispositivo_id: Optional[str] = None
    numero_setor: Optional[int] = None
    canal_fisico: Optional[int] = None
    complemento: Optional[str] = None

    model_config = {"from_attributes": True}


# ── Status de câmera (tempo real) ───────────────────────────────────
class CameraStatusSchema(BaseModel):
    nome: str
    status: str  # "ON" | "OFF" | "NO_CONFIG"


class ClienteStatusSchema(BaseModel):
    cliente_nome: str
    codigo_moni: str
    empresa_id: Optional[int] = None
    empresa_nome: Optional[str] = None
    cameras: list[CameraStatusSchema] = []
    total_cameras: int = 0
    cameras_online: int = 0
    cameras_offline: int = 0


class StatusGeralSchema(BaseModel):
    total_clientes: int = 0
    total_cameras: int = 0
    cameras_online: int = 0
    cameras_offline: int = 0
    clientes: list[ClienteStatusSchema] = []


# ── Relatórios ──────────────────────────────────────────────────────
class SlaUnidadeSchema(BaseModel):
    cliente_nome: str
    codigo_moni: str
    total_cameras: int
    eventos_offline: int
    eventos_online: int
    uptime_percent: float


class FalhaRankingSchema(BaseModel):
    camera_nome: str
    uuid_camera: str
    cliente_nome: str
    dispositivo_ip: Optional[str] = None
    total_falhas: int


class ReportSlaSchema(BaseModel):
    empresa_id: int
    empresa_nome: str
    periodo_dias: int
    unidades: list[SlaUnidadeSchema] = []


class ReportFalhasSchema(BaseModel):
    empresa_id: int
    empresa_nome: str
    periodo_dias: int
    ranking: list[FalhaRankingSchema] = []
