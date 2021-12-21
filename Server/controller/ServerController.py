import asyncio
import json
import random
import socket as sk
import time
from base64 import b64decode

from Crypto.Hash import SHA512
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

import Model.Model as model
import Messages.Respond
import Messages.Configration
from Cryptography import SymmetricLayer as sl
from Cryptography import AsymmetricLayer as asl


class Server:
    def __init__(self, db_manager):
        self.__DB = model.DB()
        db_manager.add_db(self.__DB)
        self.receive_buffer = 2048
        self.asl = asl.AsymmetricLayer()

    async def handle(self, address='127.0.0.1', port='50050'):
        print(self.__DB.get_db_name())
        self.main_sock = await asyncio.start_server(self.handle_conn, address, port, family=sk.AF_INET)
        try:
            async with self.main_sock:
                await self.main_sock.serve_forever()
        except Exception as e:
            await self.main_sock.wait_closed()
            self.main_sock.close()
            pass

    async def handle_conn(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.peer = writer.get_extra_info('peername')
        try:
            # Send Public Key To User
            if await self.init_authentication(reader, writer):
                # Send And Receive Processes
                while not writer.is_closing():
                    data = await reader.read(self.receive_buffer)
                    if not reader.at_eof():
                        # Comment's Lines Below are for Symmetric Encryption and Decryption
                        results = self.symmetric_send_encrypt(
                            self.handle_receive_message(
                                self.symmetric_receive_decrypt(data)))
                        # results = self.handle_receive_message(data)
                        if results is not None:
                            for r in results:
                                writer.write(r)
                                await writer.drain()
                    else:
                        break
                writer.close()
                await writer.wait_closed()
        except RuntimeError as r:
            usersItr = self.__DB.get_user_by_peer(writer.get_extra_info('peername'))
            for user in usersItr:
                self.__DB.remove_active_user(user['Name'], user['PublicKey'])
            print("Error")
        except ConnectionError as c:
            usersItr = self.__DB.get_user_by_peer(writer.get_extra_info('peername'))
            for user in usersItr:
                self.__DB.remove_active_user(user['Name'], user['PublicKey'])
            print("Connection Issue\t", self.peer[0])

    async def init_authentication(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        try:
            writer.write(Messages.Configration.ConfigMessage(
                public_key=self.asl.rsa_pair.public_key()
                    .export_key().decode('utf8'))
                         .to_json_byte())
            await writer.drain()
            data = await reader.read(self.receive_buffer)
            mes_dic = json.loads(data)
            if mes_dic['Type'] == 'Session':
                self.session_key = self.asl.decrypt_config(mes_dic)
                if self.session_key is not False:
                    writer.write(Messages.Respond.RespondMessage(details={
                        'Type': 'Config',
                        'Result': 'Done'
                    }).to_json_byte())
                    await writer.drain()
                    return True
                else:
                    writer.write(Messages.Respond.RespondMessage(details={
                        'Type': 'Config',
                        'Result': 'Error'
                    }).to_json_byte())
                    await writer.drain()
                    return False
        except Exception as e:
            print('Init Authentication Error')

    def handle_receive_message(self, mes: bytes):
        msg_str = mes.decode('utf8')
        try:
            msg_dict = json.loads(msg_str)
            if msg_dict['Type'] == 'Size':
                self.receive_buffer = int(msg_dict['Size'])
                return None
            elif msg_dict['Type'] == 'Empty':
                return [Messages.Respond.RespondMessage({'Type': 'Empty'}).to_json_byte()]
            elif msg_dict['Type'] == 'NewUser':
                return self.__signup_handler(msg_dict=msg_dict)
            elif msg_dict['Type'] == 'OldUser':
                return self.__login_handler(msg_dict=msg_dict)
            elif msg_dict['Type'] == 'Put':
                return self.__put_handler(msg_dict=msg_dict)
            elif msg_dict['Type'] == 'Get':
                return self.__get_handler(msg_dict=msg_dict)
            elif msg_dict['Type'] == 'Update':
                return self.__update_handler(msg_dict=msg_dict)
            elif msg_dict['Type'] == 'Delete':
                return self.__delete_handler(msg_dict=msg_dict)
            elif msg_dict['Type'] == 'ShareServer':
                return self.__share_handler(msg_dict=msg_dict)
            elif msg_dict['Type'] == 'GetUserPK':
                return self.__get_user_PK_handler(msg_dict=msg_dict)
            elif msg_dict['Type'] == 'GetShareMes':
                return self.__get_share_message_handler(msg_dict=msg_dict)
            elif msg_dict['Type'] == 'Put-Delete':
                return self.__put_delete_handler(msg_dict=msg_dict)
            else:
                return None

        except Exception as e:
            print(e)
            print('Error in receive Message', msg_str)

    def __signup_handler(self, msg_dict):
        res = self.__DB.insert_new_user(msg_dict['Name'], msg_dict['Password'], msg_dict['PublicKey'])
        if res == 1:
            self.__DB.add_active_user(msg_dict['Name'], msg_dict['PublicKey'], self.peer)
            return [Messages.Respond.RespondMessage({'Type': 'Sign',
                                                     'Result': 'Done'
                                                     }).to_json_byte()]
        else:
            return [Messages.Respond.RespondMessage({'Type': 'Sign',
                                                     'Result': 'Error In SignUp'
                                                     }).to_json_byte()]

    def __login_handler(self, msg_dict):
        query_res = self.__DB.check_user(msg_dict['Name'], msg_dict['PublicKey'])
        if query_res[1]:
            hash_pass = SHA512.new(msg_dict['Password'].encode('utf8')).hexdigest()
            user = query_res[0]
            if hash_pass == user['Password']:
                self.__DB.add_active_user(msg_dict['Name'], msg_dict['PublicKey'], self.peer)
                return [Messages.Respond.RespondMessage({'Type': 'Login',
                                                         'Result': 'Done'
                                                         }).to_json_byte()]
            else:
                return [Messages.Respond.RespondMessage({'Type': 'Login',
                                                         'Result': 'Error In Login'
                                                         }).to_json_byte()]

    def __get_handler(self, msg_dict):
        res = self.__DB.get_element_by_title(msg_dict['Name'], msg_dict['Title'])
        if res is not None:
            finalList = []
            if res.count() == 0:
                finalList.append(Messages.Respond.RespondMessage({'Type': 'Get',
                                                                  'Result': 'Error In Get'
                                                                  }).to_json_byte())
                return finalList
            else:
                temp_list = []
                for r in res:
                    get_mes = json.dumps({'Title': r['Title'],
                                          'Name': r['Name'],
                                          'Password': r['Password'],
                                          'Description': r['Description'],
                                          'Files': r['Files']
                                          })
                    temp_list.append(get_mes)
            get_mes = Messages.Respond.RespondMessage({'Type': 'Get', 'Result': temp_list}).to_json_byte()
            finalList.append(Messages.Respond.RespondMessage({'Type': 'Get',
                                                              'Result': 'Done',
                                                              'Size': 10 * len(get_mes)
                                                              }).to_json_byte())
            finalList.append(get_mes)

            return finalList

    def __put_handler(self, msg_dict):
        res = self.__DB.add_element(username=msg_dict['Name'],
                                    title=msg_dict['Title'],
                                    description=msg_dict['Description'],
                                    password=msg_dict['Password'],
                                    files=msg_dict['Files'])
        self.receive_buffer = 2048
        if res == 1:
            return [Messages.Respond.RespondMessage({'Type': 'Put',
                                                     'Result': 'Done'
                                                     }).to_json_byte()]
        else:
            return [Messages.Respond.RespondMessage({'Type': 'Put',
                                                     'Result': 'Error In Put Data'
                                                     }).to_json_byte()]

    def __update_handler(self, msg_dict):
        res = self.__DB.update_element(msg_dict['Name'], msg_dict['OldTitle'], msg_dict['Title'],
                                       msg_dict['Password'], msg_dict['Description'], msg_dict['Files'])
        self.receive_buffer = 2048
        if res == 1:
            return [Messages.Respond.RespondMessage({'Type': 'Update',
                                                     'Result': 'Update Done'}).to_json_byte()]
        else:
            return [Messages.Respond.RespondMessage({'Type': 'Update', 'Result': 'Error In Update'}).to_json_byte()]

    def __delete_handler(self, msg_dict):
        res = self.__DB.delete_element(msg_dict['Name'], msg_dict['Title'])
        if res == 1:
            return [Messages.Respond.RespondMessage({'Type': 'Delete', 'Result': 'Delete Done'}).to_json_byte()]
        else:
            return [Messages.Respond.RespondMessage({'Type': 'Delete', 'Result': 'Error In Delete'}).to_json_byte()]

    def __share_handler(self, msg_dict):
        res = self.__DB.add_share_message(msg_dict)
        if res:
            return [Messages.Respond.RespondMessage({'Type': 'ShareRespond', 'Result': 'Done'}).to_json_byte()]
        else:
            return [Messages.Respond.RespondMessage(
                {'Type': 'ShareRespond', 'Result': 'Error In Put Share Message'}).to_json_byte()]

    def __get_user_PK_handler(self, msg_dict):
        pk = self.__DB.get_user_publicKey(msg_dict['SecondUser'])
        if pk is not None:
            return [Messages.Respond.RespondMessage({'Type': 'PK', 'PK': pk}).to_json_byte()]
        else:
            return [Messages.Respond.RespondMessage({'Type': 'PK', 'PK': 'Error'}).to_json_byte()]

    def __get_share_message_handler(self, msg_dict):
        res = self.__DB.get_share_messages(msg_dict['Name'])
        if res is None:
            return [Messages.Respond.RespondMessage(
                {'Type': 'GetShareMesSize', 'Result': 'No Share Message To Show'}).to_json_byte()]
        else:
            share_mes = Messages.Respond.RespondMessage(
                {'Type': 'GetShareMes', 'Result': [json.dumps({
                    'Sender': r['Name'],
                    'SenderPK': self.__DB.get_user_publicKey(r['Name']),
                    'Message': r['Message'],
                    'Nonce': r['Nonce'],
                    'Tag': r['Tag'],
                    'Signature': r['Signature'],
                    'EncKey': r['EncKey']
                }) for r in res]}).to_json_byte()
            siz_mes = Messages.Respond.RespondMessage({'Type': 'GetShareMesSize',
                                                       "Result": len(res),
                                                       "Size": 10 * len(share_mes)
                                                       }).to_json_byte()
            return [siz_mes, share_mes]

    def __put_delete_handler(self, msg_dict):
        self.__DB.add_element(username=msg_dict['Name'], title=msg_dict['Title'], description=msg_dict['Description'],
                              password=msg_dict['Password'], files=msg_dict['Files'])
        res = self.__DB.delete_share_message(msg_dict['Name'], msg_dict['Tag'])
        if res:
            return [Messages.Respond.RespondMessage({'Type': 'Put', 'Result': 'Done'}).to_json_byte()]
        else:
            return [Messages.Respond.RespondMessage({'Type': 'Put', 'Result': 'Error In Put-Delete'}).to_json_byte()]

    def symmetric_receive_decrypt(self, data: bytes):
        try:
            temp_dict = json.loads(data)
            public_key = self.__DB.get_user_publicKey(temp_dict['Name'])
            dec_dic = sl.SymmetricLayer(key=self.session_key).dec_dict(data, public_key)
            self.__DB.add_event(temp_dict)
            return dec_dic
        except Exception as e:
            print(e)
            print('Symmetric Receive Decrypt Error')

    def symmetric_send_encrypt(self, data):
        if data is None:
            return None
        else:
            enc_list = []
            sym_enc = sl.SymmetricLayer(key=self.session_key)
            for d in data:
                enc_list.append(sym_enc.enc_dict(d))
            return enc_list
