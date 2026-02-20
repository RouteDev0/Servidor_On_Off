"""Router: Clientes"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from backend.database import get_db
from backend.models import Cliente, Dispositivo, PontoMonitoramento, Empresa
from backend.schemas import ClienteSchema

router = APIRouter(prefix="/api/clientes", tags=["Clientes"])


@router.get("", response_model=list[ClienteSchema])
def listar_clientes(
    empresa_id: Optional[int] = Query(None, description="Filtrar por empresa"),
    db: Session = Depends(get_db),
):
    """Retorna clientes, opcionalmente filtrados por empresa."""
    query = db.query(Cliente)
    if empresa_id:
        query = query.filter(Cliente.empresa_id == empresa_id)

    clientes = query.all()
    result = []
    for cli in clientes:
        total_cameras = (
            db.query(func.count(PontoMonitoramento.uuid_camera))
            .join(Dispositivo, Dispositivo.id == PontoMonitoramento.dispositivo_id)
            .filter(Dispositivo.codigo_moni == cli.codigo_moni)
            .scalar()
        ) or 0

        empresa_nome = None
        if cli.empresa:
            empresa_nome = cli.empresa.nome

        result.append(
            ClienteSchema(
                codigo_moni=cli.codigo_moni,
                nome=cli.nome,
                latitude=float(cli.latitude) if cli.latitude else None,
                longitude=float(cli.longitude) if cli.longitude else None,
                uf=cli.uf,
                empresa_id=cli.empresa_id,
                empresa_nome=empresa_nome,
                total_cameras=total_cameras,
            )
        )
    return result
