"""
Configurações do backend FastAPI – lidas de variáveis de ambiente (.env)
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # ── Banco de Dados ──────────────────────────────────────────────
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "monitoramento_cameras"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )

    # ── Verificação de câmeras ──────────────────────────────────────
    TIMEOUT_VERIFICACAO: int = 12          # segundos
    TENTATIVAS_RETRY: int = 2
    RETRY_BACKOFF: float = 1.0             # segundos
    INTERVALO_VERIFICACAO: int = 600       # segundos entre ciclos

    # Workers
    MAX_WORKERS_CAMERAS: int = 10
    MAX_WORKERS_CONDOMINIOS: int = 8
    DELAY_ENTRE_CAMERAS: float = 0.1

    # Pool de conexões HTTP
    USE_CONNECTION_POOL: bool = True
    CONNECTION_POOL_SIZE: int = 50
    CONNECTION_POOL_MAXSIZE: int = 50

    # Cache
    CACHE_DURATION: int = 30               # ON = 30s
    CACHE_DURATION_OFFLINE: int = 120      # OFF = 120s

    # Protocolo padrão
    DEFAULT_PROTOCOL: str = "hikvision"

    # Intelbras
    INTELBRAS_MIN_IMAGE_SIZE: int = 1024

    # ── API Moni (alertas) ──────────────────────────────────────────
    MONI_API_URL: str = "http://192.168.2.50:55554/ExecutarComando"
    MONI_API_USER: str = "moni"
    MONI_API_PASS: str = "senha"

    # ── Defaults para campos de alerta (antes no JSON) ──────────────
    DEFAULT_PARTICAO: str = "01"
    DEFAULT_OCORRENCIA: int = 960
    DEFAULT_CODIGOMAQUINA: int = 897
    DEFAULT_CODIGOCONJUNTODEOCORRENCIAS: int = 7

    # ── CORS ────────────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = ["*"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
