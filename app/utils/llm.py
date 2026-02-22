from langchain_google_genai import ChatGoogleGenerativeAI
from app.utils.config import get_settings

settings = get_settings()

class LLM:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3-pro-preview",
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0
        )
    
    def get_llm(self):
        return self.llm
