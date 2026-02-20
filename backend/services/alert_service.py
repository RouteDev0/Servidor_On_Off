"""
Serviço de envio de alertas para a API Moni.
Adaptado do original para usar configurações via Pydantic Settings.
"""

import time
import requests
from requests.auth import HTTPBasicAuth
from backend.config import get_settings

settings = get_settings()
auth = HTTPBasicAuth(settings.MONI_API_USER, settings.MONI_API_PASS)


def enviar_alerta(camera_info: dict, condominio_nome: str) -> bool:
    """
    Envia alerta para a API Moni.
    camera_info: dict com os campos necessários
    condominio_nome: str, nome do condomínio
    """
    payload = {
        "comando": (
            "INSERT INTO EventosNaoProcessados(DataHora, Cliente, Particao, Empresa, "
            "Ocorrencia, Identificacao, Codigomaquina, CodigoConjuntoOcorrencias, "
            "Setor, Complemento) "
            f"VALUES (CURRENT_TIMESTAMP, '{camera_info['cliente']}', "
            f"'{camera_info['particao']}', {camera_info['empresa']}, "
            f"'{camera_info['ocorrencia']}', '{camera_info['identificacao']}', "
            f"{camera_info['codigomaquina']}, "
            f"{camera_info['codigoconjuntodeocorrencias']}, "
            f"{camera_info['setor']}, "
            f"'{camera_info['complemento']} - {time.strftime('%H:%M:%S')}')"
        )
    }

    try:
        print(
            f"\n📤 Enviando alerta - {condominio_nome}/{camera_info.get('nome', 'SemNome')}"
        )
        response = requests.post(
            settings.MONI_API_URL,
            json=payload,
            headers={"Content-Type": "application/json; charset=UTF-8"},
            auth=auth,
            timeout=5,
        )
        response.raise_for_status()
        print(f"✅ Alerta enviado com sucesso - Status: {response.status_code}")
        return True
    except Exception as e:
        print(
            f"❌ Erro ao enviar alerta - {condominio_nome}/"
            f"{camera_info.get('nome', 'SemNome')}: {e}"
        )
        return False
