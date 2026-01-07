"""
Módulo responsável pelo serviço de verificação
"""

import time
import concurrent.futures
from typing import Dict, Any, List, Optional
from ..core.config_manager import ConfigManager
from ..utils.cache_manager import CacheManager
from ..utils.protocol_utils import ProtocolUtils
from app.config import Config
from app.alert import enviar_alerta


class VerificationService:
    """Classe responsável por gerenciar verificações de câmeras"""

    def __init__(self):
        self.cache_manager = CacheManager()
        self.ultimo_estado: Dict[str, bool] = {}
        self.status_atual: Dict[str, List[Dict[str, str]]] = {}
        
        # Pool de conexões HTTP reutilizável para melhor performance
        self.http_session = None
        if Config.USE_CONNECTION_POOL:
            import requests
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            
            self.http_session = requests.Session()
            
            # Configurar adapter com pool de conexões
            adapter = HTTPAdapter(
                pool_connections=Config.CONNECTION_POOL_SIZE,
                pool_maxsize=Config.CONNECTION_POOL_MAXSIZE,
                max_retries=0  # Trataremos retry manualmente
            )
            self.http_session.mount('http://', adapter)
            self.http_session.mount('https://', adapter)
            
            print(f"[INFO] ✅ Pool de conexões HTTP ativado - {Config.CONNECTION_POOL_SIZE} conexões")

    def verificar_camera_individual(
        self,
        cam: Dict[str, Any],
        nome_condominio: str,
        config_global: Optional[Dict[str, Any]] = None,
    ) -> tuple[str, str]:
        """
        Dispatcher que roteia para o método de verificação apropriado baseado no protocolo do DVR
        
        O protocolo é injetado pelo condominio_service como '_dvr_protocol'
        """
        protocol = ProtocolUtils.get_protocol_from_camera(cam)
        
        if protocol == "intelbras":
            return self.verificar_camera_intelbras(cam, nome_condominio, config_global)
        else:  # hikvision or default
            return self.verificar_camera_hikvision(cam, nome_condominio, config_global)

    def verificar_camera_hikvision(
        self,
        cam: Dict[str, Any],
        nome_condominio: str,
        config_global: Optional[Dict[str, Any]] = None,
    ) -> tuple[str, str]:
        """Verifica uma câmera Hikvision usando snapshot da API ISAPI (HTTPDigestAuth)"""
        import requests
        from requests.auth import HTTPDigestAuth

        nome = cam.get("name", "CAMERA")
        # Tenta obter IP e porta do nível da câmera, se não encontrar, usa do DVR
        ip = cam.get("ip") or cam.get("_dvr_ip")
        porta = cam.get("porta") or cam.get("_dvr_porta", 80)
        canal = cam.get("canal") or cam.get("channel") or "101"
        # Credenciais sempre do DVR (fallback para camera se não injetado)
        usuario = cam.get("_dvr_usuario") or cam.get("usuario") or "admin"
        senha = cam.get("_dvr_senha") or cam.get("senha") or "admin"

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
        
        # Retry com backoff exponencial
        online = False
        ultima_exception = None
        
        for tentativa in range(Config.TENTATIVAS_RETRY + 1):
            try:
                # Usa pool de conexões se disponível, senão cria nova requisição
                if self.http_session:
                    resp = self.http_session.get(
                        url, 
                        auth=HTTPDigestAuth(usuario, senha), 
                        timeout=Config.TIMEOUT_VERIFICACAO
                    )
                else:
                    import requests
                    resp = requests.get(
                        url, 
                        auth=HTTPDigestAuth(usuario, senha), 
                        timeout=Config.TIMEOUT_VERIFICACAO
                    )
                
                online = resp.status_code == 200 and resp.headers.get(
                    "Content-Type", ""
                ).startswith("image")
                
                if online:
                    break  # Sucesso, sai do loop de retry
                    
            except Exception as e:
                ultima_exception = e
                if tentativa < Config.TENTATIVAS_RETRY:
                    # Backoff exponencial: 1s, 2s, 4s...
                    backoff = Config.RETRY_BACKOFF * (2 ** tentativa)
                    time.sleep(backoff)
                continue
        
        # Log apenas se falhou após todas as tentativas
        if not online and ultima_exception:
            print(f"[ERRO] {nome}: {ultima_exception}")
            
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

    def verificar_camera_intelbras(
        self,
        cam: Dict[str, Any],
        nome_condominio: str,
        config_global: Optional[Dict[str, Any]] = None,
    ) -> tuple[str, str]:
        """
        Verifica uma câmera Intelbras usando snapshot CGI (HTTPDigestAuth)
        
        Protocolo CGI (Dahua): /cgi-bin/snapshot.cgi?channel={n}
        Canais em formato numérico simples: 1, 2, 3, 4...
        
        Validação em cascata:
        1. Conectividade TCP (porta configurada)
        2. Autenticação Digest (Status 200)
        3. Content-Type: image/jpeg
        4. Content-Length > MIN_SIZE (detecta imagens estáticas "Sem Sinal")
        """
        import requests
        from requests.auth import HTTPDigestAuth

        nome = cam.get("name", "CAMERA")
        ip = cam.get("ip") or cam.get("_dvr_ip")
        porta = cam.get("porta") or cam.get("_dvr_porta", 80)
        canal = cam.get("canal") or cam.get("channel") or "1"
        # Credenciais sempre do DVR (fallback para camera se não injetado)
        usuario = cam.get("_dvr_usuario") or cam.get("usuario") or "admin"
        senha = cam.get("_dvr_senha") or cam.get("senha") or "admin"

        if not ip or not usuario or not senha:
            print(f"[⚠️] {nome} não possui dados de conexão suficientes. IP: {ip}")
            return nome, "NO_CONFIG"

        # Converte canal para formato Intelbras se necessário (101 -> 1)
        canal = ProtocolUtils.convert_channel_to_intelbras(canal)

        # Verifica cache primeiro
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

        # Verificação real via snapshot CGI Intelbras
        url = f"http://{ip}:{porta}/cgi-bin/snapshot.cgi?channel={canal}"
        
        # Retry com backoff exponencial
        online = False
        ultima_exception = None
        content_length = 0
        
        for tentativa in range(Config.TENTATIVAS_RETRY + 1):
            try:
                # Usa pool de conexões se disponível
                if self.http_session:
                    resp = self.http_session.get(
                        url, 
                        auth=HTTPDigestAuth(usuario, senha), 
                        timeout=Config.TIMEOUT_VERIFICACAO
                    )
                else:
                    import requests
                    resp = requests.get(
                        url, 
                        auth=HTTPDigestAuth(usuario, senha), 
                        timeout=Config.TIMEOUT_VERIFICACAO
                    )
                
                # Validação Intelbras:
                # 1. Status 200 (autenticação OK)
                # 2. Content-Type deve ser image/jpeg
                # 3. Content-Length deve ser maior que MIN_SIZE (evita imagens "Sem Sinal")
                content_type_ok = resp.headers.get("Content-Type", "").startswith("image")
                content_length = int(resp.headers.get("Content-Length", 0))
                size_ok = content_length >= Config.INTELBRAS_MIN_IMAGE_SIZE
                
                online = resp.status_code == 200 and content_type_ok and size_ok
                
                if online:
                    break  # Sucesso, sai do loop de retry
                elif resp.status_code == 200 and content_type_ok and not size_ok:
                    # Imagem muito pequena - provavelmente "Sem Sinal"
                    print(f"[⚠️] {nome}: Imagem muito pequena ({content_length} bytes) - possível 'Sem Sinal'")
                    break  # Não continua tentando
                    
            except Exception as e:
                ultima_exception = e
                if tentativa < Config.TENTATIVAS_RETRY:
                    # Backoff exponencial: 1s, 2s, 4s...
                    backoff = Config.RETRY_BACKOFF * (2 ** tentativa)
                    time.sleep(backoff)
                continue
        
        # Log apenas se falhou após todas as tentativas
        if not online and ultima_exception:
            print(f"[ERRO] {nome} [Intelbras]: {ultima_exception}")
        elif not online and content_length > 0:
            print(f"[INFO] {nome} [Intelbras]: Offline ou sem sinal (image size: {content_length} bytes)")
            
        status_str = "ON" if online else "OFF"
        print(f"📷 {nome} está {status_str} [Intelbras CGI]")

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
