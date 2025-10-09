import os
import json
from glob import glob

PASTA = "app/data/condominios"

# Busca todos os arquivos .json únicos
arquivos = set(glob(os.path.join(PASTA, "*.json")))

for caminho in arquivos:
    nome_arquivo = os.path.basename(caminho)
    try:
        with open(caminho, encoding="utf-8") as f:
            dados = json.load(f)
    except Exception as e:
        print(f"Erro ao ler {nome_arquivo}: {e}")
        continue

    dados["empresa"] = 4

    if "dvrs" in dados:
        for dvr in dados["dvrs"]:
            dvr["codigomaquina"] = 897
            if "cameras" in dvr:
                for cam in dvr["cameras"]:
                    cam["identificacao"] = "E"
                    cam["codigomaquina"] = 897

    if "cameras" in dados:
        for cam in dados["cameras"]:
            cam["identificacao"] = "E"
            cam["codigomaquina"] = 897

    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

print("Todos os arquivos atualizados!")