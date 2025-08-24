import requests
import json # Importar a biblioteca json para formatar a saída

# ATENÇÃO: SUBSTITUA ESTES VALORES PELOS SEUS!
# O token de acesso que você pegou no SendPulse.
access_token = 'SEU_ACCESS_TOKEN_AQUI' 

# ID do destinatário para o teste. Pode ser seu próprio ID em um chatbot do SendPulse.
# Exemplo: Se for um chatbot do Facebook, é o ID do usuário do Messenger.
# Você precisa obter este ID do painel do SendPulse, no histórico de conversas do seu chatbot.
id_do_destinatario = 'ID_DO_DESTINATARIO_AQUI' 

# URL da API do SendPulse para enviar mensagens via chatbot.
url_sendpulse = 'https://api.sendpulse.com/chatbot/send-message'

# Dados da mensagem que vamos enviar.
# Queremos que ela vá para o 'id_do_destinatario' e o texto será "Mensagem de teste via API SendPulse".
payload_da_mensagem = {
    "recipient": {
        "id": id_do_destinatario
    },
    "message": {
        "text": "Mensagem de teste via API SendPulse do Python!"
    }
}

# Cabeçalhos necessários para a requisição.
# Isso informa ao SendPulse que estamos autorizados e enviando dados JSON.
headers_da_requisicao = {
    'Authorization': f'Bearer {access_token}', # Seu token de acesso vai aqui
    'Content-Type': 'application/json' # Informa que o conteúdo é JSON
}

print("Tentando enviar mensagem para SendPulse...")
print(f"URL: {url_sendpulse}")
print(f"Payload: {json.dumps(payload_da_mensagem, indent=2)}") # Imprime o payload formatado para fácil leitura

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