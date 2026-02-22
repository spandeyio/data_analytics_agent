from langchain.tools import tool
import psycopg2
from app.utils.config import get_settings
import json
import uuid

settings = get_settings()

@tool
def execute_sql(query: str) -> str:
    """
    Executes a SQL query on the database using psycopg2.
    The query should be a valid PostgreSQL query.
    Always limit the results to 15 rows if not specified.
    """
    conn = None
    try:
        conn = psycopg2.connect(
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            dbname=settings.DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute(query)
        
        # Fetch results if any
        if cursor.description:
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()
            # Convert to list of dicts
            data = []
            for row in results:
                row_dict = {}
                for i, col in enumerate(columns):
                    val = row[i]
                    # Handle date objects for JSON serialization
                    if hasattr(val, 'isoformat'):
                        val = val.isoformat()
                    row_dict[col] = val
                data.append(row_dict)
            
            return json.dumps(data)
        else:
            conn.commit()
            return "Query executed successfully."
            
    except Exception as e:
        return f"Error executing SQL: {str(e)}"
    finally:
        if conn:
            conn.close()

def get_table_info() -> str:
    """
    Returns information about all tables in the database (excluding system tables and chat_history),
    including their schema and 5 random records for each table.
    Use this tool to understand the database structure and content before generating SQL queries.
    """
    conn = None
    try:
        conn = psycopg2.connect(
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            dbname=settings.DB_NAME
        )
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name != 'chat_history'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        info = []
        
        for table in tables:
            table_info = {"table_name": table}
            
            # Get columns
            cursor.execute(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{table}'
            """)
            columns = [{"name": row[0], "type": row[1]} for row in cursor.fetchall()]
            table_info["columns"] = columns
            
            # Get 5 random records
            try:
                cursor.execute(f"SELECT * FROM {table} ORDER BY RANDOM() LIMIT 5")
                if cursor.description:
                    col_names = [desc[0] for desc in cursor.description]
                    records = []
                    for row in cursor.fetchall():
                        record = {}
                        for i, val in enumerate(row):
                            if hasattr(val, 'isoformat'):
                                val = val.isoformat()
                            record[col_names[i]] = val
                        records.append(record)
                    table_info["sample_data"] = records
            except Exception as e:
                table_info["sample_error"] = str(e)
                
            info.append(table_info)
            
        return json.dumps(info, indent=2)
            
    except Exception as e:
        return f"Error getting table info: {str(e)}"
    finally:
        if conn:
            conn.close()

# Visualizations are now generated directly by the LLM as HTML/JS
