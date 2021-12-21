from __future__ import annotations

import json
from base64 import b64encode, b64decode

import Crypto.Hash.SHA512
from Crypto.Random import get_random_bytes
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
import Messages.Session as SMs
from Cryptography import SymmetricLayer
from Crypto.Signature import pkcs1_15


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
            for key, val in msg_dict['Files'].items():
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
            for key, val in msg_dict['Files'].items():
                dec_filename = sym.decrypt_without_verify(b64decode(val['FileName']), private_key[:32])
                dec_file = sym.decrypt_without_verify(b64decode(val['File']), private_key[:32])
                msg_dict['Files'][key]['FileName'] = dec_filename.decode('utf8')
                msg_dict['Files'][key]['File'] = dec_file.decode('utf8')
            return msg_dict
        except Exception as e:
            print('Error in put decryption')

    def encrypt_share(self, message, pk_dict, private_key):
        second_pk = pk_dict['PK']
        temp_dict = {
            "Type": '',
        }
        random_key = get_random_bytes(32)
        sym = SymmetricLayer.SymmetricLayer(random_key)
        enc_dic = sym.enc_dict(message, private_key=private_key)
        dic = json.loads(enc_dic)
        for key, val in dic.items():
            temp_dict[key] = val
        temp_dict['Type'] = 'ShareServer'
        temp_dict['SecondUser'] = json.loads(message)['SecondUser']
        pk_second_user = RSA.import_key(b64decode(second_pk))
        pkcs = PKCS1_OAEP.new(pk_second_user)
        enc_key = pkcs.encrypt(random_key)
        temp_dict['EncKey'] = b64encode(enc_key).decode('utf8')
        return temp_dict

    def decrypt_share(self, message, private_key, sender_pk, enc_key, nonce, tag, signature):
        # Every Parameter is Base64 Encoding
        try:
            private_key = RSA.import_key(b64decode(private_key))
            sender_pk = RSA.import_key(b64decode(sender_pk))
            pkcs = PKCS1_OAEP.new(private_key)
            enc_key = pkcs.decrypt(b64decode(enc_key))
            sym = SymmetricLayer.SymmetricLayer(enc_key)
            message = b64decode(message)

            # Check Sender Signature
            hash = Crypto.Hash.SHA512.new(message)
            sign = b64decode(signature)
            pkcs1_15.new(sender_pk).verify(hash, sign)

            # Decrypt and Check Message Mac
            nonce = b64decode(nonce)
            tag = b64decode(tag)
            dec_message = sym.decrypt(message, nonce, tag)
            return dec_message
        except ValueError as ve:
            print(ve, "In Share Message")
        except Exception as e:
            print('Error Decrypt Share')
