from __future__ import annotations

import json
from base64 import b64encode, b64decode
from Crypto.Random import get_random_bytes
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
import Messages.Session as SMs
from Cryptography import SymmetricLayer


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

    def encrypt_put_dic(self, msg_dict, private_key: str):
        try:
            private_key = b64decode(private_key)
            sym = SymmetricLayer.SymmetricLayer(private_key[32:64])
            msg_dict = json.loads(msg_dict)
            enc_password = sym.encrypt_with_nonce(msg_dict['Password'], private_key[:32])
            enc_description = sym.encrypt_with_nonce(msg_dict['Description'], private_key[:32])
            msg_dict['Password'] = b64encode(enc_password).decode('utf8')
            msg_dict['Description'] = b64encode(enc_description).decode('utf8')
            for key,val in msg_dict['Files'].items():
                enc_filename = sym.encrypt_with_nonce(val['FileName'], private_key[:32])
                enc_file = sym.encrypt_with_nonce(val['File'], private_key[:32])
                msg_dict['Files'][key]['FileName'] = b64encode(enc_filename).decode('utf8')
                msg_dict['Files'][key]['File'] = b64encode(enc_file).decode('utf8')
            print(msg_dict)
            return msg_dict
        except Exception as e:
            print('Error in put encryption')

    def decrypt_put_dic(self, msg_dict, private_key):
        try:
            private_key = b64decode(private_key)
            sym = SymmetricLayer.SymmetricLayer(private_key[32:64])
            msg_dict = json.loads(msg_dict)
            dec_password = sym.decrypt_without_verify(b64decode(msg_dict['Password']), private_key[:32])
            dec_description = sym.decrypt_without_verify(b64decode(msg_dict['Description']), private_key[:32])
            msg_dict['Password'] = dec_password.decode('utf8')
            msg_dict['Description'] = dec_description.decode('utf8')
            for key,val in msg_dict['Files'].items():
                dec_filename = sym.decrypt_without_verify(b64decode(val['FileName']), private_key[:32])
                dec_file = sym.decrypt_without_verify(b64decode(val['File']), private_key[:32])
                msg_dict['Files'][key]['FileName'] = dec_filename.decode('utf8')
                msg_dict['Files'][key]['File'] = dec_file.decode('utf8')
            return msg_dict
        except Exception as e:
            print('Error in put decryption')
