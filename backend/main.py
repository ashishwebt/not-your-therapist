"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.repository.database import init_db
from app.routes import router

init_db()

app = FastAPI(
    title="Not Your Therapist API",
    description="Not a real Therapist chatbot using Ollama, and Langchain",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=
    ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)