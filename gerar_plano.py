import mercadopago

# Seu token de teste
sdk = mercadopago.SDK("TEST-1721733035858480-012708-4e2e3afde2b470ef92d73bb21f26520f-263069598")

plan_data = {
    "reason": "Plano MedTools Teste",
    "payer_email": "juniormendesjp@gmail.com", # <--- ADICIONE O E-MAIL DA CONTA DE TESTE AQUI
    "auto_recurring": {
        "frequency": 1,
        "frequency_type": "months",
        "transaction_amount": 49.90,
        "currency_id": "BRL"
    },
    "back_url": "https://www.google.com"
}

result = sdk.preapproval().create(plan_data)

if result["status"] == 201:
    print("✅ Plano criado com sucesso!")
    print(f"ID do Plano: {result['response']['id']}")
else:
    print("❌ Erro ao criar plano:")
    print(result["response"])