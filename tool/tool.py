import settings
from enum import Enum
from datetime import datetime
import secrets
import string

def convert_enum_to_value(data):
    if isinstance(data, dict):
        return {key: convert_enum_to_value(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_enum_to_value(value) for value in data]
    elif isinstance(data, Enum):
        return data.value
    elif isinstance(data, datetime):
        return str(data)
    else:
        return data

def convert(data):
    return convert_enum_to_value(data)

#递归转换id的值，一层层拆，直到int，记得处理错误
def convert_int(id):
    new_id = None
    try:
        if isinstance(id, Enum):
            new_id = convert_int(id.value)
        elif isinstance(id, str):
            new_id = int(id)
        else:
            new_id = id
        result = True
    except:
        result = False
    return new_id, result


def generate_secure_random_string(length=16):
    letters = string.ascii_letters + string.digits
    secure_str = ''.join(secrets.choice(letters) for _ in range(length))
    return secure_str

def md5_salt(password, exsalt="kana"):
    import hashlib
    salt = password[:4] + exsalt
    m = hashlib.md5(str(password).join(salt).encode())
    md5pwd = m.hexdigest()
    return md5pwd