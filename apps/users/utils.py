import uuid
import hashlib

def generate_reset_code():
    code = str(uuid.uuid4()).split("-")[0]  # ex: '5f2b1a'
    hashed = hashlib.sha256(code.encode()).hexdigest()
    return code, hashed
