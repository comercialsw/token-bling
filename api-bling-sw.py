import requests
import base64
import json
from datetime import datetime
import os

# Defina seus dados diretamente aqui:
CLIENT_ID = "7ded8c4961025039acfd743f5674651aebafd95b"
CLIENT_SECRET = "a35582aacfe993dc3dda23f14aaa756f45f3c3d48228e7929009bfb903e6"
AUTHORIZATION_CODE = "0b40cffd2f0a4b8caa1bbf4a8720a4849a2f71ed"

def troca_code_por_tokens(client_id, client_secret, authorization_code):
    """
    Tenta obter refresh_token e access_token usando o authorization_code (fluxo inicial).
    """
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
    """
    Tenta renovar refresh_token e access_token usando o refresh_token atual.
    """
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
    # Usa os valores definidos diretamente no script
    client_id = CLIENT_ID
    client_secret = CLIENT_SECRET

    tokens_dir = "tokens"
    config_path = os.path.join(tokens_dir, "tokens.json")

    # Garante que a pasta "tokens" exista
    if not os.path.exists(tokens_dir):
        os.makedirs(tokens_dir)

    # Verifica se já existe um arquivo tokens.json válido
    if not os.path.isfile(config_path) or os.path.getsize(config_path) == 0:
        print("Arquivo tokens.json não encontrado ou está vazio. Vamos usar o authorization code inicial.")

        # Usa o authorization code definido diretamente
        authorization_code = AUTHORIZATION_CODE

        if not authorization_code:
            print("Nenhum AUTHORIZATION_CODE definido. Impossível gerar tokens iniciais.")
            return

        new_refresh_token, access_token = troca_code_por_tokens(client_id, client_secret, authorization_code)
    else:
        with open(config_path, "r") as f:
            config = json.load(f)

        refresh_token_value = config.get("refresh_token")
        if refresh_token_value:
            new_refresh_token, access_token = refresh_tokens(client_id, client_secret, refresh_token_value)
        else:
            print("Não há refresh_token no arquivo. Vamos tentar novamente com o authorization code.")
            authorization_code = AUTHORIZATION_CODE
            new_refresh_token, access_token = troca_code_por_tokens(client_id, client_secret, authorization_code)

    if new_refresh_token and access_token:
        token_data = {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "updated_at": datetime.now().isoformat()
        }
        with open(config_path, "w") as f:
            json.dump(token_data, f, indent=4)
        print("Tokens atualizados com sucesso em:", config_path)
    else:
        print("Falha na atualização dos tokens.")

if __name__ == "__main__":
    atualiza_tokens()
