import requests
import base64
import json
from datetime import datetime
import os

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
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    authorization_code = os.getenv("AUTHORIZATION_CODE")

    # Define o caminho do arquivo em que serão salvos os tokens
    tokens_dir = "tokens"
    config_path = os.path.join(tokens_dir, "tokens.json")

    # Garante que o diretório exista
    if not os.path.exists(tokens_dir):
        os.makedirs(tokens_dir)

    # Verifica se o arquivo JSON existe
    if not os.path.isfile(config_path) or os.path.getsize(config_path) == 0:
        print("Arquivo de tokens não encontrado ou vazio. Gerando tokens iniciais.")
        new_refresh_token, access_token = troca_code_por_tokens(client_id, client_secret, authorization_code)
    else:
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
            refresh_token_value = config.get("refresh_token")
            new_refresh_token, access_token = refresh_tokens(client_id, client_secret, refresh_token_value)
        except json.JSONDecodeError:
            print("Arquivo tokens.json corrompido ou inválido. Gerando tokens iniciais novamente.")
            new_refresh_token, access_token = troca_code_por_tokens(client_id, client_secret, authorization_code)

    if new_refresh_token and access_token:
        token_data = {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "updated_at": datetime.now().isoformat()
        }
        with open(config_path, "w") as f:
            json.dump(token_data, f, indent=4)
        print("Tokens atualizados com sucesso.")
    else:
        print("Falha na atualização dos tokens.")

if __name__ == "__main__":
    atualiza_tokens()
