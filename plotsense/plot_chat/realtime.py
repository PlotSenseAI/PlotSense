import requests


class RealtimeClient:
    def __init__(self, client):
        self.client = client

    def generate_ephemeral_key(self) -> str:
        url = "https://api.openai.com/v1/realtime/client_secrets"
        headers = {
            "Authorization": f"Bearer {self.client.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "session": {
                "type": "realtime",
                "model": "gpt-realtime"
            }
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            print("Ephemeral key generated:", data)
            return data.get("value")
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to generate ephemeral key: {e}") from e

