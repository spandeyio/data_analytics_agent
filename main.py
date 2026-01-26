from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import psycopg2
from typing import List, Optional
from langchain_core.messages import HumanMessage, AIMessage
from app.analytics_agent.analytics_agent import get_agent
import uvicorn
from dotenv import load_dotenv
from app.config import get_settings

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")
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

# Initialize DB on import/startup
init_db()

class ChatRequest(BaseModel):
    message: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    conn = get_db_connection()
    cur = conn.cursor()
    history = []
    try:
        cur.execute("SELECT role, content FROM chat_history ORDER BY id DESC LIMIT 5")
        rows = cur.fetchall()
        # Chronological order
        for role, content in reversed(rows):
            history.append({"role": role, "content": content})
    except Exception as e:
        print(f"Error fetching history: {e}")
    finally:
        cur.close()
        conn.close()
        
    return templates.TemplateResponse("index.html", {"request": request, "history": history})

@app.post("/chat")
async def chat(request: ChatRequest):
    user_message = request.message
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Get last 10 messages
        cur.execute("SELECT role, content FROM chat_history ORDER BY id DESC LIMIT 10")
        rows = cur.fetchall()
        rows = rows[::-1] # Reverse to chronological order
        
        messages = []
        for role, content in rows:
            if role == "user":
                messages.append(HumanMessage(content=content))
            else:
                messages.append(AIMessage(content=content))
                
        # Add current message
        messages.append(HumanMessage(content=user_message))
        
        # Invoke agent
        agent = get_agent()
        response = agent.invoke({"messages": messages})
        
        last_message = response["messages"][-1]
        bot_response = last_message.content
        
        # Handle case where content is a list
        if isinstance(bot_response, list):
            text_parts = []
            for part in bot_response:
                if isinstance(part, dict) and "text" in part:
                    text_parts.append(part["text"])
                elif isinstance(part, str):
                    text_parts.append(part)
            bot_response = "\n".join(text_parts)
        
        if not isinstance(bot_response, str):
            bot_response = str(bot_response)

        # Store history
        cur.execute("INSERT INTO chat_history (role, content) VALUES (%s, %s)", ("user", user_message))
        cur.execute("INSERT INTO chat_history (role, content) VALUES (%s, %s)", ("ai", bot_response))
        conn.commit()
        
        return {"response": bot_response}
        
    except Exception as e:
        print(f"Error processing chat: {e}")
        conn.rollback()
        return {"response": "Error processing request."}
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
