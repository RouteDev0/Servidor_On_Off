"""
FastAPI – Serviço de Monitoramento de Câmeras (backend)

Substitui o antigo Flask app.  Inicia o loop de verificação em background
e expõe endpoints REST para o frontend React.
"""

import time
import threading
import concurrent.futures
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.database import SessionLocal
from backend.services.db_data_loader import carregar_dados_do_banco
from backend.services.verification_service import VerificationService
from backend.services.condominio_service import CondominioService
from backend.routers import empresas, clientes, status, reports

settings = get_settings()

# ── Singletons dos serviços ─────────────────────────────────────────
verification_service = VerificationService()
condominio_service = CondominioService(verification_service)


# ── Loop de verificação (background thread) ─────────────────────────
def loop_verificacao():
    """Loop principal que verifica todas as câmeras periodicamente."""
    while True:
        db = SessionLocal()
        try:
            print("[INFO] 🔄 Carregando dados do banco de dados...")
            dados_clientes = carregar_dados_do_banco(db)

            if not dados_clientes:
                print("[AVISO] Nenhum cliente/câmera encontrado no banco.")
                time.sleep(settings.INTERVALO_VERIFICACAO)
                continue

            print(f"[INFO] Iniciando verificação de {len(dados_clientes)} clientes...")
            tempo_inicio = time.time()

            # Processa cada cliente (em paralelo – limitado por MAX_WORKERS_CONDOMINIOS)
            max_workers = (
                min(len(dados_clientes), settings.MAX_WORKERS_CONDOMINIOS) or 1
            )
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=max_workers
            ) as executor:
                futures = [
                    executor.submit(
                        condominio_service.processar_condominio,
                        nome_cond,
                        data_cond,
                    )
                    for nome_cond, data_cond in dados_clientes.items()
                ]
                for future in concurrent.futures.as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        print(f"[ERRO] Erro ao processar condomínio: {e}")

            # Flush eventos pendentes para o banco
            verification_service.flush_eventos(db)

            tempo_total = time.time() - tempo_inicio
            print(f"[INFO] ✅ Verificação concluída em {tempo_total:.2f} segundos")

        except Exception as e:
            print(f"[ERRO CRÍTICO] Erro no loop de verificação: {e}")
        finally:
            db.close()

        time.sleep(settings.INTERVALO_VERIFICACAO)


# ── Lifespan ────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicia o loop de verificação quando o servidor sobe."""
    # Injeta verification_service no router de status
    status.set_verification_service(verification_service)

    thread = threading.Thread(target=loop_verificacao, daemon=True)
    thread.start()
    print("[INFO] 🚀 Loop de verificação iniciado em background")
    yield
    print("[INFO] 🛑 Servidor desligando...")


# ── App FastAPI ─────────────────────────────────────────────────────
app = FastAPI(
    title="Monitoramento de Câmeras API",
    description="API para monitoramento de câmeras e alarmes",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    # also allow any origin via regex (covers dynamic ports/IPs)
    allow_origin_regex=r".*",
    # disable credentials so wildcard origins can be used and headers are sent
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(empresas.router)
app.include_router(clientes.router)
app.include_router(status.router)
app.include_router(reports.router)


@app.get("/")
def root():
    return {
        "service": "Monitoramento de Câmeras",
        "version": "2.0.0",
        "status": "running",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
