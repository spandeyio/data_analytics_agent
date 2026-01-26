from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import get_settings
from app.analytics_agent.tools import execute_sql
from app.analytics_agent.prompt import SYSTEM_PROMPT

settings = get_settings()

def get_agent():
    llm = ChatGoogleGenerativeAI(
        model="gemini-3-pro-preview",
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0
    )
    
    tools = [execute_sql]
    
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT
    )
    
    return agent
