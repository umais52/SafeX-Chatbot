from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import chat
from app.db.session import engine
from app.db.models import Base

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Warm up the Ollama model so it's pre-loaded in RAM for fast first response
    import httpx
    import asyncio
    async def warmup_ollama():
        try:
            print("INFO:     Warming up Ollama model (this may take 1-2 minutes on first run)...")
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    f"{settings.OLLAMA_BASE_URL}/api/generate",
                    json={"model": settings.LLM_MODEL, "prompt": "hi", "stream": False, "options": {"num_predict": 1}},
                    timeout=300.0
                )
                if r.status_code == 200:
                    print("INFO:     Ollama model loaded and ready!")
                else:
                    print(f"WARNING:  Ollama warmup returned status {r.status_code}")
        except Exception as e:
            print(f"WARNING:  Ollama warmup failed: {e}. First request may be slow.")
    
    asyncio.create_task(warmup_ollama())


# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, change to actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Welcome to SafeX Chatbot API"}

# We will include routers here later
app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["chat"])
