from __future__ import annotations

import json
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA512
import Messages.Crypto


class SymmetricLayer:
    def __init__(self, key: bytes = None):
        if key is None:
            self.__KEY = get_random_bytes(32)
        else:
            self.__KEY = key

    def encrypt(self, plain_text: bytes | str):
        symmetric = AES.new(self.__KEY, AES.MODE_EAX)
        plain_text = plain_text if type(plain_text) == bytes else plain_text.encode('utf8')
        return [symmetric.encrypt(plaintext=plain_text), symmetric.nonce, symmetric.digest()]

    def decrypt(self, cipher_text: bytes | str, nonce: bytes, tag: bytes):
        symmetric = AES.new(self.__KEY, AES.MODE_EAX, nonce=nonce)
        cipher_text = cipher_text if type(cipher_text) == bytes else cipher_text.encode('utf8')
        return symmetric.decrypt_and_verify(cipher_text, tag)

    def encrypt_with_nonce(self, plain_text: bytes | str, nonce: bytes):
        symmetric = AES.new(self.__KEY, AES.MODE_EAX, nonce=nonce)
        plain_text = plain_text if type(plain_text) == bytes else plain_text.encode('utf8')
        return symmetric.encrypt(plaintext=plain_text)

    def decrypt_without_verify(self, cipher_text: bytes | str, nonce: bytes):
        symmetric = AES.new(self.__KEY, AES.MODE_EAX, nonce=nonce)
        cipher_text = cipher_text if type(cipher_text) == bytes else cipher_text.encode('utf8')
        return symmetric.decrypt(cipher_text)

    def enc_dict(self, dic: dict | bytes | str, private_key):
        try:
            res = self.encrypt(json.dumps(dic)) if type(dic) == dict else self.encrypt(dic)
            name = dic['Name'] if type(dic) is dict else json.loads(dic)['Name']
            message = res[0]
            key = RSA.import_key(b64decode(private_key))
            sign = PKCS1_v1_5.new(key).sign(SHA512.new(message))
            return Messages.Crypto.CryptoMessage(name=name,
                                                 enc_message=b64encode(res[0]).decode('utf8'),
                                                 nonce=b64encode(res[1]).decode('utf8'),
                                                 tag=b64encode(res[2]).decode('utf8'),
                                                 signature=b64encode(sign).decode('utf8')).to_json_byte()
        except Exception as e:
            print(e)
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
