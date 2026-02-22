from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import chat, tables, pages
from app.utils.db import init_db
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize DB
init_db()

# Include routers
app.include_router(pages.router)
app.include_router(chat.router)
app.include_router(tables.router)
