"""Router: Empresas"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.models import Empresa, Cliente, Dispositivo, PontoMonitoramento
from backend.schemas import EmpresaSchema

router = APIRouter(prefix="/api/empresas", tags=["Empresas"])


@router.get("", response_model=list[EmpresaSchema])
def listar_empresas(db: Session = Depends(get_db)):
    """Retorna todas as empresas com contagem de clientes e câmeras."""
    empresas = db.query(Empresa).all()
    result = []
    for emp in empresas:
        total_clientes = (
            db.query(func.count(Cliente.codigo_moni))
            .filter(Cliente.empresa_id == emp.id)
            .scalar()
        ) or 0
        total_cameras = (
            db.query(func.count(PontoMonitoramento.uuid_camera))
            .join(Dispositivo, Dispositivo.id == PontoMonitoramento.dispositivo_id)
            .join(Cliente, Cliente.codigo_moni == Dispositivo.codigo_moni)
            .filter(Cliente.empresa_id == emp.id)
            .scalar()
        ) or 0
        result.append(
            EmpresaSchema(
                id=emp.id,
                nome=emp.nome,
                logo_arquivo=emp.logo_arquivo,
                cor_primaria=emp.cor_primaria,
                cor_secundaria=emp.cor_secundaria,
                empresa_moni=emp.empresa_moni,
                total_clientes=total_clientes,
                total_cameras=total_cameras,
            )
        )
    return result


@router.get("/{empresa_id}", response_model=EmpresaSchema)
def obter_empresa(empresa_id: int, db: Session = Depends(get_db)):
    """Retorna detalhes de uma empresa específica."""
    emp = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not emp:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    total_clientes = (
        db.query(func.count(Cliente.codigo_moni))
        .filter(Cliente.empresa_id == emp.id)
        .scalar()
    ) or 0
    total_cameras = (
        db.query(func.count(PontoMonitoramento.uuid_camera))
        .join(Dispositivo, Dispositivo.id == PontoMonitoramento.dispositivo_id)
        .join(Cliente, Cliente.codigo_moni == Dispositivo.codigo_moni)
        .filter(Cliente.empresa_id == emp.id)
        .scalar()
    ) or 0
    return EmpresaSchema(
        id=emp.id,
        nome=emp.nome,
        logo_arquivo=emp.logo_arquivo,
        cor_primaria=emp.cor_primaria,
        cor_secundaria=emp.cor_secundaria,
        empresa_moni=emp.empresa_moni,
        total_clientes=total_clientes,
        total_cameras=total_cameras,
    )
