import requests

url = "https://a2aad873c8ca.ngrok-free.app/webhook"

payload = {"teste": "mensagem"}
response = requests.post(url, json=payload)
print("Status:", response.status_code)
print("Resposta:", response.text)