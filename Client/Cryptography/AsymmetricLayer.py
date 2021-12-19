from __future__ import annotations

import json
from base64 import b64encode, b64decode
from Crypto.Random import get_random_bytes
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
import Messages.Session as SMs


class AsymmetricLayer:
    def __init__(self):
        self.rsa_pair = RSA.generate(2048)
        self.__session_key = get_random_bytes(32)

    def encrypt_config(self, mes_dic):
        public_key = RSA.import_key(mes_dic['PublicKey'])
        pkcs = PKCS1_OAEP.new(public_key)
        enc_session_key = pkcs.encrypt(self.__session_key)
        return SMs.SessionMessage(session_key=b64encode(enc_session_key)
                                  .decode('utf-8')).to_json_byte()

    def get_session_key(self):
        return self.__session_key

    def get_private_key(self):
        """
            Return private as bytes
        """
        return self.rsa_pair.exportKey()

    def get_public_key(self):
        """
            Return public as bytes
        """
        return self.rsa_pair.publickey().exportKey()
