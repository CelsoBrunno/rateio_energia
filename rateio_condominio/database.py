# condominio_black_falcon/database.py
# condominio_black_falcon/database.py
import sqlite3
import os
from datetime import datetime # Importe datetime

DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'condominio.db')
INSTANCE_FOLDER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')

# Função para converter ISO format string para datetime
def adapt_datetime_iso(val):
    """Adapta datetime.datetime para formato ISO string."""
    return val.isoformat()

def convert_timestamp(val):
    """Converte uma string ISO de timestamp de volta para um objeto datetime."""
    return datetime.fromisoformat(val.decode()) # .decode() é importante aqui

# Registra os adaptadores e conversores
sqlite3.register_adapter(datetime, adapt_datetime_iso) # Para salvar datetime no BD
sqlite3.register_converter("timestamp", convert_timestamp) # Para ler timestamp do BD

def get_db_connection():
    # Garante que a pasta instance exista
    os.makedirs(INSTANCE_FOLDER_PATH, exist_ok=True)
    # Adiciona detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES
    conn = sqlite3.connect(DATABASE_PATH, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    conn.row_factory = sqlite3.Row # Permite acessar colunas por nome
    return conn

def init_db(app):
    """Inicializa o banco de dados com o schema."""
    with app.app_context():
        conn = get_db_connection()
        with open('schema.sql', 'r') as f:
            conn.executescript(f.read())
        # Popula dados iniciais das unidades se ainda não existirem
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(id) FROM Unidades")
        if cursor.fetchone()[0] == 0:
            with open('data.sql', 'r') as f:
                conn.executescript(f.read())
        conn.commit()
        conn.close()
    print("Banco de dados inicializado.")

def query_db(query, args=(), one=False):
    conn = get_db_connection()
    cur = conn.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, args)
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id