import time
from django.core import signing
import hashlib
from django.conf import settings

HEADER = {'typ': 'JWP', 'alg': 'default'}
KEY = settings.SECRETS['signing']['key']
SALT = settings.SECRETS['signing']['salt']


def encrypt(obj):
    """加密"""
    value = signing.dumps(obj, key=KEY, salt=SALT)
    value = signing.b64_encode(value.encode()).decode()
    return value


def decrypt(src):
    """解密"""
    src = signing.b64_decode(src.encode()).decode()
    raw = signing.loads(src, key=KEY, salt=SALT)
    return raw


def create_token(user_id):
    """生成token信息"""
    # 1. 加密头信息
    header = encrypt(HEADER)
    # 2. 构造Payload(有效期14天)
    payload = {"user_id": user_id, "iat": time.time(), "exp": time.time()+1209600.0}
    payload = encrypt(payload)
    # 3. 生成签名
    md5 = hashlib.md5()
    md5.update(("%s.%s" % (header, payload)).encode())
    signature = md5.hexdigest()
    token = "%s.%s.%s" % (header, payload, signature)
    # 存储到缓存中
    # cache.set(username, token, TIME_OUT)
    return token


def get_payload(token):
    payload = str(token).split('.')[1]
    payload = decrypt(payload)
    return payload


# 通过token获取用户名
def get_user_id(token):
    payload = get_payload(token)
    return payload['user_id']


def get_exp_time(token):
    payload = get_payload(token)
    return payload['exp']


def check_token(username, token):
    return get_username(token) == username and get_exp_time(token) > time.time()
