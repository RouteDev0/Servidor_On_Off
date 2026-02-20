"""
Módulo responsável pelo gerenciamento de configurações de alerta.
Adaptado do original para usar dados do banco em vez de JSON.
"""

from typing import Dict, Any, Optional
from backend.config import get_settings

settings = get_settings()


class ConfigManager:
    """Constrói os payloads de alerta a partir dos dados de câmera e config global."""

    @staticmethod
    def construir_camera_info(
        cam: Dict[str, Any],
        nome_condominio: str,
        config_global: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if config_global:
            return {
                "cliente": config_global.get("cliente", nome_condominio),
                "particao": config_global.get("particao", settings.DEFAULT_PARTICAO),
                "empresa": config_global.get("empresa", 1),
                "identificacao": cam.get("identificacao", cam.get("name", "CAMERA")),
                "ocorrencia": config_global.get("ocorrencia", settings.DEFAULT_OCORRENCIA),
                "codigomaquina": cam.get(
                    "codigomaquina",
                    config_global.get("codigomaquina", settings.DEFAULT_CODIGOMAQUINA),
                ),
                "codigoconjuntodeocorrencias": config_global.get(
                    "codigoconjuntodeocorrencias",
                    settings.DEFAULT_CODIGOCONJUNTODEOCORRENCIAS,
                ),
                "setor": cam.get("setor", 1),
                "complemento": cam.get(
                    "complemento", f"{cam.get('name', 'CAMERA')} está offline"
                ),
                "nome": cam.get("name", "CAMERA"),
            }
        else:
            return {
                "cliente": cam.get("cliente", nome_condominio),
                "particao": cam.get("particao", settings.DEFAULT_PARTICAO),
                "empresa": cam.get("empresa", 1),
                "identificacao": cam.get("identificacao", cam.get("name", "CAMERA")),
                "ocorrencia": cam.get("ocorrencia", settings.DEFAULT_OCORRENCIA),
                "codigomaquina": cam.get("codigomaquina", settings.DEFAULT_CODIGOMAQUINA),
                "codigoconjuntodeocorrencias": cam.get(
                    "codigoconjuntodeocorrencias",
                    settings.DEFAULT_CODIGOCONJUNTODEOCORRENCIAS,
                ),
                "setor": cam.get("setor", 1),
                "complemento": cam.get(
                    "complemento", f"{cam.get('name', 'CAMERA')} está offline"
                ),
                "nome": cam.get("name", "CAMERA"),
            }

    @staticmethod
    def extrair_config_global(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extrai configuração global (agora com defaults do settings)."""
        if "particao" in data or "empresa" in data:
            return {
                "cliente": data.get("cliente"),
                "particao": data.get("particao", settings.DEFAULT_PARTICAO),
                "empresa": data.get("empresa"),
                "ocorrencia": data.get("ocorrencia", settings.DEFAULT_OCORRENCIA),
                "codigomaquina": data.get("codigomaquina", settings.DEFAULT_CODIGOMAQUINA),
                "codigoconjuntodeocorrencias": data.get(
                    "codigoconjuntodeocorrencias",
                    settings.DEFAULT_CODIGOCONJUNTODEOCORRENCIAS,
                ),
            }
        return None
