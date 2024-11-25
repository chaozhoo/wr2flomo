import requests
from .config import Config

class FlomoAPI:
    def __init__(self, api_url):
        self.api_url = api_url

    def send_note(self, content):
        try:
            response = requests.post(self.api_url, json={"content": content})
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Error sending note to Flomo: {e}")
            return False

    def create_memo(self, content):
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            'content': content
        }
        try:
            response = requests.post(self.api_url, json=data, headers=headers)
            response.raise_for_status()
            return {'code': 0, 'message': 'Success'}
        except requests.RequestException as e:
            return {'code': -1, 'message': str(e)}
