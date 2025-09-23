# schemas.py

from pydantic import BaseModel, constr, EmailStr, validator
from typing import Optional, List
from datetime import date
from database import Base

# --- Schemas de Autenticação e Usuário ---
class UserBase(BaseModel):
    email: EmailStr

class UserSchema(UserBase):
    id: int
    cpf: str
    is_saas_admin: bool
    class Config:
        orm_mode = True

# ATUALIZADO
class TenantRegistration(BaseModel):
    tenant_name: constr(min_length=3, max_length=50)
    owner_email: EmailStr
    owner_cpf: str
    owner_password: str
    password_confirm: str

class TokenData(BaseModel):
    email: str | None = None

class TenantSchema(BaseModel):
    id: int
    name: str
    schema_name: str
    status: str
    trial_ends_at: date
    class Config:
        orm_mode = True

class MeSchema(BaseModel):
    user: UserSchema
    tenant: TenantSchema

# --- Schemas para Alunos ---
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

