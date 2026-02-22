from langchain.agents import create_agent
from app.utils.llm import LLM
from app.analytics_agent.tools import execute_sql
from app.analytics_agent.prompt import SYSTEM_PROMPT_TEMPLATE

def get_agent(table_info: str):
    llm_instance = LLM()
    llm = llm_instance.get_llm()
    
    tools = [execute_sql]
    
    formatted_prompt = SYSTEM_PROMPT_TEMPLATE.format(table_info=table_info)
    
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=formatted_prompt
    )
    
    return agent
