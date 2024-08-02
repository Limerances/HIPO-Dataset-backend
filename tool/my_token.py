from jwt import encode
from jwt import decode
import datetime
import settings
from enum import Enum

def generate_token(id,email,name,type):
    # If the type is an enum type, it needs to be converted to an int
    if isinstance(type, Enum):
        type = type.value
    data = {
        'id':id,
        'email': email,
        'username': name,
        'type': type,
        'logintime': str(datetime.datetime.now()),
    }
    return encode(data, settings.Configs.SECRET_KEY, algorithm='HS256')

def check_token(id,token):
    try:
        data = decode(token, settings.Configs.SECRET_KEY, algorithms='HS256')
        if datetime.datetime.now() - datetime.datetime.strptime(data['logintime'], '%Y-%m-%d %H:%M:%S.%f') <= datetime.timedelta(hours=6) and\
            data['id'] == id:
            return True
    except:
        return False
    return False

def get_info(token):
    try:
        data = decode(token, settings.Configs.SECRET_KEY, algorithms='HS256')
        return data
    except:
        return None
    return None
