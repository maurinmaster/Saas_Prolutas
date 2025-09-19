import uuid
from enum import Enum as PyEnum

from sqlalchemy import Column, String, DateTime, func, Boolean, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

# Em um projeto real, essa Base pode ser compartilhada entre os serviços
# se eles usarem o mesmo código base, ou definida independentemente.
Base = declarative_base()

class UserRole(PyEnum):
    ACADEMY_OWNER = "academy_owner" # Dono da academia, permissão máxima
    INSTRUCTOR = "instructor"
    STUDENT = "student"

class User(Base):
    """
    Representa um usuário final do sistema, que pode ser de qualquer academia.
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # CAMPO MAIS IMPORTANTE PARA MULTI-TENANCY!
    # Esta Foreign Key conecta o usuário diretamente a uma academia.
    # Garante que cada usuário pertença a apenas um tenant.
    # O `index=True` acelera as buscas filtradas por academia.
    academy_id = Column(UUID(as_uuid=True), ForeignKey("academies.id"), nullable=False, index=True)

    email = Column(String(255), unique=True, nullable=False, index=True)
    
    # NUNCA armazene a senha em texto puro. Este campo guardará o hash da senha.
    hashed_password = Column(String(255), nullable=False)
    
    full_name = Column(String(100), nullable=True)
    
    # Papel do usuário dentro da sua academia, para controle de permissões.
    role = Column(Enum(UserRole), nullable=False, default=UserRole.STUDENT)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role.value}')>"