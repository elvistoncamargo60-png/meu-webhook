import requests
import json  # Importar a biblioteca json para formatar a saída

# ATENÇÃO: SUBSTITUA ESTES VALORES PELOS SEUS!
# O token de acesso que você pegou no SendPulse.
access_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6ImUwZmI4YzAxOTFmZTAxNDhjZjgwMjZlYTgwMmY1NmI0MTUzNDU3ZjNiNmQzZDIyMWJhNTMzYWRmYWQ2ZWJiYzllODFiZjQyOGEzOTliMjEwIn0.eyJhdWQiOiJiNGVkODMwNmQ4N2RiMWUwNWE0ZmUyMTYzZGRlZGU3ZSIsImp0aSI6ImUwZmI4YzAxOTFmZTAxNDhjZjgwMjZlYTgwMmIifQ...'  # Cole seu token aqui inteiro

# ID do destinatário para o teste. Pode ser seu próprio ID em um chatbot do SendPulse.
id_do_destinatario = 'COLE_AQUI_O_ID_DO_DESTINATARIO'

# URL da API do SendPulse para enviar mensagens via chatbot.
url_sendpulse = 'https://api.sendpulse.com/chatbot/send-message'

# Dados da mensagem que vamos enviar.
payload_da_mensagem = {
    "recipient": {
        "id": id_do_destinatario
    },
    "message": {
        "text": "Mensagem de teste via API SendPulse do Python!"
    }
}

# Cabeçalhos necessários para a requisição.
headers_da_requisicao = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

print("Tentando enviar mensagem para SendPulse...")
print(f"URL: {url_sendpulse}")
print(f"Payload: {json.dumps(payload_da_mensagem, indent=2)}")  # Imprime o payload formatado para fácil leitura

try:
    # Faz a requisição POST para a API do SendPulse.
    response = requests.post(url_sendpulse, json=payload_da_mensagem, headers=headers_da_requisicao)

    # Imprime o código de status da resposta (ex: 200 para sucesso, 400/500 para erro).
    print(f'\nStatus da Resposta: {response.status_code}')
    # Imprime o corpo da resposta do SendPulse.
    print(f'Corpo da Resposta: {response.text}')

    if response.status_code == 200:
        print("\nMensagem enviada com sucesso (verifique no SendPulse)!")
    else:
        print(f"\nErro ao enviar mensagem. Detalhes: {response.text}")

except requests.exceptions.RequestException as e:
    print(f"\nOcorreu um erro na requisição: {e}")

