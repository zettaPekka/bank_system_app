from authx import AuthX, AuthXConfig
import jwt


config = AuthXConfig()
config.JWT_SECRET_KEY = 'secret_key'
config.JWT_ACCESS_COOKIE_NAME = 'access_token'
config.JWT_TOKEN_LOCATION = ['cookies']
config.JWT_ALGORITHM = 'HS256'

security = AuthX(config)

def create_jwt(user_id: int):
    jw_token = security.create_access_token(uid=str(user_id))
    return jw_token

def check_jwt(token: str):
    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=['HS256'])
        print(payload)
        return payload['sub']
    except Exception as e:
        print(e)
        return None