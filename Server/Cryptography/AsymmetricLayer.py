import base64

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from base64 import b64encode, b64decode


class AsymmetricLayer:
    def __init__(self, nbits=1024):
        self.rsa_pair = RSA.generate(nbits)

    def encrypt(self, plain_message):
        pass

    def decrypt(self, cipher_message):
        pass

    def decrypt_config(self, mes_dic: dict,private_key):
        try:
            session_key = b64decode(mes_dic['SessionKey'].encode('utf-8'))
            private_key = RSA.import_key(private_key)
            pkcs = PKCS1_OAEP.new(private_key)
            session_key = pkcs.decrypt(session_key)
            return session_key
        except Exception as e:
            return False
            print('Configuration Decrypt Error')
