import os
import mysql.connector
import time
import redis
import json
from datetime import datetime
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

# --- Configurações (DB e Cache) ---
DB_HOST = os.getenv('happydb')
DB_PASS = os.getenv('happydb_senha', 'tijolo22')
DB_USER = os.getenv('happydb_user', 'root')
DB_NAME = "happydb"

CACHE_HOST = os.getenv('cache_host', 'localhost')
CACHE_PORT = os.getenv('cache_port', 6379)

GIF_URL = "https://i.makeagif.com/media/12-31-2023/iFU7lY.gif"

# Inicializa Redis
cache = redis.Redis(host=CACHE_HOST, port=CACHE_PORT, decode_responses=True)

def init_db():
    """Migração inicial do MariaDB"""
    print(f"--- Migração DB em: {DB_HOST} ---")
    try:
        conn = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASS)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cursor.execute(f"USE {DB_NAME}")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tbl_happy (
                id INT AUTO_INCREMENT PRIMARY KEY,
                mensagem VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print(">>> DB MariaDB Pronto.")
    except Exception as e:
        print(f"Erro DB: {e}")

@app.route('/happy')
def happy():
    # 1. Incrementar métrica no Cache (Métrica de total de requests)
    total_requests = cache.incr('metrics:total_requests')
    
    # 2. Pub/Sub: Publica um evento de que alguém ficou feliz
    event_data = {
        "event": "user_is_happy",
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "request_id": total_requests
    }
    cache.publish('happy_channel', json.dumps(event_data))
    
    # 3. Armazenar histórico no Cache (para a página de status)
    cache.lpush('happy_history', json.dumps(event_data))
    cache.ltrim('happy_history', 0, 9) # Mantém apenas as últimas 10

    return render_template_string(f'''
    <html>
        <body style="background:#000; color:#0f0; text-align:center; padding-top:50px; font-family:sans-serif;">
            <h1>HAPPY HAPPY HAPPY!</h1>
            <img src="{GIF_URL}" style="border: 10px solid #0f0; border-radius:20px; width:400px;">
            <p>Request ID: {total_requests}</p>
            <a href="/status" style="color:#fff;">Ver Status do Sistema</a>
        </body>
    </html>
    ''')

@app.route('/status')
def status():
    # Coleta dados do Cache
    total = cache.get('metrics:total_requests') or 0
    history_raw = cache.lrange('happy_history', 0, -1)
    history = [json.loads(h) for h in history_raw]
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Happy Status</title>
        <style>
            body { background: #121212; color: #e0e0e0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 20px; }
            .card { background: #1e1e1e; border-radius: 8px; padding: 20px; margin-bottom: 20px; border-left: 5px solid #00ff00; }
            .metric { font-size: 2em; color: #00ff00; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { text-align: left; padding: 12px; border-bottom: 1px solid #333; }
            th { color: #888; }
        </style>
    </head>
    <body>
        <h1>Dashboard de Status do Gato</h1>
        
        <div class="card">
            <h3>Métricas de Aplicação</h3>
            <div class="metric">{{ total }}</div>
            <p>Total de Requests no /happy</p>
        </div>

        <div class="card">
            <h3>Últimos Eventos Pub/Sub (Channel: happy_channel)</h3>
            <table>
                <tr><th>Hora</th><th>Evento</th><th>ID</th></tr>
                {% for item in history %}
                <tr>
                    <td>{{ item.timestamp }}</td>
                    <td>{{ item.event }}</td>
                    <td>{{ item.request_id }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        
        <div class="card" style="border-left-color: #007bff;">
            <h3>Metadados do Cache</h3>
            <p>Host: {{ cache_host }} | Porta: {{ cache_port }}</p>
        </div>

        <p><a href="/happy" style="color: #00ff00;"><- Voltar para a felicidade</a></p>
    </body>
    </html>
    ''', total=total, history=history, cache_host=CACHE_HOST, cache_port=CACHE_PORT)

if __name__ == '__main__':
    init_db()
    # Garante que o contador de métricas existe se estiver zerado
    if not cache.exists('metrics:total_requests'):
        cache.set('metrics:total_requests', 0)
    
    app.run(host='0.0.0.0', port=5000, debug=True)