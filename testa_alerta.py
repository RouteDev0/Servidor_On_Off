# arquivo: alerta_manual.py
import os
import json
import requests
from requests.auth import HTTPBasicAuth
import time
import sys
from app.config import Config

# Config da API
API_URL = Config.API_URL
API_CREDENTIALS = HTTPBasicAuth(Config.API_USERNAME, Config.API_PASSWORD)


def enviar_alerta(camera_info, condominio_nome):
    payload = {
        "comando": (
            "INSERT INTO EventosNaoProcessados(DataHora, Cliente, Particao, Empresa, Ocorrencia, Identificacao, Codigomaquina, "
            "CodigoConjuntoOcorrencias, Setor, Complemento) "
            f"VALUES (CURRENT_TIMESTAMP, '{camera_info['cliente']}', '{camera_info['particao']}', {camera_info['empresa']}, "
            f"'{camera_info['ocorrencia']}', '{camera_info['identificacao']}', {camera_info['codigomaquina']}, {camera_info['codigoconjuntodeocorrencias']}, "
            f"{camera_info['setor']}, '{camera_info['complemento']} - {time.strftime('%H:%M:%S')}')"
        )
    }
    headers = {"Content-Type": "application/json; charset=UTF-8"}

    try:
        response = requests.post(
            API_URL, json=payload, headers=headers, auth=API_CREDENTIALS, timeout=5
        )
        response.raise_for_status()
        print(
            f"🚨 Alerta enviado com sucesso - {condominio_nome}/{camera_info['nome']}"
        )
        return True
    except Exception as e:
        print(f"⚠️ Erro ao enviar alerta - {condominio_nome}/{camera_info['nome']}: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Uso: python alerta_manual.py caminho/do/arquivo.json")
        return

    arquivo = sys.argv[1]
    if not os.path.exists(arquivo):
        print(f"❌ Arquivo não encontrado: {arquivo}")
        return

    with open(arquivo, "r", encoding="utf-8") as f:
        dados = json.load(f)

    condominio_nome = os.path.basename(arquivo).replace(".json", "")

    # Campos comuns
    particao = dados["particao"]
    empresa = dados["empresa"]
    ocorrencia = dados["ocorrencia"]
    codigomaquina = dados["codigomaquina"]
    codigoconjuntodeocorrencias = dados["codigoconjuntodeocorrencias"]

    for dvr in dados.get("dvrs", []):
        cliente = dvr["cliente"]
        for cam in dvr.get("cameras", []):
            camera_info = {
                "cliente": cliente,
                "particao": particao,
                "empresa": empresa,
                "ocorrencia": ocorrencia,
                "codigomaquina": codigomaquina,
                "codigoconjuntodeocorrencias": codigoconjuntodeocorrencias,
                "identificacao": cam["identificacao"],
                "setor": cam["setor"],
                "complemento": cam["complemento"],
                "nome": cam["name"],
            }

            enviar_alerta(camera_info, condominio_nome)


if __name__ == "__main__":
    main()
