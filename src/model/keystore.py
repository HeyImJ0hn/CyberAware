class KeyStore:
    def __init__(self, path, store_password):
        self._path = path
        self._store_password = store_password
        self._key_alias = "cyberaware"
        self._key_password = store_password
        
    def get_path(self):
        return self._path
    
    def get_store_password(self):
        return self._store_password
    
    def get_key_alias(self):
        return self._key_alias
    
    def get_key_password(self):
        return self._key_password