"""
Módulo responsável pela validação de câmeras
"""
import subprocess
import socket
from urllib.parse import urlparse
from typing import Dict, Any, Optional


class CameraValidator:
    """Classe responsável por validar o status das câmeras"""
    
    @staticmethod
    def verificar_stream_video_avancado(rtsp_url: str, tentativas: int = 3, timeout: int = 8) -> bool:
        """
        Verificação avançada que valida se o stream realmente contém vídeo válido.
        """
        # Primeira verificação: conectividade básica
        if not CameraValidator._verificar_conectividade_basica(rtsp_url, timeout):
            return False
        
        # Segunda verificação: ffprobe com validação de conteúdo
        return CameraValidator._verificar_com_ffprobe_avancado(rtsp_url, tentativas, timeout)
    
    @staticmethod
    def _verificar_conectividade_basica(rtsp_url: str, timeout: int = 5) -> bool:
        """Verifica conectividade básica com a câmera"""
        try:
            parsed = urlparse(rtsp_url)
            host = parsed.hostname
            port = parsed.port or 554  # Porta padrão RTSP
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            
            return result == 0
        except Exception:
            return False
    
    @staticmethod
    def _verificar_com_ffprobe_avancado(rtsp_url: str, tentativas: int = 3, timeout: int = 8) -> bool:
        """Verificação principal com ffprobe usando múltiplas estratégias"""
        
        # Estratégia 1: TCP forçado
        cmd_tcp = [
            "ffprobe",
            "-rtsp_transport", "tcp",
            "-v", "error",
            "-timeout", str(timeout * 1000000),
            "-i", rtsp_url
        ]
        
        # Estratégia 2: Auto (pode usar UDP)
        cmd_auto = [
            "ffprobe",
            "-v", "error",
            "-timeout", str(timeout * 1000000),
            "-i", rtsp_url
        ]
        
        # Estratégia 3: Verificação de metadados específicos
        cmd_metadados = [
            "ffprobe",
            "-rtsp_transport", "tcp",
            "-v", "error",
            "-select_streams", "v:0",  # Apenas stream de vídeo
            "-show_entries", "stream=codec_type",
            "-of", "csv=p=0",
            "-timeout", str(timeout * 1000000),
            "-i", rtsp_url
        ]

        for tentativa in range(tentativas):
            try:
                if tentativa == 0:
                    result = subprocess.run(cmd_tcp, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=timeout)
                elif tentativa == 1:
                    result = subprocess.run(cmd_auto, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=timeout)
                else:
                    result = subprocess.run(cmd_metadados, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=timeout)
                    
                if result.returncode == 0:
                    return True
                    
            except (subprocess.TimeoutExpired, Exception):
                continue
        return False
    
    @staticmethod
    def verificar_portas_alternativas(rtsp_url: str, timeout: int = 5) -> bool:
        """Tenta portas alternativas comuns para câmeras"""
        try:
            parsed = urlparse(rtsp_url)
            host = parsed.hostname
            base_port = parsed.port or 554
            
            # Portas alternativas comuns
            portas_alternativas = [base_port, 8554, 10554, 554, 8080, 80]
            
            for porta in portas_alternativas:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)  # Timeout menor para portas alternativas
                    result = sock.connect_ex((host, porta))
                    sock.close()
                    
                    if result == 0:
                        # Se conectou, tenta ffprobe nesta porta
                        nova_url = rtsp_url.replace(f":{base_port}", f":{porta}")
                        if CameraValidator._verificar_com_ffprobe_avancado(nova_url, tentativas=1, timeout=3):
                            return True
                except Exception:
                    continue
                    
            return False
        except Exception:
            return False 