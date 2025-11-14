"""
Módulo responsável pelo serviço de verificação
"""

import time
import concurrent.futures
from typing import Dict, Any, List, Optional
from ..core.config_manager import ConfigManager
from ..utils.cache_manager import CacheManager
from app.config import Config
from app.alert import enviar_alerta


class VerificationService:
    """Classe responsável por gerenciar verificações de câmeras"""

    def __init__(self):
        self.cache_manager = CacheManager()
        self.ultimo_estado: Dict[str, bool] = {}
        self.status_atual: Dict[str, List[Dict[str, str]]] = {}

    def verificar_camera_individual(
        self,
        cam: Dict[str, Any],
        nome_condominio: str,
        config_global: Optional[Dict[str, Any]] = None,
    ) -> tuple[str, str]:
        """Verifica uma câmera individual usando snapshot da API Hikvision (HTTPDigestAuth)"""
        import requests
        from requests.auth import HTTPDigestAuth

        nome = cam.get("name", "CAMERA")
        # Tenta obter IP e porta do nível da câmera, se não encontrar, usa do DVR/DV
        ip = cam.get("ip") or cam.get(
            "_dvr_ip"
        )  # _dvr_ip será injetado pelo método verificar_cameras
        porta = cam.get("porta") or cam.get(
            "_dvr_porta", 80
        )  # _dvr_porta será injetado pelo método verificar_cameras
        canal = cam.get("canal") or cam.get("channel") or "101"
        usuario = cam.get("usuario") or cam.get("user") or "admin"
        senha = cam.get("senha") or cam.get("password") or "admin"

        if not ip or not usuario or not senha:
            print(f"[⚠️] {nome} não possui dados de conexão suficientes. IP: {ip}")
            return nome, "NO_CONFIG"

        # Verifica cache primeiro
        chave_cache = f"{nome_condominio}_{nome}_{ip}_{canal}"
        resultado_encontrado, resultado_cache = self.cache_manager.get_cached_result(
            chave_cache
        )
        if resultado_encontrado:
            status_str = "ON" if resultado_cache else "OFF"
            print(f"📷 {nome} está {status_str} (cache)")
            chave = f"{nome_condominio}_{nome}"
            estado_anterior = self.ultimo_estado.get(chave)
            if estado_anterior is False and resultado_cache:
                cam_info = ConfigManager.construir_camera_info(
                    cam, nome_condominio, config_global
                )
                cam_info["ocorrencia"] = "941"
                cam_info["complemento"] = f"{nome} voltou online"
                enviar_alerta(cam_info, nome_condominio)
            if estado_anterior != resultado_cache and not resultado_cache:
                cam_info = ConfigManager.construir_camera_info(
                    cam, nome_condominio, config_global
                )
                enviar_alerta(cam_info, nome_condominio)
            self.ultimo_estado[chave] = resultado_cache
            return nome, status_str

        # Verificação real via snapshot API Hikvision
        url = f"http://{ip}:{porta}/ISAPI/Streaming/channels/{canal}/picture"
        try:
            resp = requests.get(url, auth=HTTPDigestAuth(usuario, senha), timeout=8)
            online = resp.status_code == 200 and resp.headers.get(
                "Content-Type", ""
            ).startswith("image")
        except Exception as e:
            print(f"[ERRO] {nome}: {e}")
            online = False
        status_str = "ON" if online else "OFF"
        print(f"📷 {nome} está {status_str}")

        # Atualiza cache
        self.cache_manager.set_cached_result(chave_cache, online)

        # Atualiza contador de falhas consecutivas
        chave_falhas = f"{nome_condominio}_{nome}"
        self.cache_manager.update_falhas_consecutivas(chave_falhas, online)

        chave = f"{nome_condominio}_{nome}"
        estado_anterior = self.ultimo_estado.get(chave)

        # Envia alerta se voltou online
        if estado_anterior is False and online:
            cam_info = ConfigManager.construir_camera_info(
                cam, nome_condominio, config_global
            )
            cam_info["ocorrencia"] = "941"
            cam_info["complemento"] = f"{nome} voltou online"
            enviar_alerta(cam_info, nome_condominio)

        # Envia alerta se acabou de cair
        if estado_anterior != online and not online:
            cam_info = ConfigManager.construir_camera_info(
                cam, nome_condominio, config_global
            )
            enviar_alerta(cam_info, nome_condominio)

        self.ultimo_estado[chave] = online
        return nome, status_str

    def verificar_cameras(
        self,
        cameras: List[Dict[str, Any]],
        nome_condominio: str = "Condomínio",
        config_global: Optional[Dict[str, Any]] = None,
    ):
        """Verifica múltiplas câmeras em paralelo, mas com limite de concorrência e delay para não sobrecarregar a rede"""
        # Inicializa com metadados do condomínio se disponível
        self.status_atual[nome_condominio] = {
            "cameras": [],
            "metadata": config_global or {},
        }

        # Debug para verificar se os metadados estão sendo extraídos
        if config_global:
            print(
                f"[DEBUG] ✅ {nome_condominio} - Empresa: {config_global.get('empresa')} - Metadados: {config_global}"
            )
        else:
            print(f"[DEBUG] ❌ {nome_condominio} - NENHUM metadado extraído!")

        if not cameras:
            return

        # Limpa cache antigo periodicamente
        self.cache_manager.limpar_cache_antigo()

        # Limite de concorrência e delay configuráveis
        num_cameras = len(cameras)
        max_workers = min(getattr(Config, "MAX_WORKERS_CAMERAS", 2), num_cameras) or 1
        delay_entre_cameras = getattr(Config, "DELAY_ENTRE_CAMERAS", 0.5)

        print(
            f"[INFO] Verificando {num_cameras} câmeras em {nome_condominio} com {max_workers} workers e delay de {delay_entre_cameras}s"
        )

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for cam in cameras:
                # Se a câmera não tem IP próprio, injeta o IP e porta do DVR/DV
                if not cam.get("ip") and "_dvr_ip" in cam:
                    cam = cam.copy()  # Cria uma cópia para não modificar o original
                cam["_dvr_ip"] = cam.get(
                    "_dvr_ip"
                )  # Mantém o IP do DVR se já estiver definido
                cam["_dvr_porta"] = cam.get(
                    "_dvr_porta"
                )  # Mantém a porta do DVR se já estiver definida

                futures.append(
                    executor.submit(
                        self.verificar_camera_individual,
                        cam,
                        nome_condominio,
                        config_global,
                    )
                )
                time.sleep(
                    delay_entre_cameras
                )  # Pequeno delay entre submissões para não sobrecarregar a rede

            # Processa resultados conforme ficam prontos
            for future in concurrent.futures.as_completed(futures):
                try:
                    nome, status_str = future.result()
                    if status_str != "NO_RTSP":
                        self.status_atual[nome_condominio]["cameras"].append(
                            {"nome": nome, "status": status_str}
                        )
                except Exception as e:
                    print(f"[ERRO] Erro ao processar câmera em thread: {e}")

    def get_status_atual(self) -> Dict[str, List[Dict[str, str]]]:
        """Retorna o status atual de todas as câmeras"""
        return self.status_atual
