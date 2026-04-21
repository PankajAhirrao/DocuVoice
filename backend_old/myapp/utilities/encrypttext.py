import base64

def encode_text(text):
    """Encode text using Base64."""
    text_bytes = text.encode('utf-8')
    encoded_bytes = base64.b64encode(text_bytes)
    return encoded_bytes.decode('utf-8')

def decode_text(encoded_text):
    """Decode text using Base64."""
    encoded_bytes = encoded_text.encode('utf-8')
    text_bytes = base64.b64decode(encoded_bytes)
    return text_bytes.decode('utf-8')