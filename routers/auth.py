# routers/auth.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import timedelta
import stripe # Importe a biblioteca do Stripe

# Nossos módulos
import models
import schemas
import security
import config # Importe o arquivo de configuração
from database import get_db, engine

# Configure a chave da API do Stripe a partir do arquivo config
stripe.api_key = config.STRIPE_API_KEY

router = APIRouter(tags=["Área Pública e Autenticação"])

@router.post("/api/register")
def register_tenant(form_data: schemas.TenantRegistration, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == form_data.owner_email).first():
        raise HTTPException(status_code=400, detail="Email já está em uso.")
    
    schema_name = form_data.tenant_name.lower().replace(" ", "_").strip()
    if db.query(models.Tenant).filter(models.Tenant.schema_name == schema_name).first():
        raise HTTPException(status_code=400, detail="Nome da academia já está em uso.")
        
    db_tenant = None
    try:
        # 1. Cria um Cliente no Stripe primeiro
        customer = stripe.Customer.create(
            email=form_data.owner_email,
            name=form_data.tenant_name,
            metadata={
                "schema_name": schema_name
            }
        )

        # 2. Continua com a criação no nosso banco de dados
        with db.begin_nested():
            db_tenant = models.Tenant(
                name=form_data.tenant_name, 
                schema_name=schema_name,
                stripe_customer_id=customer.id # Salva o ID do cliente do Stripe
            )
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
    except Exception as e:
        # Se algo der errado, tentamos deletar o cliente no Stripe para não deixar lixo
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

# --- ROTA PARA OBTER DADOS DO USUÁRIO LOGADO ---
@router.get("/api/me", response_model=schemas.MeSchema)
def read_users_me(current_user: models.User = Depends(security.get_current_user)):
    """
    Retorna os dados do usuário logado e do seu tenant.
    O frontend usará isso para verificar o status da assinatura.
    """
    return {"user": current_user, "tenant": current_user.tenant}

