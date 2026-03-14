import os
import mysql.connector

# Pega as mesmas variáveis que você já definiu
DB_HOST = os.getenv('happydb')
DB_PASS = os.getenv('happydb_senha', 'tijolo22')
DB_USER = os.getenv('happydb_user', 'root')
DB_NAME = "happydb"

def delete_everything():
    print(f"--- ATENÇÃO: Deletando tudo em {DB_HOST} ---")
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS
        )
        cursor = conn.cursor()

        # Dropa o banco inteiro. É o jeito mais garantido de limpar "poha nenhuma".
        cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
        
        conn.commit()
        print(f">>> O banco '{DB_NAME}' foi EXCLUÍDO com sucesso.")
        print(">>> Agora, ao rodar o app.py, ele terá que recriar tudo.")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"ERRO AO DELETAR: {e}")

if __name__ == '__main__':
    delete_everything()