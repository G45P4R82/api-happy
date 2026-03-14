import os
import mysql.connector
from flask import Flask, render_template_string

app = Flask(__name__)

# Variáveis vindas do seu ambiente (K8s/Docker)
DB_HOST = os.getenv('happydb')
DB_PASS = os.getenv('happydb_senha')
DB_USER = os.getenv('happydb_user', 'root')  # Padrão root se não definido
DB_NAME = "happydb"
GIF_URL = "https://i.makeagif.com/media/12-31-2023/iFU7lY.gif"

def init_db():
    try:
        # 1. Conecta sem especificar o banco (para poder criá-lo)
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS
        )
        cursor = conn.cursor()

        # 2. Cria o banco de dados se não existir
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cursor.execute(f"USE {DB_NAME}")

        # 3. Cria a tabela se não existir
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tbl_happy (
                id INT AUTO_INCREMENT PRIMARY KEY,
                status VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 4. Checa se a tabela está vazia e insere o dado inicial
        cursor.execute("SELECT COUNT(*) FROM tbl_happy")
        count = cursor.fetchone()[0]
        
        if count == 0:
            cursor.execute("INSERT INTO tbl_happy (status) VALUES ('happy_initialized')")
            conn.commit()
            print(">>> Banco e tabela inicializados com sucesso!")
        else:
            print(">>> Tabela já contém dados, pulando insert inicial.")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f">>> Erro na migração: {e}")

@app.route('/happy')
def happy():
    html_content = f'''
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Happy Happy Happy!</title>
        <style>
            body {{ display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100vh; margin: 0; background-color: #1a1a1a; color: #00ff00; font-family: 'Courier New', Courier, monospace; }}
            img {{ max-width: 80%; border: 5px solid #00ff00; border-radius: 15px; }}
            .status {{ margin-top: 15px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <img src="{GIF_URL}" alt="Happy Cat">
        <div class="status">DB STATUS: CONNECTED TO {DB_NAME}</div>
    </body>
    </html>
    '''
    return render_template_string(html_content)

if __name__ == '__main__':
    # Roda a migração antes de iniciar o app
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
