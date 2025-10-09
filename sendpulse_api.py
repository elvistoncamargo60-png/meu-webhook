import requests
import time

class SendPulseAPI:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None
        self.token_expire_time = 0

    def authenticate(self):
        if self.token and time.time() < self.token_expire_time:
            return self.token

        url = "https://api.sendpulse.com/oauth/access_token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            self.token = data['access_token']
            self.token_expire_time = time.time() + data['expires_in'] - 60
            return self.token
        else:
            raise Exception(f"Erro na autenticação SendPulse: {response.text}")

    def get_headers(self):
        token = self.authenticate()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

