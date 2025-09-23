# main.py

from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import Base, engine 
import models 
from routers import auth, alunos, billing # 1. Importe o novo roteador

# Cria as tabelas no schema 'public' se não existirem
models.Base.metadata.create_all(
    bind=engine, 
    tables=[models.User.__table__, models.Tenant.__table__], 
    checkfirst=True
)

app = FastAPI(title="Sistema de Gestão de Academias - Multi-Tenant")

origins = [
    "http://localhost",
    "http://localhost:8080",
    "null", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# Inclui os roteadores na aplicação principal
app.include_router(auth.router)
app.include_router(alunos.router)
app.include_router(billing.router) # 2. Inclua o roteador de pagamentos

# Monte o diretório estático por último
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

