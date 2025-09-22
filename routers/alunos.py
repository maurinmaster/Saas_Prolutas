# routers/alunos.py

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
import security
from database import get_db

router = APIRouter(
    prefix="/api/alunos",
    tags=["Gestão de Alunos"]
)

@router.post("/", response_model=schemas.AlunoSchema, status_code=status.HTTP_201_CREATED)
def criar_aluno(
    aluno: schemas.AlunoCreate,
    x_tenant_id: str = Header(..., alias="x-tenant-id"),
    current_user: models.User = Depends(security.get_current_user), 
    db: Session = Depends(get_db)
):
    security.validate_tenant_access(x_tenant_id, current_user)
    db_aluno = models.Aluno(**aluno.dict())
    db.add(db_aluno)
    db.commit()
    db.refresh(db_aluno)
    return db_aluno

@router.get("/", response_model=List[schemas.AlunoSchema])
def listar_alunos(
    x_tenant_id: str = Header(..., alias="x-tenant-id"),
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    security.validate_tenant_access(x_tenant_id, current_user)
    return db.query(models.Aluno).all()

@router.get("/{aluno_id}", response_model=schemas.AlunoSchema)
def obter_aluno(
    aluno_id: int,
    x_tenant_id: str = Header(..., alias="x-tenant-id"),
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    security.validate_tenant_access(x_tenant_id, current_user)
    aluno = db.query(models.Aluno).filter(models.Aluno.id == aluno_id).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado.")
    return aluno

@router.put("/{aluno_id}", response_model=schemas.AlunoSchema)
def atualizar_aluno(
    aluno_id: int,
    aluno_update: schemas.AlunoUpdate,
    x_tenant_id: str = Header(..., alias="x-tenant-id"),
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    security.validate_tenant_access(x_tenant_id, current_user)
    db_aluno = db.query(models.Aluno).filter(models.Aluno.id == aluno_id).first()
    if not db_aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado.")
    
    update_data = aluno_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_aluno, key, value)
        
    db.add(db_aluno)
    db.commit()
    db.refresh(db_aluno)
    return db_aluno

@router.delete("/{aluno_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_aluno(
    aluno_id: int,
    x_tenant_id: str = Header(..., alias="x-tenant-id"),
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    security.validate_tenant_access(x_tenant_id, current_user)
    db_aluno = db.query(models.Aluno).filter(models.Aluno.id == aluno_id).first()
    if not db_aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado.")
        
    db.delete(db_aluno)
    db.commit()
    return None
