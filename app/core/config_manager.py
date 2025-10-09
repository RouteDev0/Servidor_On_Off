"""
Módulo responsável pelo gerenciamento de configurações
"""

from typing import Dict, Any, Optional


class ConfigManager:
    """Classe responsável por gerenciar configurações de câmeras e condomínios"""

    @staticmethod
    def construir_camera_info(
        cam: Dict[str, Any],
        nome_condominio: str,
        config_global: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Constrói informações da câmera usando configuração global ou valores padrão
        """
        if config_global:
            return {
                "cliente": config_global.get("cliente", nome_condominio),
                "particao": config_global.get("particao", "1"),
                "empresa": config_global.get("empresa", 1),
                "identificacao": cam.get("identificacao", cam.get("name", "CAMERA")),
                "ocorrencia": config_global.get("ocorrencia", "CAMERA_OFFLINE"),
                "codigomaquina": cam.get(
                    "codigomaquina", config_global.get("codigomaquina", 1)
                ),
                "codigoconjuntodeocorrencias": config_global.get(
                    "codigoconjuntodeocorrencias", 1
                ),
                "setor": cam.get("setor", 1),
                "complemento": cam.get(
                    "complemento", f"{cam.get('name', 'CAMERA')} está offline"
                ),
                "nome": cam.get("name", "CAMERA"),
            }
        else:
            # Fallback para estrutura antiga (compatibilidade)
            return {
                "cliente": cam.get("cliente", nome_condominio),
                "particao": cam.get("particao", "1"),
                "empresa": cam.get("empresa", 1),
                "identificacao": cam.get("identificacao", cam.get("name", "CAMERA")),
                "ocorrencia": cam.get("ocorrencia", "CAMERA_OFFLINE"),
                "codigomaquina": cam.get("codigomaquina", 1),
                "codigoconjuntodeocorrencias": cam.get(
                    "codigoconjuntodeocorrencias", 1
                ),
                "setor": cam.get("setor", 1),
                "complemento": cam.get(
                    "complemento", f"{cam.get('name', 'CAMERA')} está offline"
                ),
                "nome": cam.get("name", "CAMERA"),
            }

    @staticmethod
    def extrair_config_global(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extrai configuração global do JSON do condomínio
        Suporta tanto estrutura simples quanto estrutura com DVRs
        """
        # Verifica se tem os campos básicos no nível raiz
        if "particao" in data or "empresa" in data:
            return {
                "cliente": data.get("cliente"),
                "particao": data.get("particao"),
                "empresa": data.get("empresa"),
                "ocorrencia": data.get("ocorrencia"),
                "codigomaquina": data.get("codigomaquina"),
                "codigoconjuntodeocorrencias": data.get("codigoconjuntodeocorrencias"),
            }
        return None
