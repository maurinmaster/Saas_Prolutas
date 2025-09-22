# database.py

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from fastapi import Header

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
# Lembre-se de ajustar com suas credenciais
DATABASE_URL = "postgresql://postgres:1025@localhost/gym_manager_db"
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- FUNÇÃO DE DEPENDÊNCIA PARA OBTER A SESSÃO DO BANCO ---
def get_db(x_tenant_id: str | None = Header(default=None)):
    """
    Injeta a sessão do banco e configura o search_path do PostgreSQL
    com base no cabeçalho x-tenant-id.
    """
    db = SessionLocal()
    search_path = "public"
    if x_tenant_id:
        safe_schema_name = f'"{x_tenant_id}"'
        search_path = f'{safe_schema_name}, {search_path}'
        
    try:
        db.execute(text(f'SET search_path TO {search_path}'))
        yield db
    finally:
        db.close()