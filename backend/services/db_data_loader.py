"""
Carregador de dados do MySQL – substitui a leitura de arquivos JSON.

Faz um JOIN entre empresa → clientes → dispositivos → pontos_monitoramento
e agrupa os dados em memória no mesmo formato dict que o serviço de verificação espera.
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.models import Empresa, Cliente, Dispositivo, PontoMonitoramento
from backend.config import get_settings


settings = get_settings()


def _marca_to_protocol(marca: str | None) -> str:
    """Converte a marca do dispositivo para o protocolo de verificação."""
    if not marca:
        return settings.DEFAULT_PROTOCOL
    marca_lower = marca.lower()
    if "intelbras" in marca_lower or "dahua" in marca_lower:
        return "intelbras"
    return "hikvision"


def _canal_fisico_to_channel(canal_fisico: int | None, protocol: str) -> str:
    """
    Converte canal_fisico (int) para o formato de canal esperado pelo protocolo.

    Hikvision: canal 1 → "101", canal 2 → "201", canal 15 → "1501"
    Intelbras:  canal 1 → "1",   canal 2 → "2",   canal 15 → "15"
    """
    if canal_fisico is None:
        return "101" if protocol == "hikvision" else "1"

    if protocol == "hikvision":
        return f"{canal_fisico}01"
    return str(canal_fisico)


def carregar_dados_do_banco(db: Session) -> Dict[str, Dict[str, Any]]:
    """
    Consulta o banco e retorna um dicionário agrupado por cliente (nome),
    com a mesma estrutura que o antigo JSON produzia:

    {
        "Nome do Cliente": {
            "cliente": "codigo_moni",
            "particao": "01",
            "empresa": empresa_moni,
            "empresa_id": 1,
            "empresa_nome": "Empresa X",
            "ocorrencia": 960,
            "codigomaquina": 897,
            "codigoconjuntodeocorrencias": 7,
            "dvrs": [
                {
                    "ip": "...",
                    "porta": 80,
                    "protocol": "hikvision",
                    "usuario": "admin",
                    "senha": "...",
                    "cliente": "codigo_moni",
                    "cameras": [
                        {
                            "name": "Setor 1 - ...",
                            "canal": "101",
                            "identificacao": "E",
                            "setor": 1,
                            "complemento": "...",
                            "codigomaquina": 897,
                        }
                    ]
                }
            ]
        }
    }
    """
    # Query com JOINs
    rows = (
        db.query(
            Empresa.id.label("empresa_id"),
            Empresa.nome.label("empresa_nome"),
            Empresa.empresa_moni,
            Cliente.codigo_moni,
            Cliente.nome.label("cliente_nome"),
            Dispositivo.id.label("dispositivo_id"),
            Dispositivo.marca,
            Dispositivo.ip,
            Dispositivo.porta,
            Dispositivo.usuario,
            Dispositivo.senha,
            Dispositivo.servicos,
            PontoMonitoramento.uuid_camera,
            PontoMonitoramento.numero_setor,
            PontoMonitoramento.canal_fisico,
            PontoMonitoramento.complemento,
        )
        .join(Cliente, Cliente.empresa_id == Empresa.id)
        .join(Dispositivo, Dispositivo.codigo_moni == Cliente.codigo_moni)
        .join(
            PontoMonitoramento,
            PontoMonitoramento.dispositivo_id == Dispositivo.id,
        )
        .filter(Dispositivo.servicos.like("%on_off%"))
        .all()
    )

    # Agrupar em memória
    clientes_dict: Dict[str, Dict[str, Any]] = {}
    dispositivos_por_cliente: Dict[str, Dict[str, Dict[str, Any]]] = {}

    for row in rows:
        cliente_key = row.cliente_nome or row.codigo_moni
        protocol = _marca_to_protocol(row.marca)
        canal = _canal_fisico_to_channel(row.canal_fisico, protocol)

        # Inicializa cliente se não existe
        if cliente_key not in clientes_dict:
            clientes_dict[cliente_key] = {
                "cliente": row.codigo_moni,
                "particao": settings.DEFAULT_PARTICAO,
                "empresa": row.empresa_moni or settings.DEFAULT_OCORRENCIA,
                "empresa_id": row.empresa_id,
                "empresa_nome": row.empresa_nome,
                "ocorrencia": settings.DEFAULT_OCORRENCIA,
                "codigomaquina": settings.DEFAULT_CODIGOMAQUINA,
                "codigoconjuntodeocorrencias": settings.DEFAULT_CODIGOCONJUNTODEOCORRENCIAS,
                "dvrs": [],
            }
            dispositivos_por_cliente[cliente_key] = {}

        # Inicializa dispositivo se não existe
        disp_key = row.dispositivo_id
        if disp_key not in dispositivos_por_cliente[cliente_key]:
            disp_data = {
                "ip": row.ip,
                "porta": row.porta or 80,
                "protocol": protocol,
                "usuario": row.usuario or "admin",
                "senha": row.senha or "admin",
                "cliente": row.codigo_moni,
                "cameras": [],
            }
            dispositivos_por_cliente[cliente_key][disp_key] = disp_data
            clientes_dict[cliente_key]["dvrs"].append(disp_data)

        # Adiciona câmera ao dispositivo
        camera_data = {
            "name": row.complemento or f"Setor {row.numero_setor}",
            "canal": canal,
            "identificacao": "E",
            "codigomaquina": settings.DEFAULT_CODIGOMAQUINA,
            "setor": row.numero_setor or 1,
            "complemento": row.complemento or f"Setor {row.numero_setor}",
            "uuid_camera": row.uuid_camera,
        }
        dispositivos_por_cliente[cliente_key][disp_key]["cameras"].append(camera_data)

    return clientes_dict


def carregar_dados_por_empresa(db: Session, empresa_id: int | None = None) -> Dict[str, Dict[str, Any]]:
    """
    Mesma lógica de carregar_dados_do_banco, mas com filtro opcional por empresa.
    """
    if empresa_id is None:
        return carregar_dados_do_banco(db)

    # Query com JOINs + filtro
    rows = (
        db.query(
            Empresa.id.label("empresa_id"),
            Empresa.nome.label("empresa_nome"),
            Empresa.empresa_moni,
            Cliente.codigo_moni,
            Cliente.nome.label("cliente_nome"),
            Dispositivo.id.label("dispositivo_id"),
            Dispositivo.marca,
            Dispositivo.ip,
            Dispositivo.porta,
            Dispositivo.usuario,
            Dispositivo.senha,
            Dispositivo.servicos,
            PontoMonitoramento.uuid_camera,
            PontoMonitoramento.numero_setor,
            PontoMonitoramento.canal_fisico,
            PontoMonitoramento.complemento,
        )
        .join(Cliente, Cliente.empresa_id == Empresa.id)
        .join(Dispositivo, Dispositivo.codigo_moni == Cliente.codigo_moni)
        .join(
            PontoMonitoramento,
            PontoMonitoramento.dispositivo_id == Dispositivo.id,
        )
        .filter(Dispositivo.servicos.like("%on_off%"))
        .filter(Empresa.id == empresa_id)
        .all()
    )

    clientes_dict: Dict[str, Dict[str, Any]] = {}
    dispositivos_por_cliente: Dict[str, Dict[str, Dict[str, Any]]] = {}

    for row in rows:
        cliente_key = row.cliente_nome or row.codigo_moni
        protocol = _marca_to_protocol(row.marca)
        canal = _canal_fisico_to_channel(row.canal_fisico, protocol)

        if cliente_key not in clientes_dict:
            clientes_dict[cliente_key] = {
                "cliente": row.codigo_moni,
                "particao": settings.DEFAULT_PARTICAO,
                "empresa": row.empresa_moni or settings.DEFAULT_OCORRENCIA,
                "empresa_id": row.empresa_id,
                "empresa_nome": row.empresa_nome,
                "ocorrencia": settings.DEFAULT_OCORRENCIA,
                "codigomaquina": settings.DEFAULT_CODIGOMAQUINA,
                "codigoconjuntodeocorrencias": settings.DEFAULT_CODIGOCONJUNTODEOCORRENCIAS,
                "dvrs": [],
            }
            dispositivos_por_cliente[cliente_key] = {}

        disp_key = row.dispositivo_id
        if disp_key not in dispositivos_por_cliente[cliente_key]:
            disp_data = {
                "ip": row.ip,
                "porta": row.porta or 80,
                "protocol": protocol,
                "usuario": row.usuario or "admin",
                "senha": row.senha or "admin",
                "cliente": row.codigo_moni,
                "cameras": [],
            }
            dispositivos_por_cliente[cliente_key][disp_key] = disp_data
            clientes_dict[cliente_key]["dvrs"].append(disp_data)

        camera_data = {
            "name": row.complemento or f"Setor {row.numero_setor}",
            "canal": canal,
            "identificacao": "E",
            "codigomaquina": settings.DEFAULT_CODIGOMAQUINA,
            "setor": row.numero_setor or 1,
            "complemento": row.complemento or f"Setor {row.numero_setor}",
            "uuid_camera": row.uuid_camera,
        }
        dispositivos_por_cliente[cliente_key][disp_key]["cameras"].append(camera_data)

    return clientes_dict
