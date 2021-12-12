from __future__ import annotations

import json
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

import Messages.Crypto


class SymmetricLayer:
    def __init__(self, key: bytes = None):
        if key is None:
            self.__KEY = get_random_bytes(32)
        else:
            key = key * 4
            self.__KEY = key[:32]

    def encrypt(self, plain_text: bytes | str):
        symmetric = AES.new(self.__KEY, AES.MODE_EAX)
        plain_text = plain_text if type(plain_text) == bytes else plain_text.encode('utf8')
        return [symmetric.encrypt(plaintext=plain_text), symmetric.nonce, symmetric.digest()]

    def decrypt(self, cipher_text: bytes | str, nonce: bytes, tag: bytes):
        symmetric = AES.new(self.__KEY, AES.MODE_EAX, nonce=nonce)
        cipher_text = cipher_text if type(cipher_text) == bytes else cipher_text.encode('utf8')
        return symmetric.decrypt_and_verify(cipher_text, tag)

    def enc_dict(self, dic: dict | bytes | str):
        try:
            res = self.encrypt(json.dumps(dic)) if type(dic) == dict else self.encrypt(dic)
            return Messages.Crypto.CryptoMessage(enc_message=b64encode(res[0]).decode('utf8'),
                                                 nonce=b64encode(res[1]).decode('utf8'),
                                                 tag=b64encode(res[2]).decode('utf8')).to_json_byte()
        except Exception as e:
            print('Encryption Error')
            return None

    def dec_dict(self, dic: bytes):
        try:
            dic = json.loads(dic)
            if dic['Type'] == 'Encrypt':
                res = self.decrypt(cipher_text=b64decode(dic['Message'].encode('utf8')),
                                   nonce=b64decode(dic['Nonce'].encode('utf8')),
                                   tag=b64decode(dic['Tag'].encode('utf8')))
                return res
        except Exception as e:
            print('Decryption Error')
            return None
