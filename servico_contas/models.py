import uuid
from enum import Enum as PyEnum

from sqlalchemy import Column, String, DateTime, func, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Usamos Enums para garantir a integridade dos dados para campos
# que possuem um conjunto fixo de opções, como planos e status.
class Plan(PyEnum):
    FREE = "free"
    PREMIUM = "premium"
    TRIAL = "trial"

class AccountStatus(PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TRIAL_EXPIRED = "trial_expired"
    PAYMENT_PENDING = "payment_pending"


class Academy(Base):
    """
    Representa um tenant (uma academia cliente) no sistema.
    Esta é a tabela central para o controle de multi-tenancy.
    """
    __tablename__ = "academies"

    # Usamos UUID como chave primária. É uma prática melhor para sistemas
    # distribuídos (microsserviços) para evitar colisões de ID.
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String(100), nullable=False, comment="Nome fantasia da academia")
    
    # O plano atual da academia. O Enum garante que só valores válidos sejam inseridos.
    plan = Column(Enum(Plan), nullable=False, default=Plan.TRIAL)
    
    # Status da conta da academia, importante para a lógica de negócio.
    status = Column(Enum(AccountStatus), nullable=False, default=AccountStatus.ACTIVE)

    # Campos de auditoria, preenchidos automaticamente pelo banco de dados.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Academy(id={self.id}, name='{self.name}', plan='{self.plan.value}')>"