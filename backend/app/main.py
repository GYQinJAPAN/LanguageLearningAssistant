from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import translate

app = FastAPI(title="LLM Chat Translator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(translate.router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to the LLM Translator API. Visit /docs for documentation."
    }
