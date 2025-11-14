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
    TIMEOUT_VERIFICACAO = 8  # segundos
    TENTATIVAS_VERIFICACAO = 3
    INTERVALO_VERIFICACAO = 600  # segundos

    # Configurações de workers
    MAX_WORKERS_CAMERAS = 2  # Ajuste conforme necessário
    MAX_WORKERS_CONDOMINIOS = 3

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
