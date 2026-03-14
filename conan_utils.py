import base64
import hashlib

def xor_encrypt(data, key):
    res = bytearray()
    for i in range(len(data)):
        res.append(ord(data[i]) ^ ord(key[i % len(key)]))
    return base64.b64encode(res).decode('utf-8')

def xor_decrypt(encoded_data, key):
    data = base64.b64decode(encoded_data)
    res = bytearray()
    for i in range(len(data)):
        res.append(data[i] ^ ord(key[i % len(key)]))
    return res.decode('utf-8')

def hash_password(password, key="ConanEncryptKey2024"):
    sha256_hash = hashlib.sha256(password.encode()).hexdigest()
    return xor_encrypt(sha256_hash, key)
