from authx import AuthX, AuthXConfig
import jwt

from datetime import timedelta


config = AuthXConfig()
config.JWT_SECRET_KEY = 'secret_key'
config.JWT_ACCESS_COOKIE_NAME = 'access_token'
config.JWT_TOKEN_LOCATION = ['cookies']
config.JWT_ALGORITHM = 'HS256'

security = AuthX(config)

def create_jwt(user_id: int):
    expiry_timedelta = timedelta(seconds=2592000)
    jw_token = security.create_access_token(uid=str(user_id), expiry=expiry_timedelta)
    return jw_token

def check_jwt(token: str):
    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=['HS256'])
        return payload['sub']
    except Exception as e:
        print(e)
        return None