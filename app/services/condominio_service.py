"""
Módulo responsável pelo serviço de condomínios
"""

import os
from typing import Dict, Any, Optional
from ..utils.file_utils import FileUtils
from ..core.config_manager import ConfigManager
from ..services.verification_service import VerificationService


class CondominioService:
    """Classe responsável por gerenciar condomínios"""

    def __init__(self, verification_service: VerificationService):
        self.verification_service = verification_service

    def processar_condominio(self, arquivo: str, pasta_condominios: str) -> bool:
        """Processa um condomínio individual - usado para paralelização"""
        caminho = os.path.join(pasta_condominios, arquivo)
        try:
            data = FileUtils.carregar_cameras(caminho)
            # Suporte a estrutura antiga (cameras), nova (dvrs) e mais nova (dvs)
            cameras = []
            if "dvrs" in data:
                for dvr in data["dvrs"]:
                    # Injeta informações do DVR em cada câmera
                    for camera in dvr.get("cameras", []):
                        camera = camera.copy()
                        camera["_dvr_ip"] = dvr.get("ip")
                        camera["_dvr_porta"] = dvr.get("porta", 80)
                        cameras.append(camera)
            elif "dvs" in data:
                for dv in data["dvs"]:
                    # Injeta informações do DV em cada câmera
                    for camera in dv.get("cameras", []):
                        camera = camera.copy()
                        camera["_dvr_ip"] = dv.get("ip")
                        camera["_dvr_porta"] = dv.get("porta", 80)
                        cameras.append(camera)
            else:
                cameras = data.get("cameras", [])
            # usa exatamente o nome do arquivo JSON (sem extensão) como nome do condomínio
            nome_condominio = os.path.splitext(arquivo)[0]
            # Extrai configuração global (nova estrutura) ou usa None (estrutura antiga)
            config_global = ConfigManager.extrair_config_global(data)
            self.verification_service.verificar_cameras(
                cameras, nome_condominio, config_global
            )
            return True
        except Exception as e:
            print(f"[ERRO] Falha ao processar {arquivo}: {e}")
            return False

    def obter_pasta_condominios(self) -> str:
        """Obtém o caminho da pasta de condomínios"""
        from app.config import Config

        return Config.CONDOMINIOS_DIR
