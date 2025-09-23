# routers/auth.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import timedelta
import stripe 

import models
import schemas
import security
import config 
from database import get_db, engine

stripe.api_key = config.STRIPE_API_KEY

router = APIRouter(tags=["Área Pública e Autenticação"])

# ATUALIZADO
@router.post("/api/register")
def register_tenant(form_data: schemas.TenantRegistration, db: Session = Depends(get_db)):
    # 1. Validação dos dados de entrada
    if form_data.owner_password != form_data.password_confirm:
        raise HTTPException(status_code=400, detail="As senhas não coincidem.")

    if db.query(models.User).filter(models.User.email == form_data.owner_email).first():
        raise HTTPException(status_code=400, detail="Email já está em uso.")
    
    if db.query(models.User).filter(models.User.cpf == form_data.owner_cpf).first():
        raise HTTPException(status_code=400, detail="CPF já está cadastrado.")

    schema_name = form_data.tenant_name.lower().replace(" ", "_").strip()
    if db.query(models.Tenant).filter(models.Tenant.schema_name == schema_name).first():
        raise HTTPException(status_code=400, detail="Nome da academia já está em uso.")
        
    db_tenant = None
    try:
        # 2. Cria o Cliente no Stripe
        customer = stripe.Customer.create(
            email=form_data.owner_email,
            name=form_data.tenant_name,
            metadata={ "schema_name": schema_name },
            # Adiciona o CPF como um ID fiscal no Stripe (bom para notas fiscais no Brasil)
            tax_id_data=[{"type": "br_cpf", "value": form_data.owner_cpf}],
        )

        # 3. Cria o Tenant e o Usuário no nosso banco de dados
        with db.begin_nested():
            db_tenant = models.Tenant(
                name=form_data.tenant_name, 
                schema_name=schema_name,
                stripe_customer_id=customer.id
            )
            db.add(db_tenant)
            db.flush() 

            hashed_password = security.get_password_hash(form_data.owner_password)
            db_user = models.User(
                email=form_data.owner_email, 
                cpf=form_data.owner_cpf,
                hashed_password=hashed_password,
                tenant_id=db_tenant.id
            )
            db.add(db_user)

            db.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))
            models.Aluno.metadata.create_all(bind=engine, tables=[models.Aluno.__table__], checkfirst=True)
        
        db.commit()
    except Exception as e:
        # Se algo der errado, deleta o cliente que foi criado no Stripe para não deixar lixo
        if 'customer' in locals() and customer:
            stripe.Customer.delete(customer.id)
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro interno: {e}")

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

@router.get("/api/me", response_model=schemas.MeSchema)
def read_users_me(current_user: models.User = Depends(security.get_current_user)):
    """
    Endpoint para o frontend obter os dados do usuário logado e do seu tenant.
    """
    return {"user": current_user, "tenant": current_user.tenant}

