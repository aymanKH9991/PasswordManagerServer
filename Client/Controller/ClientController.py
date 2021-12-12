import asyncio
import json
import socket as sk
import sys

from Controller import InputController as Ic
from Model import Model as model
from Cryptography import SymmetricLayer as sr


class Client:
    def __init__(self, address='127.0.0.1', port='50050'):
        self.address = address
        self.port = port
        self.input = Ic.CMDInput()
        self.receive_buffer = 2048
        self.__DB = model.DB()

    async def handle(self):
        try:
            self.re_sock, self.wr_sock = await asyncio.open_connection(self.address, self.port, family=sk.AF_INET)
            while not self.wr_sock.is_closing():
                mes = self.symmetric_encryption_handler(self.handle_sending_message())
                if len(mes) == 1:
                    self.wr_sock.write(mes[0])
                    await self.wr_sock.drain()
                elif len(mes) == 2:
                    self.wr_sock.write(mes[0])
                    await self.wr_sock.drain()
                    self.wr_sock.write(mes[1])
                    await self.wr_sock.drain()
                data = await self.re_sock.read(self.receive_buffer)
                if not self.re_sock.at_eof():
                    await self.handle_receive_message(data)
                else:
                    self.wr_sock.close()
        except ConnectionRefusedError:
            print("No Server Respond")
        except ConnectionResetError:
            print("Server Down")

    def handle_sending_message(self):
        if self.input.user_name is None:
            self.input.init_input_ui()
        else:
            self.input.operations_ui()

        mes = json.loads(self.input.last_message) \
            if type(self.input.last_message) is str \
            else self.input.last_message
        if mes['Type'] == 'Error':
            print(mes['Description'])
            mes1 = {
                "Type": "Empty",
                "Description": "No Action"
            }
            return [bytes(json.dumps(mes1), 'utf8')]
        elif mes['Type'] in ('Put', 'Update'):
            mes_b = bytes(self.input.last_message, 'utf8')
            mes_len = len(mes_b)
            mes1 = {
                "Type": "Size",
                "Size": mes_len
            }
            return [bytes(json.dumps(mes1), 'utf8'), mes_b]
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
        except Exception as e:
            print('Error in Receive Message')

    def signup_handler(self, mes_dict):
        if mes_dict['Result'] == 'Done':
            in_dict = json.loads(self.input.last_message)
            self.__DB.insert_new_user(in_dict['Name'], in_dict['UniqueKey'])
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
                mes_dict = json.loads(data)
                for i, r in enumerate(mes_dict['Details']['Result']):
                    print('<<<' + str(i + 1) + '>>>')
                    for key, val in json.loads(r).items():
                        print(key, ':', val)
            except Exception as e:
                print(e)
                print('Error In Get')
        else:
            print(mes_dict['Type'], ':', mes_dict['Result'])

    def put_handler(self, mes_dict):
        print(mes_dict['Type'], ':', mes_dict['Result'])

    def delete_handler(self, mes_dict):
        print(mes_dict['Type'], ':', mes_dict['Result'])

    def update_handler(self, mes_dict):
        print(mes_dict['Type'], ':', mes_dict['Result'])

    def symmetric_encryption_handler(self, message_list: list):
        try:
            crypto_messages = []
            for m in message_list:
                js_mes = json.loads(m)
                if js_mes['Type'] in ['NewUser', 'OldUser']:
                    self.sym_layer = sr.SymmetricLayer(js_mes['Password'].encode('utf8'))
                    crypto_messages.append(m)
                else:
                    crypto_messages.append(self.sym_layer.enc_dict(m))
            return crypto_messages
        except Exception as e:
            print('Symmetric Handler')
