"""Router: Relatórios gerenciais"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas import ReportSlaSchema, ReportFalhasSchema
from backend.reports.report_generator import gerar_sla_por_unidade, gerar_ranking_falhas

router = APIRouter(prefix="/api/reports", tags=["Relatórios"])


@router.get("/sla", response_model=ReportSlaSchema)
def report_sla(
    empresa_id: int = Query(..., description="ID da empresa"),
    dias: int = Query(7, description="Período em dias"),
    db: Session = Depends(get_db),
):
    """SLA / Uptime por unidade (cliente) de uma empresa."""
    return gerar_sla_por_unidade(db, empresa_id, dias)


@router.get("/failures", response_model=ReportFalhasSchema)
def report_falhas(
    empresa_id: int = Query(..., description="ID da empresa"),
    dias: int = Query(7, description="Período em dias"),
    db: Session = Depends(get_db),
):
    """Ranking de câmeras/DVRs com mais falhas (offline) no período."""
    return gerar_ranking_falhas(db, empresa_id, dias)
