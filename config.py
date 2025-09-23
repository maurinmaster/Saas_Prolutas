# config.py

# --- Configurações do Stripe ---
# ATENÇÃO: Substitua pelas suas chaves reais do painel do Stripe.
# Use as chaves de "Teste" durante o desenvolvimento.
STRIPE_API_KEY = "sk_test_SUA_CHAVE_SECRETA_AQUI"
STRIPE_WEBHOOK_SECRET = "whsec_SEU_SEGREDO_DE_WEBHOOK_AQUI"

# Crie um produto e um preço no seu painel do Stripe e cole o ID do preço aqui.
# Ex: "Plano Mensal", R$ 99,00/mês
STRIPE_PRICE_ID = "price_SEU_ID_DE_PRECO_AQUI"


# --- Configurações da Aplicação ---
# URL base do seu frontend. Usada para redirecionar o usuário após o pagamento.
APP_BASE_URL = "http://127.0.0.1:8000"
