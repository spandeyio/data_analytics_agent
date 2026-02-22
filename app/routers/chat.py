from fastapi import APIRouter
from app.schemas.chat import ChatRequest
from app.utils.db import get_db_connection
from langchain_core.messages import HumanMessage, AIMessage
from app.analytics_agent.analytics_agent import get_agent
from app.analytics_agent.tools import get_table_info

router = APIRouter()

@router.post("/chat")
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
        
        # Get table info
        table_info = get_table_info()
        
        # Invoke agent
        agent = get_agent(table_info=table_info)
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
        return {"response": f"Error processing request: {str(e)}"}
    finally:
        cur.close()
        conn.close()
