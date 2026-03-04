from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from datetime import timedelta
import os
import time
import threading
import concurrent.futures

from app.config import Config
from app.services.verification_service import VerificationService

app = Flask(
    __name__, template_folder=Config.TEMPLATES_DIR, static_folder=Config.STATIC_DIR
)
app.secret_key = Config.SECRET_KEY
app.permanent_session_lifetime = timedelta(minutes=Config.PERMANENT_SESSION_LIFETIME)

USUARIO = Config.USUARIO
SENHA = Config.SENHA
verification_service = VerificationService()


def login_obrigatorio(f):
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")
        if usuario == USUARIO and senha == SENHA:
            session.permanent = True
            session["usuario"] = usuario
            return redirect(url_for("index"))
        else:
            return render_template("login.html", erro="Usuário ou senha inválidos")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("login"))


def processar_condominio_db(cliente_nome, data):
    try:
        config_global = data.get("metadata", {})
        cameras = data.get("cameras", [])
        verification_service.verificar_cameras(cameras, cliente_nome, config_global)
        return True
    except Exception as e:
        print(f"[ERRO] Falha ao processar {cliente_nome}: {e}")
        return False


def loop_verificacao():
    from app.core.database import get_alert_devices
    while True:
        try:
            clientes_data = get_alert_devices()
            if not clientes_data:
                print("[AVISO] Nenhum dispositivo para alerta encontrado no banco de dados.")
                time.sleep(Config.INTERVALO_VERIFICACAO)
                continue

            print(f"[INFO] Iniciando verificação de {len(clientes_data)} condomínios (DB)...")
            tempo_inicio = time.time()

            max_workers = (
                min(len(clientes_data), getattr(Config, "MAX_WORKERS_CONDOMINIOS", 3)) or 1
            )
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=max_workers
            ) as executor:
                futures = [
                    executor.submit(
                        processar_condominio_db,
                        cliente_nome,
                        data,
                    )
                    for cliente_nome, data in clientes_data
                ]
                for future in concurrent.futures.as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        print(f"[ERRO] Erro ao processar condomínio: {e}")

            tempo_total = time.time() - tempo_inicio
            print(f"[INFO] Verificação concluída em {tempo_total:.2f} segundos")
        except Exception as e:
            print(
                f"[ERRO CRÍTICO] Ocorreu um erro inesperado no loop de verificação DB: {e}"
            )
        time.sleep(Config.INTERVALO_VERIFICACAO)

threading.Thread(target=loop_verificacao, daemon=True).start()


@app.route("/")
@login_obrigatorio
def index():
    return render_template("index.html")


@app.route("/condominio/<condominio>")
@login_obrigatorio
def condominio_page(condominio):
    # Em uma estrutura de banco de dados, você deve consultar o banco para obter os dados do "condominio" (Cliente)
    nome_condominio = condominio  # Simplificação para este caso limpo
    return render_template(
        "condominio.html", nome_condominio=nome_condominio, condominio=condominio
    )


@app.route("/status")
@login_obrigatorio
def status():
    return jsonify(verification_service.get_status_atual())


@app.route("/status/<condominio>")
@login_obrigatorio
def status_condominio(condominio):
    status_atual = verification_service.get_status_atual()
    if condominio in status_atual:
        # Retorna apenas as câmeras para manter compatibilidade
        return jsonify(status_atual[condominio].get("cameras", []))
    else:
        return jsonify({"error": "Condomínio não encontrado"}), 404


if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
