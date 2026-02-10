# aler.py
import requests
from requests.auth import HTTPBasicAuth
import time

API_URL = "http://192.168.2.50:555/ExecutarComando"
API_USER = "moni"
API_PASS = "moni"
auth = HTTPBasicAuth(API_USER, API_PASS)


def enviar_alerta(camera_info, condominio_nome):
    """
    Envia alerta para a API Moni.
    camera_info: dict com os campos necessários (cliente, particao, empresa, ocorrencia, codigomaquina, codigoconjuntodeocorrencias, identificacao, setor, complemento, nome)
    condominio_nome: str, nome do condomínio
    """
    payload = {
        "comando": (
            "INSERT INTO EventosNaoProcessados(DataHora, Cliente, Particao, Empresa, Ocorrencia, Identificacao, Codigomaquina, "
            "CodigoConjuntoOcorrencias, Setor, Complemento) "
            f"VALUES (CURRENT_TIMESTAMP, '{camera_info['cliente']}', '{camera_info['particao']}', {camera_info['empresa']}, "
            f"'{camera_info['ocorrencia']}', '{camera_info['identificacao']}', {camera_info['codigomaquina']}, {camera_info['codigoconjuntodeocorrencias']}, "
            f"{camera_info['setor']}, '{camera_info['complemento']} - {time.strftime('%H:%M:%S')}')"
        )
    }

    try:
        print(
            f"\n📤 Enviando alerta - {condominio_nome}/{camera_info.get('nome', 'SemNome')}"
        )
        response = requests.post(
            API_URL,
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
            f"❌ Erro ao enviar alerta - {condominio_nome}/{camera_info.get('nome', 'SemNome')}: {e}"
        )
        return False
