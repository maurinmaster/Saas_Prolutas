# schemas.py

from pydantic import BaseModel, constr, EmailStr
from typing import Optional, List
from datetime import date
from database import Base

# --- Schemas de Autenticação e Usuário ---
class UserBase(BaseModel):
    email: EmailStr

class UserSchema(UserBase):
    id: int
    is_saas_admin: bool
    class Config:
        orm_mode = True

class TenantRegistration(BaseModel):
    tenant_name: constr(min_length=3, max_length=50)
    owner_email: EmailStr
    owner_password: str

class TokenData(BaseModel):
    email: str | None = None

# --- Schemas para Alunos (ATUALIZADOS) ---
class AlunoBase(BaseModel):
    nome_completo: str
    data_nascimento: date
    whatsapp: str
    dia_vencimento: int
    foto_url: Optional[str] = None
    cpf: Optional[str] = None
    nome_responsavel: Optional[str] = None
    contato_responsavel: Optional[str] = None
    receber_notificacoes: bool = True
    modalidade: Optional[str] = None
    faixa: Optional[str] = None

class AlunoCreate(AlunoBase):
    pass

class AlunoUpdate(BaseModel):
    nome_completo: Optional[str] = None
    data_nascimento: Optional[date] = None
    whatsapp: Optional[str] = None
    dia_vencimento: Optional[int] = None
    foto_url: Optional[str] = None
    cpf: Optional[str] = None
    nome_responsavel: Optional[str] = None
    contato_responsavel: Optional[str] = None
    receber_notificacoes: Optional[bool] = None
    modalidade: Optional[str] = None
    faixa: Optional[str] = None

class AlunoSchema(AlunoBase):
    id: int
    class Config:
        orm_mode = True
