from fastapi import FastAPI
from .routers import router

from config.env_settings import get_settings

app = FastAPI(
    title="Law Agents API",
    description="API para obter respostas via agentes de IA sobre assuntos legais tributários",
    version="0.1.0",
)

app.include_router(router, prefix="/law-agents", tags=["Law Agents"])

if __name__ == "__main__":
    import uvicorn

    settings = get_settings()

    uvicorn.run(
        app,                
        host="0.0.0.0",
        port=settings.API_PORT
    )
