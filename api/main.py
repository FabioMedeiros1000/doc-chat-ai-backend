from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import router

from config.env_settings import get_settings

app = FastAPI(
    title="Law Agents API",
    description="API para obter respostas via agentes de IA em documentos importados",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    settings = get_settings()

    uvicorn.run(
        app,                
        host="0.0.0.0",
        port=settings.API_PORT
    )
