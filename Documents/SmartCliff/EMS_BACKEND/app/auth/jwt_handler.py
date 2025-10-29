from datetime import timedelta, datetime
from jose import JWTError
import jwt

secret_key= "This is my super powerfull secret_key. No one can find it...."
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    encode = data.copy()
    expire_time = datetime.utcnow() + timedelta(minutes= ACCESS_TOKEN_EXPIRE_MINUTES)
    encode.update({'exp': expire_time})
    token = jwt.encode(encode, secret_key, algorithm= ALGORITHM)
    return token
    
def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, secret_key, algorithms=ALGORITHM)
        return payload
    except Exception as e:
        return e
    