import pymysql
import os
import time

def get_db_connection():
    # Attempt to load env variables from .env if not already loaded
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    # Basic env parsing
                    if '=' in line:
                        key, val = line.strip().split('=', 1)
                        if key not in os.environ:
                            os.environ[key] = val.strip('"\'')
                    
    host = os.environ.get('DB_HOST', '192.185.209.100')
    user = os.environ.get('DB_USER', 'juanca22_admin')
    password = os.environ.get('DB_PASSWORD', 'Route@0450')
    database = os.environ.get('DB_NAME', 'juanca22_banco_de_dados_route')
    port = int(os.environ.get('DB_PORT', 3306))

    return pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port,
        cursorclass=pymysql.cursors.DictCursor
    )

def get_alert_devices():
    """
    Fetches alert devices and cameras from the database and returns them
    grouped by client, ready for the verification service.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Query the required tables. 'servicos LIKE '%on_off
            # %'' filters devices for alerts.
            sql = """
            SELECT 
                d.id AS dispositivo_id, d.ip AS dvr_ip, d.porta AS dvr_porta, 
                d.usuario AS dvr_usuario, d.senha AS dvr_senha, 
                d.tipo_dispositivo AS dvr_tipo, d.marca AS dvr_marca,
                c.uuid_camera, c.canal_fisico, c.numero_setor, c.complemento,
                cli.nome AS cliente_nome, cli.empresa_id, cli.codigo_moni
            FROM dispositivos d
            JOIN pontos_monitoramento c ON d.id = c.dispositivo_id
            JOIN clientes cli ON d.codigo_moni = cli.codigo_moni
            WHERE d.servicos LIKE '%on_off%'
            """
            cursor.execute(sql)
            results = cursor.fetchall()
            
            # Format results into a dictionary grouped by client name
            clientes = {}
            for row in results:
                cliente = row['cliente_nome']
                if not cliente:
                    cliente = f"Cliente_{row['codigo_moni']}"
                    
                if cliente not in clientes:
                    clientes[cliente] = {
                        "metadata": {
                            "empresa": row['empresa_id'] or "",
                            "codigo_moni": row['codigo_moni'] or "",
                            "origem": "banco_de_dados"
                        },
                        "cameras": []
                    }
                
                # Using the rule: append 01 after the channel
                base_channel = row['canal_fisico']
                if base_channel is None:
                    base_channel = row['numero_setor']
                
                if base_channel is None:
                    continue # Skip if no channel information is available
                    
                canal_convertido = f"{base_channel}01"
                
                # Protocol logic
                marca = str(row['dvr_marca']).lower() if row['dvr_marca'] else ""
                protocol = "intelbras" if "intelbras" in marca else "hikvision"
                
                # Determine camera name
                cam_name = row['complemento']
                if not cam_name:
                    cam_name = f"Camera {base_channel}"

                # Append the structured camera data
                cam_data = {
                    "name": cam_name,
                    "canal": canal_convertido,
                    "channel": canal_convertido, # verification_service checks both
                    "_dvr_ip": row['dvr_ip'],
                    "_dvr_porta": row['dvr_porta'] or 80,
                    "_dvr_usuario": row['dvr_usuario'] or "admin",
                    "_dvr_senha": row['dvr_senha'] or "admin",
                    "_dvr_protocol": protocol,
                    "uuid": row['uuid_camera']
                }
                clientes[cliente]["cameras"].append(cam_data)
                
            return list(clientes.items()) # Returns list of tuples (cliente_nome, dict_data)
    except Exception as e:
        print(f"[ERRO DB] Exception while fetching alert devices: {e}")
        return []
    finally:
        connection.close()
