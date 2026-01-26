from langchain.tools import tool
import psycopg2
from app.config import get_settings
import json

settings = get_settings()

@tool
def execute_sql(query: str) -> str:
    """
    Executes a SQL query on the database using psycopg2.
    Use this tool to get data from the 'sensor_data' table.
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

