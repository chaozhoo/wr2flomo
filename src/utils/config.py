import json
import os
from cryptography.fernet import Fernet
import keyring

class Config:
    def __init__(self):
        self.config_file = 'config.json'
        self.key = self.get_or_create_key()
        self.fernet = Fernet(self.key)
        self.config = self.load_config()
        self.config = {
            'font_size': 14,  # 添加默认字体大小
        }

    def get_or_create_key(self):
        key = keyring.get_password("wr2flomo", "encryption_key")
        if not key:
            key = Fernet.generate_key()
            keyring.set_password("wr2flomo", "encryption_key", key.decode())
        return key

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'rb') as f:
                encrypted_data = f.read()
                decrypted_data = self.fernet.decrypt(encrypted_data)
                config = json.loads(decrypted_data)
        else:
            config = {}
        
        if 'db_path' not in config:
            config['db_path'] = ''
        
        return config

    def save_config(self):
        encrypted_data = self.fernet.encrypt(json.dumps(self.config).encode())
        with open(self.config_file, 'wb') as f:
            f.write(encrypted_data)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config()

    def get_api_key(self):
        return os.environ.get('FLOMO_API_KEY') or keyring.get_password("wr2flomo", "flomo_api_key")

    def set_api_key(self, api_key):
        keyring.set_password("wr2flomo", "flomo_api_key", api_key)

    def set_db_path(self, path):
        self.config['db_path'] = path
        self.save_config()

    def get_db_path(self):
        return self.config.get('db_path', '')

    def get_api_url(self):
        return self.config.get('flomo_api_url', '')

    def set_api_url(self, url):
        self.config['flomo_api_url'] = url
        self.save_config()
