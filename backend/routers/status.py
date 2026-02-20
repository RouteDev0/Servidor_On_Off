"""Router: Status em tempo real"""

from fastapi import APIRouter, Query
from typing import Optional

from backend.schemas import StatusGeralSchema, ClienteStatusSchema, CameraStatusSchema

router = APIRouter(prefix="/api/status", tags=["Status"])

# Referência global ao verification_service (injetada pelo main.py)
_verification_service = None


def set_verification_service(vs):
    global _verification_service
    _verification_service = vs


@router.get("", response_model=StatusGeralSchema)
def status_geral(
    empresa_id: Optional[int] = Query(None, description="Filtrar por empresa"),
):
    """Retorna o status atual de todas as câmeras, opcionalmente filtrado por empresa."""
    if _verification_service is None:
        return StatusGeralSchema()

    status_raw = _verification_service.get_status_atual()

    clientes_list = []
    total_cameras = 0
    cameras_online = 0
    cameras_offline = 0

    for nome_cond, dados in status_raw.items():
        metadata = dados.get("metadata", {})
        cond_empresa_id = metadata.get("empresa_id")

        # Filtro por empresa
        if empresa_id is not None and cond_empresa_id != empresa_id:
            continue

        cameras_status = [
            CameraStatusSchema(nome=c["nome"], status=c["status"])
            for c in dados.get("cameras", [])
        ]

        n_online = sum(1 for c in cameras_status if c.status == "ON")
        n_offline = sum(1 for c in cameras_status if c.status == "OFF")

        clientes_list.append(
            ClienteStatusSchema(
                cliente_nome=nome_cond,
                codigo_moni=metadata.get("cliente", nome_cond),
                empresa_id=cond_empresa_id,
                empresa_nome=metadata.get("empresa_nome"),
                cameras=cameras_status,
                total_cameras=len(cameras_status),
                cameras_online=n_online,
                cameras_offline=n_offline,
            )
        )

        total_cameras += len(cameras_status)
        cameras_online += n_online
        cameras_offline += n_offline

    return StatusGeralSchema(
        total_clientes=len(clientes_list),
        total_cameras=total_cameras,
        cameras_online=cameras_online,
        cameras_offline=cameras_offline,
        clientes=clientes_list,
    )
