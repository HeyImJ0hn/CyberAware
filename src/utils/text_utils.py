import re
import unicodedata

class TextUtils:
    # Remove special characters from text
    @staticmethod
    def clean_text(text):
        normalized_text = unicodedata.normalize('NFKD', text)
        without_diacritics = ''.join([c for c in normalized_text if not unicodedata.combining(c)])
        return re.sub(r'[^a-zA-Z0-9]', '', without_diacritics).lower()