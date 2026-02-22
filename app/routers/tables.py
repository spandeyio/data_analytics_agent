from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.utils.db import get_db_connection
from app.analytics_agent.tools import get_table_info
import json
import csv
import io

router = APIRouter()

@router.get("/tables")
async def get_tables():
    try:
        info_json = get_table_info()
        info = json.loads(info_json)
        # Simplify for the list view: just table names
        tables = [item["table_name"] for item in info]
        return {"tables": tables}
    except Exception as e:
        return {"error": str(e)}

@router.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...), table_name: str = Form(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        contents = await file.read()
        decoded = contents.decode('utf-8')
        csv_reader = csv.reader(io.StringIO(decoded))
        header = next(csv_reader)
        
        # Infer types (simple approach: check first row)
        first_row = next(csv_reader, None)
        if not first_row:
             raise HTTPException(status_code=400, detail="CSV is empty")

        columns_def = []
        for i, val in enumerate(first_row):
            col_name = header[i].replace(" ", "_").lower()
            # Basic type inference
            try:
                int(val)
                col_type = "INTEGER"
            except ValueError:
                try:
                    float(val)
                    col_type = "FLOAT"
                except ValueError:
                    col_type = "TEXT"
            columns_def.append(f"{col_name} {col_type}")
        
        create_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns_def)});"
        cur.execute(create_query)
        
        # Reset reader to start (including first row)
        csv_reader = csv.reader(io.StringIO(decoded))
        next(csv_reader) # Skip header
        
        insert_query = f"INSERT INTO {table_name} ({', '.join([h.replace(' ', '_').lower() for h in header])}) VALUES ({', '.join(['%s'] * len(header))})"
        
        for row in csv_reader:
             if len(row) == len(header): # Ensure row length matches header
                cur.execute(insert_query, row)
        
        conn.commit()
        return {"message": f"Table '{table_name}' created successfully."}
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")
    finally:
        cur.close()
        conn.close()
