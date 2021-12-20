from __future__ import annotations

import json
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Hash import SHA512
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Signature import pkcs1_15

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

    def enc_dict(self, dic: dict | bytes | str):
        try:
            res = self.encrypt(json.dumps(dic)) if type(dic) == dict else self.encrypt(dic)
            return Messages.Crypto.CryptoMessage(name='Server',
                                                 enc_message=b64encode(res[0]).decode('utf8'),
                                                 nonce=b64encode(res[1]).decode('utf8'),
                                                 tag=b64encode(res[2]).decode('utf8')).to_json_byte()
        except Exception as e:
            print('Encryption Error')
            return None

    def dec_dict(self, dic: bytes, public_key):
        try:
            dic = json.loads(dic)
            if dic['Type'] == 'Encrypt':
                res = self.decrypt(cipher_text=b64decode(dic['Message'].encode('utf8')),
                                   nonce=b64decode(dic['Nonce'].encode('utf8')),
                                   tag=b64decode(dic['Tag'].encode('utf8')))
            res1 = json.loads(res)
            if public_key is None:
                public_key = b64decode(res1['PublicKey'])
            else:
                public_key = b64decode(public_key)
            key = RSA.importKey(public_key)
            hash = SHA512.new(b64decode(dic['Message'].encode('utf8')))
            sign = b64decode(dic['Signature'].encode('utf8'))
            pkcs1_15.new(key).verify(hash, sign)
            return res

        except Exception as e:
            print('Decryption Error')
            return None
