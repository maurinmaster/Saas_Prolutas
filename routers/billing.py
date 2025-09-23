# routers/billing.py

from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
import stripe

import models, schemas, config, security
from database import get_db

# Configure a chave da API do Stripe
stripe.api_key = config.STRIPE_API_KEY

router = APIRouter(
    prefix="/api/billing",
    tags=["Gestão de Pagamentos"]
)

@router.post("/create-checkout-session")
def create_checkout_session(
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Cria uma sessão de checkout no Stripe para o usuário logado iniciar a assinatura.
    """
    if not current_user.tenant or not current_user.tenant.stripe_customer_id:
        raise HTTPException(status_code=400, detail="Cliente não encontrado no sistema de pagamento.")

    try:
        checkout_session = stripe.checkout.Session.create(
            customer=current_user.tenant.stripe_customer_id,
            payment_method_types=['card'],
            line_items=[
                {
                    'price': config.STRIPE_PRICE_ID,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=config.APP_BASE_URL + '?payment_success=true',
            cancel_url=config.APP_BASE_URL + '?payment_canceled=true',
        )
        return {"sessionId": checkout_session.id, "url": checkout_session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stripe-webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint para receber eventos do Stripe (webhooks).
    Atualiza o status da assinatura no nosso banco de dados.
    """
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, config.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Payload inválido
        raise HTTPException(status_code=400, detail=str(e))
    except stripe.error.SignatureVerificationError as e:
        # Assinatura inválida
        raise HTTPException(status_code=400, detail=str(e))

    # --- Lidar com o evento ---
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_id = session.get('customer')
        subscription_id = session.get('subscription')

        # Atualiza nosso banco de dados com o ID da assinatura
        tenant = db.query(models.Tenant).filter(models.Tenant.stripe_customer_id == customer_id).first()
        if tenant:
            tenant.stripe_subscription_id = subscription_id
            tenant.status = 'active' # Assinatura iniciada!
            db.commit()

    if event['type'] in ['customer.subscription.updated', 'customer.subscription.deleted']:
        subscription = event['data']['object']
        customer_id = subscription.get('customer')
        status = subscription.get('status') # ex: active, past_due, canceled

        # Atualiza o status no nosso banco de dados
        tenant = db.query(models.Tenant).filter(models.Tenant.stripe_customer_id == customer_id).first()
        if tenant:
            tenant.status = status
            db.commit()

    return {"status": "success"}
