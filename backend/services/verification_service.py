"""
Serviço de verificação de câmeras – adaptado do original.

Mantém toda a lógica de verificação (Hikvision ISAPI / Intelbras CGI),
cache, retry com backoff, e envio de alertas.

Adicionado: gravação de historico_eventos no banco quando há mudança de estado.
"""

import time
import concurrent.futures
from typing import Dict, Any, List, Optional, Union

from backend.core.cache_manager import CacheManager
from backend.core.config_manager import ConfigManager
from backend.utils.protocol_utils import ProtocolUtils
from backend.services.alert_service import enviar_alerta
from backend.config import get_settings

settings = get_settings()


class VerificationService:
    """Classe responsável por gerenciar verificações de câmeras"""

    def __init__(self):
        self.cache_manager = CacheManager()
        self.ultimo_estado: Dict[str, bool] = {}
        self.status_atual: Dict[str, Any] = {}

        # Pool de conexões HTTP reutilizável
        self.http_session = None
        if settings.USE_CONNECTION_POOL:
            import requests
            from requests.adapters import HTTPAdapter

            self.http_session = requests.Session()
            adapter = HTTPAdapter(
                pool_connections=settings.CONNECTION_POOL_SIZE,
                pool_maxsize=settings.CONNECTION_POOL_MAXSIZE,
                max_retries=0,
            )
            self.http_session.mount("http://", adapter)
            self.http_session.mount("https://", adapter)
            print(
                f"[INFO] ✅ Pool de conexões HTTP ativado - {settings.CONNECTION_POOL_SIZE} conexões"
            )

        # Fila de eventos para gravar de forma assíncrona
        self._pending_events: List[Dict[str, Any]] = []

    # ── Registro de eventos ─────────────────────────────────────────

    def registrar_evento(self, uuid_camera: Union[str, None], tipo_evento: str):
        """Enfileira evento para gravação posterior no banco."""
        if uuid_camera:
            self._pending_events.append(
                {"ponto_id": uuid_camera, "tipo_evento": tipo_evento}
            )

    def flush_eventos(self, db_session):
        """Grava todos os eventos pendentes no banco de dados."""
        if not self._pending_events:
            return
        from backend.models import HistoricoEvento

        try:
            for evt in self._pending_events:
                db_session.add(HistoricoEvento(**evt))
            db_session.commit()
            print(
                f"[INFO] 📝 {len(self._pending_events)} eventos gravados no histórico"
            )
        except Exception as e:
            db_session.rollback()
            print(f"[ERRO] Falha ao gravar eventos: {e}")
        finally:
            self._pending_events.clear()

    # ── Dispatcher ──────────────────────────────────────────────────

    def verificar_camera_individual(
        self,
        cam: Dict[str, Any],
        nome_condominio: str,
        config_global: Optional[Dict[str, Any]] = None,
    ) -> tuple[str, str]:
        protocol = ProtocolUtils.get_protocol_from_camera(cam)

        if protocol == "intelbras":
            return self.verificar_camera_intelbras(cam, nome_condominio, config_global)
        else:
            return self.verificar_camera_hikvision(cam, nome_condominio, config_global)

    # ── Hikvision ───────────────────────────────────────────────────

    def verificar_camera_hikvision(
        self,
        cam: Dict[str, Any],
        nome_condominio: str,
        config_global: Optional[Dict[str, Any]] = None,
    ) -> tuple[str, str]:
        import requests
        from requests.auth import HTTPDigestAuth

        nome = cam.get("name", "CAMERA")
        ip = cam.get("ip") or cam.get("_dvr_ip")
        porta = cam.get("porta") or cam.get("_dvr_porta", 80)
        canal = cam.get("canal") or cam.get("channel") or "101"
        usuario = cam.get("_dvr_usuario") or cam.get("usuario") or "admin"
        senha = cam.get("_dvr_senha") or cam.get("senha") or "admin"

        if not ip or not usuario or not senha:
            print(f"[⚠️] {nome} não possui dados de conexão suficientes. IP: {ip}")
            return nome, "NO_CONFIG"

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
                cam_info["ocorrencia"] = "961"
                cam_info["complemento"] = f"{nome} voltou online"
                enviar_alerta(cam_info, nome_condominio)
                self.registrar_evento(cam.get("uuid_camera"), "961")
            if estado_anterior != resultado_cache and not resultado_cache:
                cam_info = ConfigManager.construir_camera_info(
                    cam, nome_condominio, config_global
                )
                enviar_alerta(cam_info, nome_condominio)
                self.registrar_evento(cam.get("uuid_camera"), "960")
            self.ultimo_estado[chave] = resultado_cache
            return nome, status_str

        url = f"http://{ip}:{porta}/ISAPI/Streaming/channels/{canal}/picture"
        online = False
        ultima_exception = None

        for tentativa in range(settings.TENTATIVAS_RETRY + 1):
            try:
                if self.http_session:
                    resp = self.http_session.get(
                        url,
                        auth=HTTPDigestAuth(usuario, senha),
                        timeout=settings.TIMEOUT_VERIFICACAO,
                    )
                else:
                    resp = requests.get(
                        url,
                        auth=HTTPDigestAuth(usuario, senha),
                        timeout=settings.TIMEOUT_VERIFICACAO,
                    )

                if resp.status_code == 401:
                    ultima_exception = Exception("Senha Incorreta (401 Unauthorized)")
                    online = False
                    status_str = "SENHA_ERRADA"
                    break

                online = resp.status_code == 200 and resp.headers.get(
                    "Content-Type", ""
                ).startswith("image")

                if online:
                    break

            except Exception as e:
                ultima_exception = e
                if tentativa < settings.TENTATIVAS_RETRY:
                    backoff = settings.RETRY_BACKOFF * (2**tentativa)
                    time.sleep(backoff)
                continue

        if 'status_str' not in locals():
            status_str = "ON" if online else "OFF"
            
        if status_str == "SENHA_ERRADA":
            print(f"[⚠️] {nome}: Senha incorreta (401 Unauthorized)")
        else:
            if not online and ultima_exception:
                print(f"[ERRO] {nome}: {ultima_exception}")
            print(f"📷 {nome} está {status_str}")

        self.cache_manager.set_cached_result(chave_cache, online)

        chave_falhas = f"{nome_condominio}_{nome}"
        self.cache_manager.update_falhas_consecutivas(chave_falhas, online)

        chave = f"{nome_condominio}_{nome}"
        estado_anterior = self.ultimo_estado.get(chave)

        if estado_anterior is False and online:
            cam_info = ConfigManager.construir_camera_info(
                cam, nome_condominio, config_global
            )
            cam_info["ocorrencia"] = "961"
            cam_info["complemento"] = f"{nome} voltou online"
            enviar_alerta(cam_info, nome_condominio)
            self.registrar_evento(cam.get("uuid_camera"), "961")

        if estado_anterior != online and not online:
            cam_info = ConfigManager.construir_camera_info(
                cam, nome_condominio, config_global
            )
            enviar_alerta(cam_info, nome_condominio)
            self.registrar_evento(cam.get("uuid_camera"), "960")

        self.ultimo_estado[chave] = online
        return nome, status_str

    # ── Intelbras ───────────────────────────────────────────────────

    def verificar_camera_intelbras(
        self,
        cam: Dict[str, Any],
        nome_condominio: str,
        config_global: Optional[Dict[str, Any]] = None,
    ) -> tuple[str, str]:
        import requests
        from requests.auth import HTTPDigestAuth

        nome = cam.get("name", "CAMERA")
        ip = cam.get("ip") or cam.get("_dvr_ip")
        porta = cam.get("porta") or cam.get("_dvr_porta", 80)
        canal = cam.get("canal") or cam.get("channel") or "1"
        usuario = cam.get("_dvr_usuario") or cam.get("usuario") or "admin"
        senha = cam.get("_dvr_senha") or cam.get("senha") or "admin"

        if not ip or not usuario or not senha:
            print(f"[⚠️] {nome} não possui dados de conexão suficientes. IP: {ip}")
            return nome, "NO_CONFIG"

        canal = ProtocolUtils.convert_channel_to_intelbras(canal)

        chave_cache = f"{nome_condominio}_{nome}_{ip}_{canal}_intelbras"
        resultado_encontrado, resultado_cache = self.cache_manager.get_cached_result(
            chave_cache
        )
        if resultado_encontrado:
            status_str = "ON" if resultado_cache else "OFF"
            print(f"📷 {nome} está {status_str} (cache) [Intelbras]")
            chave = f"{nome_condominio}_{nome}"
            estado_anterior = self.ultimo_estado.get(chave)
            if estado_anterior is False and resultado_cache:
                cam_info = ConfigManager.construir_camera_info(
                    cam, nome_condominio, config_global
                )
                cam_info["ocorrencia"] = "961"
                cam_info["complemento"] = f"{nome} voltou online"
                enviar_alerta(cam_info, nome_condominio)
                self.registrar_evento(cam.get("uuid_camera"), "961")
            if estado_anterior != resultado_cache and not resultado_cache:
                cam_info = ConfigManager.construir_camera_info(
                    cam, nome_condominio, config_global
                )
                enviar_alerta(cam_info, nome_condominio)
                self.registrar_evento(cam.get("uuid_camera"), "960")
            self.ultimo_estado[chave] = resultado_cache
            return nome, status_str

        url = f"http://{ip}:{porta}/cgi-bin/snapshot.cgi?channel={canal}"
        online = False
        ultima_exception = None
        content_length = 0

        for tentativa in range(settings.TENTATIVAS_RETRY + 1):
            try:
                if self.http_session:
                    resp = self.http_session.get(
                        url,
                        auth=HTTPDigestAuth(usuario, senha),
                        timeout=settings.TIMEOUT_VERIFICACAO,
                    )
                else:
                    resp = requests.get(
                        url,
                        auth=HTTPDigestAuth(usuario, senha),
                        timeout=settings.TIMEOUT_VERIFICACAO,
                    )

                content_type_ok = resp.headers.get("Content-Type", "").startswith(
                    "image"
                )
                content_length = int(resp.headers.get("Content-Length", 0))
                size_ok = content_length >= settings.INTELBRAS_MIN_IMAGE_SIZE

                online = resp.status_code == 200 and content_type_ok and size_ok

                if resp.status_code == 401:
                    ultima_exception = Exception("Senha Incorreta (401 Unauthorized)")
                    online = False
                    status_str = "SENHA_ERRADA"
                    break

                if online:
                    break
                elif resp.status_code == 200 and content_type_ok and not size_ok:
                    print(
                        f"[⚠️] {nome}: Imagem muito pequena ({content_length} bytes)"
                    )
                    break

            except Exception as e:
                ultima_exception = e
                if tentativa < settings.TENTATIVAS_RETRY:
                    backoff = settings.RETRY_BACKOFF * (2**tentativa)
                    time.sleep(backoff)
                continue

        if 'status_str' not in locals():
            status_str = "ON" if online else "OFF"

        if status_str == "SENHA_ERRADA":
            print(f"[⚠️] {nome} [Intelbras]: Senha incorreta (401 Unauthorized)")
        else:
            if not online and ultima_exception:
                print(f"[ERRO] {nome} [Intelbras]: {ultima_exception}")
            elif not online and content_length > 0:
                print(
                    f"[INFO] {nome} [Intelbras]: Offline ou sem sinal ({content_length} bytes)"
                )
            print(f"📷 {nome} está {status_str} [Intelbras CGI]")

        self.cache_manager.set_cached_result(chave_cache, online)

        chave_falhas = f"{nome_condominio}_{nome}"
        self.cache_manager.update_falhas_consecutivas(chave_falhas, online)

        chave = f"{nome_condominio}_{nome}"
        estado_anterior = self.ultimo_estado.get(chave)

        if estado_anterior is False and online:
            cam_info = ConfigManager.construir_camera_info(
                cam, nome_condominio, config_global
            )
            cam_info["ocorrencia"] = "961"
            cam_info["complemento"] = f"{nome} voltou online"
            enviar_alerta(cam_info, nome_condominio)
            self.registrar_evento(cam.get("uuid_camera"), "961")

        if estado_anterior != online and not online:
            cam_info = ConfigManager.construir_camera_info(
                cam, nome_condominio, config_global
            )
            enviar_alerta(cam_info, nome_condominio)
            self.registrar_evento(cam.get("uuid_camera"), "960")

        self.ultimo_estado[chave] = online
        return nome, status_str

    # ── Verificar múltiplas câmeras ─────────────────────────────────

    def verificar_cameras(
        self,
        cameras: List[Dict[str, Any]],
        nome_condominio: str = "Condomínio",
        config_global: Optional[Dict[str, Any]] = None,
    ):
        self.status_atual[nome_condominio] = {
            "cameras": [],
            "metadata": config_global or {},
        }

        if config_global:
            print(
                f"[DEBUG] ✅ {nome_condominio} - Empresa: {config_global.get('empresa')}"
            )

        if not cameras:
            return

        self.cache_manager.limpar_cache_antigo()

        num_cameras = len(cameras)
        max_workers = min(settings.MAX_WORKERS_CAMERAS, num_cameras) or 1
        delay_entre_cameras = settings.DELAY_ENTRE_CAMERAS

        print(
            f"[INFO] Verificando {num_cameras} câmeras em {nome_condominio} "
            f"com {max_workers} workers e delay de {delay_entre_cameras}s"
        )

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for cam in cameras:
                if not cam.get("ip") and "_dvr_ip" in cam:
                    cam = cam.copy()
                cam["_dvr_ip"] = cam.get("_dvr_ip")
                cam["_dvr_porta"] = cam.get("_dvr_porta")

                futures.append(
                    executor.submit(
                        self.verificar_camera_individual,
                        cam,
                        nome_condominio,
                        config_global,
                    )
                )
                time.sleep(delay_entre_cameras)

            for future in concurrent.futures.as_completed(futures):
                try:
                    nome, status_str = future.result()
                    if status_str != "NO_RTSP":
                        self.status_atual[nome_condominio]["cameras"].append(
                            {"nome": nome, "status": status_str}
                        )
                except Exception as e:
                    print(f"[ERRO] Erro ao processar câmera em thread: {e}")

    def get_status_atual(self) -> Dict[str, Any]:
        """Retorna o status atual de todas as câmeras"""
        return self.status_atual
