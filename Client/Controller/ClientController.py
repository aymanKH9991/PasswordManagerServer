import asyncio
import base64
import json
import socket as sk
import sys

import Crypto.Random
from Crypto.PublicKey import RSA

from Controller import InputController as Ic
from Model import Model as model
from Cryptography import SymmetricLayer as sl
from Cryptography import AsymmetricLayer as asl


class Client:
    def __init__(self, address='127.0.0.1', port='50050'):
        self.share_messages = []
        self.address = address
        self.port = port
        self.receive_buffer = 2048
        self.__DB = model.DB()
        self.asl = asl.AsymmetricLayer()
        self.input = Ic.CMDInput(self.asl.get_public_key())
        self.__shareMessage = False
        self.__bring_share_message = True

    async def handle(self):
        try:
            self.re_sock, self.wr_sock = await asyncio.open_connection(self.address, self.port, family=sk.AF_INET)
            conf = await self.config_message_handler()
            if conf:
                while not self.wr_sock.is_closing():
                    mes = self.symmetric_encryption_handler(self.handle_sending_message())
                    # mes = self.handle_sending_message()
                    for m in mes:
                        self.wr_sock.write(m)
                        await self.wr_sock.drain()
                    data = await self.re_sock.read(self.receive_buffer)
                    if not self.re_sock.at_eof():
                        await self.handle_receive_message(self.symmetric_decrypt_handler(data))
                        # await self.handle_receive_message(data)
                    else:
                        self.wr_sock.close()
            else:
                self.wr_sock.close()
        except ConnectionRefusedError:
            print("No Server Respond")
        except ConnectionResetError:
            print("Server Down")

    async def config_message_handler(self):
        try:
            data = await self.re_sock.read(4096)
            js_dic = json.loads(data)
            if js_dic['Type'] == 'Config':
                session_mes = self.asl.encrypt_config(js_dic)
                self.wr_sock.write(session_mes)
                await self.wr_sock.drain()
                data = await self.re_sock.read(1024)
                js_dic = json.loads(data)
                if js_dic['Type'] == 'Respond':
                    if js_dic['Details']['Result'] == 'Done':
                        return True
                    else:
                        raise Exception(js_dic['Details']['Result'])
        except Exception as e:
            print(e)
            print('Configuration Handler Error')
            return False

    def handle_sending_message(self):
        if not self.__shareMessage:
            if self.input.user_name is None:
                self.input.init_input_ui()
            elif self.__bring_share_message:
                self.input.last_message = json.dumps({
                    "Type": "GetShareMes",
                    "Name": self.input.user_name
                })
                self.__bring_share_message = False
            else:
                self.input.operations_ui()

        mes = json.loads(self.input.last_message) \
            if type(self.input.last_message) is str \
            else self.input.last_message
        if mes['Type'] == 'Error':
            print(mes['Description'])
            mes1 = {
                "Type": "Empty",
                "Name": self.input.user_name,
                "Description": "No Action"
            }
            return [bytes(json.dumps(mes1), 'utf8')]
        elif mes['Type'] in ('Put', 'Update', 'Put-Delete'):
            if mes['Type'] == 'Put-Delete':
                self.share_messages = self.input.share_messages
            pr_key = self.__DB.get_private_key(self.input.user_name)
            asy_dic = self.asl.encrypt_put_dic(self.input.last_message, pr_key)
            asy_dic = json.dumps(asy_dic)
            mes_b = bytes(asy_dic, 'utf8')
            mes_len = len(mes_b)
            mes1 = {
                "Type": "Size",
                "Name": self.input.user_name,
                "Size": 10 * mes_len
            }
            return [bytes(json.dumps(mes1), 'utf8'), mes_b]
        elif mes['Type'] == 'Share':
            dic = {
                "Type": 'GetUserPK',
                "Name": self.input.user_name,
                "SecondUser": mes['SecondUser']
            }
            return [bytes(json.dumps(dic), 'utf8')]
        elif mes['Type'] == 'ShareServer':
            mes_b = json.dumps(mes)
            mes_len = len(mes_b)
            mes1 = {
                "Type": "Size",
                "Name": self.input.user_name,
                "Size": 10 * mes_len
            }
            self.__shareMessage = False
            return [bytes(json.dumps(mes1), 'utf8'), bytes(mes_b, 'utf8')]
        else:
            return [bytes(self.input.last_message, 'utf8')]

    async def handle_receive_message(self, msg: bytes):
        msg_str = msg.decode('utf8')
        try:
            mes_dict = json.loads(msg_str)
            if mes_dict['Type'] == 'Respond':
                if type(mes_dict['Details']) == str:
                    print(mes_dict['Details'])
                elif type(mes_dict) == dict:
                    sub_dict = mes_dict['Details']
                    if sub_dict['Type'] == 'Sign':
                        self.signup_handler(sub_dict)
                    if sub_dict['Type'] == 'Login':
                        self.login_handler(sub_dict)
                    if sub_dict['Type'] == 'Put':
                        self.put_handler(sub_dict)
                    if sub_dict['Type'] == 'Get':
                        await self.get_handler(sub_dict)
                    if sub_dict['Type'] == 'Delete':
                        self.delete_handler(sub_dict)
                    if sub_dict['Type'] == 'Update':
                        self.update_handler(sub_dict)
                    if sub_dict['Type'] == 'PK':
                        self.share_handler(sub_dict)
                    if sub_dict['Type'] == 'ShareRespond':
                        self.share_respond(sub_dict)
                    if sub_dict['Type'] == 'GetShareMesSize':
                        await self.get_share_size_handler(sub_dict)
        except Exception as e:
            print(e)
            print('Error in Receive Message')

    def signup_handler(self, mes_dict):
        if mes_dict['Result'] == 'Done':
            in_dict = json.loads(self.input.last_message)
            self.__DB.insert_new_user(name=in_dict['Name'],
                                      public_key=in_dict['PublicKey'],
                                      private_key=base64.b64encode(self.asl.get_private_key()).decode('utf8'))
            print('SignUp Done')
        else:
            sys.exit(mes_dict['Result'])

    def login_handler(self, mes_dict):
        if mes_dict['Result'] == 'Done':
            print('You Logged in With User Name: ', self.input.user_name)
        else:
            sys.exit(mes_dict['Result'])

    async def get_handler(self, mes_dict):
        if mes_dict['Result'] == 'Done':
            buf = int(mes_dict['Size'])
            try:
                data = await self.re_sock.read(buf)
                data = self.symmetric_decrypt_handler(data)
                mes_dict = json.loads(data)
                pr_key = self.__DB.get_private_key(self.input.user_name)
                for i, r in enumerate(mes_dict['Details']['Result']):
                    print('<<<' + str(i + 1) + '>>>')
                    asy_dic = self.asl.decrypt_put_dic(r, pr_key)
                    for key, val in asy_dic.items():
                        print(key, ':', val)
            except Exception as e:
                print(e)
                print('Error In Get')
        else:
            print(mes_dict['Type'], ':', mes_dict['Result'])

    def share_handler(self, mes_dict):
        """
            After Getting The Second User Public key, we will encrypt the share data with symmetric encryption
            and sign it with Client private Key and Encrypt the symmetric key, the message are ready to send
            to the server to put it in server share tables and only Second User can encrypt it.
        """
        try:
            private_key = self.__DB.get_private_key(self.input.user_name)
            self.input.last_message = self.asl.encrypt_share(message=self.input.last_message,
                                                             pk_dict=mes_dict,
                                                             private_key=private_key)
            self.__shareMessage = True
        except Exception as e:
            print(e)

    async def get_share_size_handler(self, mes_dict):
        print('Share Messages: ', mes_dict['Result'])
        if type(mes_dict['Result']) == int:
            data = await self.re_sock.read(mes_dict['Size'])
            data = self.symmetric_decrypt_handler(data)
            respond_dict = json.loads(data)
            enc_share_messages = respond_dict['Details']['Result']
            try:
                for m in enc_share_messages:
                    m = json.loads(m)
                    private_key = self.__DB.get_private_key(self.input.user_name)
                    dec_mes_tag = self.asl.decrypt_share(message=m['Message'], private_key=private_key,
                                                         sender_pk=m['SenderPK'], enc_key=m['EncKey'], nonce=m['Nonce'],
                                                         tag=m['Tag'], signature=m['Signature'])
                    self.share_messages.append(dec_mes_tag)
                self.input.share_messages = [[json.loads(x[0]), x[1]] for x in self.share_messages]
            except Exception as e:
                print(e)

    def put_handler(self, mes_dict):
        print(mes_dict['Type'], ':', mes_dict['Result'])

    def delete_handler(self, mes_dict):
        print(mes_dict['Type'], ':', mes_dict['Result'])

    def update_handler(self, mes_dict):
        print(mes_dict['Type'], ':', mes_dict['Result'])

    def share_respond(self, mes_dict):
        print(mes_dict['Type'], ':', mes_dict['Result'])

    def symmetric_encryption_handler(self, message_list: list):
        try:
            crypto_messages = []
            private_key = self.__DB.get_private_key(self.input.user_name)
            if private_key is None:
                private_key = base64.b64encode(self.asl.get_private_key())
            for m in message_list:
                crypto_messages.append(sl.SymmetricLayer(
                    self.asl.get_session_key()
                ).enc_dict(m, private_key))
            return crypto_messages
        except Exception as e:
            print('Symmetric Handler')

    def symmetric_decrypt_handler(self, data):
        try:
            return sl.SymmetricLayer(
                self.asl.get_session_key()
            ).dec_dict(data)
        except Exception as e:
            print(e)
            print('Symmetric Decrypt Handler')
            return None
