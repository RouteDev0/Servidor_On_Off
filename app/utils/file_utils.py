"""
Módulo responsável por utilitários de arquivo
"""
import os
import json
from typing import List, Dict, Any


class FileUtils:
    """Classe responsável por operações com arquivos"""
    
    @staticmethod
    def carregar_cameras(path: str) -> Dict[str, Any]:
        """Carrega arquivo JSON de configuração de câmeras"""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def listar_arquivos_json(pasta: str) -> List[str]:
        """Lista todos os arquivos JSON em uma pasta"""
        return [f for f in os.listdir(pasta) if f.endswith('.json')]
    
    @staticmethod
    def nome_condominio_por_arquivo(nome_arquivo: str) -> str:
        """Converte nome do arquivo em nome do condomínio"""
        base = os.path.splitext(nome_arquivo)[0]
        return base.replace('_', ' ').title() 