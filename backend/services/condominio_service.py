"""
Serviço de processamento de condomínios – adaptado do original.

Em vez de ler arquivos JSON, consome dados agrupados pelo db_data_loader.
"""

from typing import Dict, Any
from backend.services.verification_service import VerificationService
from backend.core.config_manager import ConfigManager


class CondominioService:
    """Classe responsável por gerenciar condomínios (agora via banco)."""

    def __init__(self, verification_service: VerificationService):
        self.verification_service = verification_service

    def processar_condominio(
        self, nome_condominio: str, data: Dict[str, Any]
    ) -> bool:
        """
        Processa um condomínio/cliente a partir dos dados carregados do banco.

        data: dict com estrutura idêntica ao antigo JSON:
            {
                "cliente": "...",
                "particao": "01",
                "empresa": ...,
                "dvrs": [{"ip":..., "cameras": [...]}]
            }
        """
        try:
            cameras = []

            for dvr in data.get("dvrs", []):
                dvr_protocol = dvr.get("protocol", "hikvision").lower()
                for camera in dvr.get("cameras", []):
                    camera = camera.copy()
                    camera["_dvr_ip"] = dvr.get("ip")
                    camera["_dvr_porta"] = dvr.get("porta", 80)
                    camera["_dvr_protocol"] = dvr_protocol
                    camera["_dvr_usuario"] = dvr.get("usuario", "admin")
                    camera["_dvr_senha"] = dvr.get("senha", "admin")
                    cameras.append(camera)

            # Suporte a cameras_individuais (se vier do banco com essa estrutura)
            for camera in data.get("cameras_individuais", []):
                camera = camera.copy()
                camera["_dvr_ip"] = camera.get("ip")
                camera["_dvr_porta"] = camera.get("porta", 80)
                camera["_dvr_protocol"] = camera.get("protocol", "intelbras").lower()
                camera["_dvr_usuario"] = camera.get("usuario", "admin")
                camera["_dvr_senha"] = camera.get("senha", "admin")
                cameras.append(camera)

            config_global = ConfigManager.extrair_config_global(data)
            self.verification_service.verificar_cameras(
                cameras, nome_condominio, config_global
            )
            return True

        except Exception as e:
            print(f"[ERRO] Falha ao processar {nome_condominio}: {e}")
            return False
