import requests
import base64
import json
from datetime import datetime
import os

# Defina seus dados diretamente aqui:
CLIENT_ID = "7ded8c4961025039acfd743f5674651aebafd95b"
CLIENT_SECRET = "a35582aacfe993dc3dda23f14aaa756f45f3c3d48228e7929009bfb903e6"
AUTHORIZATION_CODE = "c27314314c08d02fcb469f5ae97a3e6b4d600789"

TOKEN_FILE = "tokens.json"  # Salvará o token na raiz do repositório GitHub

def troca_code_por_tokens(client_id, client_secret, authorization_code):
    encoded_credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    api_url = "https://www.bling.com.br/Api/v3/oauth/token"
    headers = {
        "Authorization": "Basic " + encoded_credentials,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = f"grant_type=authorization_code&code={authorization_code}"
    response = requests.post(api_url, headers=headers, data=payload)

    if response.status_code == 200:
        data = response.json()
        return data.get("refresh_token"), data.get("access_token")
    else:
        print("Erro ao trocar code por tokens:", response.status_code, response.text)
        return None, None

def refresh_tokens(client_id, client_secret, refresh_token):
    encoded_credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    api_url = "https://www.bling.com.br/Api/v3/oauth/token"
    headers = {
        "Authorization": "Basic " + encoded_credentials,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = f"grant_type=refresh_token&refresh_token={refresh_token}"
    response = requests.post(api_url, headers=headers, data=payload)

    if response.status_code == 200:
        data = response.json()
        return data.get("refresh_token"), data.get("access_token")
    else:
        print("Erro ao atualizar tokens:", response.status_code, response.text)
        return None, None

def atualiza_tokens():
    if not os.path.isfile(TOKEN_FILE) or os.path.getsize(TOKEN_FILE) == 0:
        print("Arquivo token.json não encontrado ou está vazio. Usando authorization code.")
        new_refresh_token, access_token = troca_code_por_tokens(CLIENT_ID, CLIENT_SECRET, AUTHORIZATION_CODE)
    else:
        with open(TOKEN_FILE, "r") as f:
            config = json.load(f)

        refresh_token_value = config.get("refresh_token")
        if refresh_token_value:
            new_refresh_token, access_token = refresh_tokens(CLIENT_ID, CLIENT_SECRET, refresh_token_value)
        else:
            print("Refresh token não encontrado. Usando authorization code.")
            new_refresh_token, access_token = troca_code_por_tokens(CLIENT_ID, CLIENT_SECRET, AUTHORIZATION_CODE)

    if new_refresh_token and access_token:
        token_data = {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "updated_at": datetime.now().isoformat()
        }
        with open(TOKEN_FILE, "w") as f:
            json.dump(token_data, f, indent=4)
        print("Tokens atualizados com sucesso.")
    else:
        print("Falha ao atualizar os tokens.")

if __name__ == "__main__":
    atualiza_tokens()
