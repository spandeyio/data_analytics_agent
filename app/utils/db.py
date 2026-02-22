import psycopg2
from app.utils.config import get_settings

settings = get_settings()

def get_db_connection():
    return psycopg2.connect(
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        dbname=settings.DB_NAME
    )

def init_db():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id SERIAL PRIMARY KEY,
                role TEXT NOT NULL,
                content TEXT NOT NULL
            )
        ''')
        conn.commit()
        cur.close()
    except Exception as e:
        print(f"Error initializing chat_history table: {e}")
    finally:
        if conn:
            conn.close()
