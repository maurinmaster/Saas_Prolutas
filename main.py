# main.py

from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware # 1. Importe o Middleware

# Importa a Base e o engine do nosso módulo de banco de dados
from database import Base, engine 
# Importa todos os modelos para que o SQLAlchemy possa criar as tabelas
import models 
# Importa os roteadores que criamos
from routers import auth, alunos 

# Cria as tabelas no schema 'public' se não existirem
models.Base.metadata.create_all(
    bind=engine, 
    tables=[models.User.__table__, models.Tenant.__table__], 
    checkfirst=True
)

# Inicializa a aplicação FastAPI
app = FastAPI(title="Sistema de Gestão de Academias - Multi-Tenant")

# --- 2. Adicione a configuração de CORS ---
# Lista de origens que podem fazer requisições para a API
origins = [
    "http://localhost",
    "http://localhost:8080",
    "null", # Importante para permitir requisições de file:// (arquivos locais)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"], # Permite todos os cabeçalhos
)
# --- Fim da configuração de CORS ---


# Inclui os roteadores na aplicação principal
app.include_router(auth.router)
app.include_router(alunos.router)


# Ponto de entrada para rodar a aplicação
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

