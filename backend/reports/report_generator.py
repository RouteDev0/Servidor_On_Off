"""
Gerador de relatórios gerenciais com Pandas.

1. SLA / Uptime por Unidade – disponibilidade comparativa entre clientes de uma empresa
2. Ranking de Falhas – câmeras/DVRs com mais eventos 960 (offline) na semana
"""

from datetime import datetime, timedelta
from typing import Optional
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.models import (
    Empresa,
    Cliente,
    Dispositivo,
    PontoMonitoramento,
    HistoricoEvento,
)


def gerar_sla_por_unidade(
    db: Session, empresa_id: int, dias: int = 7
) -> dict:
    """
    Calcula o SLA / Uptime por unidade (cliente) de uma empresa.

    Lógica:
    - Conta eventos 960 (offline) e 961 (online) por cliente no período.
    - Calcula um score simples: uptime_percent = online / (online + offline) * 100
    """
    data_inicio = datetime.now() - timedelta(days=dias)

    # Busca empresa
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        return {"empresa_id": empresa_id, "empresa_nome": "N/A", "periodo_dias": dias, "unidades": []}

    # Query: eventos agrupados por cliente
    rows = (
        db.query(
            Cliente.codigo_moni,
            Cliente.nome.label("cliente_nome"),
            HistoricoEvento.tipo_evento,
            func.count(HistoricoEvento.id).label("total"),
        )
        .join(Dispositivo, Dispositivo.codigo_moni == Cliente.codigo_moni)
        .join(PontoMonitoramento, PontoMonitoramento.dispositivo_id == Dispositivo.id)
        .join(HistoricoEvento, HistoricoEvento.ponto_id == PontoMonitoramento.uuid_camera)
        .filter(Cliente.empresa_id == empresa_id)
        .filter(HistoricoEvento.data_hora >= data_inicio)
        .filter(HistoricoEvento.tipo_evento.in_(["960", "961"]))
        .group_by(Cliente.codigo_moni, Cliente.nome, HistoricoEvento.tipo_evento)
        .all()
    )

    # Converter para DataFrame
    if not rows:
        # Retorna clientes sem eventos
        clientes = db.query(Cliente).filter(Cliente.empresa_id == empresa_id).all()
        unidades = []
        for c in clientes:
            total_cameras = (
                db.query(func.count(PontoMonitoramento.uuid_camera))
                .join(Dispositivo, Dispositivo.id == PontoMonitoramento.dispositivo_id)
                .filter(Dispositivo.codigo_moni == c.codigo_moni)
                .scalar()
            ) or 0
            unidades.append({
                "cliente_nome": c.nome,
                "codigo_moni": c.codigo_moni,
                "total_cameras": total_cameras,
                "eventos_offline": 0,
                "eventos_online": 0,
                "uptime_percent": 100.0,
            })
        return {
            "empresa_id": empresa_id,
            "empresa_nome": empresa.nome,
            "periodo_dias": dias,
            "unidades": unidades,
        }

    df = pd.DataFrame(
        [{"codigo_moni": r.codigo_moni, "cliente_nome": r.cliente_nome,
          "tipo_evento": r.tipo_evento, "total": r.total} for r in rows]
    )

    # Pivot para ter colunas 960 e 961
    pivot = df.pivot_table(
        index=["codigo_moni", "cliente_nome"],
        columns="tipo_evento",
        values="total",
        fill_value=0,
        aggfunc="sum",
    ).reset_index()

    # Garantir colunas
    if "960" not in pivot.columns:
        pivot["960"] = 0
    if "961" not in pivot.columns:
        pivot["961"] = 0

    pivot["total_eventos"] = pivot["960"] + pivot["961"]
    pivot["uptime_percent"] = pivot.apply(
        lambda r: round((r["961"] / r["total_eventos"]) * 100, 2) if r["total_eventos"] > 0 else 100.0,
        axis=1,
    )

    unidades = []
    for _, row in pivot.iterrows():
        total_cameras = (
            db.query(func.count(PontoMonitoramento.uuid_camera))
            .join(Dispositivo, Dispositivo.id == PontoMonitoramento.dispositivo_id)
            .filter(Dispositivo.codigo_moni == row["codigo_moni"])
            .scalar()
        ) or 0
        unidades.append({
            "cliente_nome": row["cliente_nome"],
            "codigo_moni": row["codigo_moni"],
            "total_cameras": total_cameras,
            "eventos_offline": int(row["960"]),
            "eventos_online": int(row["961"]),
            "uptime_percent": float(row["uptime_percent"]),
        })

    # Ordena por uptime crescente (piores primeiro)
    unidades.sort(key=lambda x: x["uptime_percent"])

    return {
        "empresa_id": empresa_id,
        "empresa_nome": empresa.nome,
        "periodo_dias": dias,
        "unidades": unidades,
    }


def gerar_ranking_falhas(
    db: Session, empresa_id: int, dias: int = 7
) -> dict:
    """
    Ranking de câmeras/DVRs com mais falhas (evento 960) no período.
    """
    data_inicio = datetime.now() - timedelta(days=dias)

    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        return {"empresa_id": empresa_id, "empresa_nome": "N/A", "periodo_dias": dias, "ranking": []}

    rows = (
        db.query(
            PontoMonitoramento.uuid_camera,
            PontoMonitoramento.complemento,
            Cliente.nome.label("cliente_nome"),
            Dispositivo.ip.label("dispositivo_ip"),
            func.count(HistoricoEvento.id).label("total_falhas"),
        )
        .join(HistoricoEvento, HistoricoEvento.ponto_id == PontoMonitoramento.uuid_camera)
        .join(Dispositivo, Dispositivo.id == PontoMonitoramento.dispositivo_id)
        .join(Cliente, Cliente.codigo_moni == Dispositivo.codigo_moni)
        .filter(Cliente.empresa_id == empresa_id)
        .filter(HistoricoEvento.tipo_evento == "960")
        .filter(HistoricoEvento.data_hora >= data_inicio)
        .group_by(
            PontoMonitoramento.uuid_camera,
            PontoMonitoramento.complemento,
            Cliente.nome,
            Dispositivo.ip,
        )
        .order_by(func.count(HistoricoEvento.id).desc())
        .limit(50)
        .all()
    )

    ranking = [
        {
            "camera_nome": r.complemento or r.uuid_camera,
            "uuid_camera": r.uuid_camera,
            "cliente_nome": r.cliente_nome,
            "dispositivo_ip": r.dispositivo_ip,
            "total_falhas": r.total_falhas,
        }
        for r in rows
    ]

    return {
        "empresa_id": empresa_id,
        "empresa_nome": empresa.nome,
        "periodo_dias": dias,
        "ranking": ranking,
    }
