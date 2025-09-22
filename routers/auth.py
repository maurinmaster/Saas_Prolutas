# routers/auth.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import timedelta
from database import Base

import models
import schemas
import security
from database import get_db, engine

router = APIRouter(tags=["Área Pública"])

@router.post("/api/register")
def register_tenant(form_data: schemas.TenantRegistration, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == form_data.owner_email).first():
        raise HTTPException(status_code=400, detail="Email já está em uso.")
    
    schema_name = form_data.tenant_name.lower().replace(" ", "_").strip()
    if db.query(models.Tenant).filter(models.Tenant.schema_name == schema_name).first():
        raise HTTPException(status_code=400, detail="Nome da academia já está em uso.")
        
    with db.begin_nested():
        db_tenant = models.Tenant(name=form_data.tenant_name, schema_name=schema_name)
        db.add(db_tenant)
        db.flush() 

        hashed_password = security.get_password_hash(form_data.owner_password)
        db_user = models.User(
            email=form_data.owner_email, 
            hashed_password=hashed_password,
            tenant_id=db_tenant.id
        )
        db.add(db_user)

        db.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))
        models.Aluno.metadata.create_all(bind=engine, tables=[models.Aluno.__table__], checkfirst=True)
    
    db.commit()
    return {"message": f"Academia '{db_tenant.name}' registrada com sucesso! Faça o login."}

@router.post("/api/login/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=400, detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = security.create_access_token(
        data={"sub": user.email}, 
        expires_delta=timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}
