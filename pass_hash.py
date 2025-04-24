import hashlib


def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(password: str, hashed_password: str):
    return hash_password(password) == hashed_password