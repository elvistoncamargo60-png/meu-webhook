import requests
import time

class SendPulseAuth:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id  # Salva client_id
        self.client_secret = client_secret  # Salva client_secret
        self.token = None
        self.token_expire_time = 0
        self.last_renewal_time = None

    def _get_new_token(self):
        url = 'https://api.sendpulse.com/oauth/access_token'
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        response = requests.post(url, data=data)
        response.raise_for_status()
        token_info = response.json()
        self.token = token_info.get('access_token')
        expires_in = token_info.get('expires_in', 3600)
        self.token_expire_time = time.time() + expires_in - 60
        self.last_renewal_time = time.time()
        print(f"Novo token gerado, válido por {expires_in} segundos.")

    def get_token(self):
        if self.token is None or time.time() >= self.token_expire_time:
            self._get_new_token()
        return self.token

    def get_last_renewal(self):
        return self.last_renewal_time

