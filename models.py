# models.py

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timedelta

# --- Tabelas no Schema 'public' ---
class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'public'}
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_saas_admin = Column(Boolean, default=False)
    tenant_id = Column(Integer, ForeignKey('public.tenants.id'), nullable=True)
    
    tenant = relationship("Tenant", back_populates="owner")

class Tenant(Base):
    __tablename__ = 'tenants'
    __table_args__ = {'schema': 'public'}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    schema_name = Column(String, unique=True, nullable=False)
    status = Column(String, default='trial')
    created_at = Column(DateTime, default=datetime.utcnow)
    trial_ends_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=30))
    
    owner = relationship("User", back_populates="tenant")

# --- Tabelas no Schema do Tenant ---
class Aluno(Base):
    __tablename__ = 'alunos'
    id = Column(Integer, primary_key=True, index=True)
    
    # --- CAMPOS ATUALIZADOS ---
    foto_url = Column(String, nullable=True)
    nome_completo = Column(String, index=True, nullable=False)
    data_nascimento = Column(Date, nullable=False)
    cpf = Column(String, unique=True, index=True, nullable=True)
    whatsapp = Column(String, nullable=False)
    nome_responsavel = Column(String, nullable=True)
    contato_responsavel = Column(String, nullable=True)
    dia_vencimento = Column(Integer, nullable=False)
    receber_notificacoes = Column(Boolean, default=True)
    
    # Campos antigos que podem ser mantidos para outros usos
    modalidade = Column(String, nullable=True)
    faixa = Column(String, nullable=True)
