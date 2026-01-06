"""
Configurações globais do sistema de monitoramento de câmeras
"""

import os


# Configurações da aplicação Flask
class Config:
    SECRET_KEY = "chave-super-secreta"  # Troque por algo seguro em produção
    PERMANENT_SESSION_LIFETIME = 30  # minutos

    # Configurações de autenticação
    USUARIO = "admin"
    SENHA = "1234"

    # Configurações do servidor
    HOST = "0.0.0.0"
    PORT = 8080
    DEBUG = False

    # Configurações de verificação de câmeras
    TIMEOUT_VERIFICACAO = 12  # segundos
    TENTATIVAS_VERIFICACAO = 3
    INTERVALO_VERIFICACAO = 600  # segundos

    # Configurações de workers para escalabilidade
    MAX_WORKERS_CAMERAS = 10  # Processa até 10 câmeras simultaneamente
    MAX_WORKERS_CONDOMINIOS = 8  # Processa até 8 condomínios simultaneamente
    DELAY_ENTRE_CAMERAS = 0.1  # segundos - delay entre submissões de câmeras
    
    # Configurações de retry e resiliência
    TENTATIVAS_RETRY = 2  # Tentativas adicionais em caso de falha
    RETRY_BACKOFF = 1  # segundos - delay entre retries
    
    # Configurações de pool de conexões HTTP
    USE_CONNECTION_POOL = True  # Habilita pool de conexões reutilizáveis
    CONNECTION_POOL_SIZE = 50  # Máximo de conexões no pool
    CONNECTION_POOL_MAXSIZE = 50  # Conexões por host

    # Configurações de cache
    CACHE_DURATION = 30  # segundos
    CACHE_DURATION_OFFLINE = 120  # segundos

    # Configurações de API
    API_URL = "http://192.168.2.50:5554/ExecutarComando"
    # "http://192.168.2.50:5554/ExecutarComando"
    API_USERNAME = "moni"
    # API_PASSWORD = "moni"
    API_PASSWORD = "senha"

    # Caminhos dos arquivos (BASE_DIR = raiz do projeto)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    APP_DIR = os.path.join(BASE_DIR, "app")
    CONDOMINIOS_DIR = os.path.join(APP_DIR, "data", "condominios")
    WEB_DIR = os.path.join(BASE_DIR, "web")
    TEMPLATES_DIR = os.path.join(WEB_DIR, "templates")
    STATIC_DIR = os.path.join(WEB_DIR, "static")
