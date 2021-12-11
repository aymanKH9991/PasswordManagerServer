import asyncio
import json
import random
import socket as sk
import time
import Model.Model as model
import Messages.Respond


class Server:
    def __init__(self):
        self.__DB = model.DB()
        self.receive_buffer = 2048

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
        peer = writer.get_extra_info('peername')
        print(peer)
        i = 0
        try:
            while not writer.is_closing():
                data = await reader.read(self.receive_buffer)
                if not reader.at_eof():
                    results = self.handle_receive_message(data)
                    if results is not None:
                        for r in results:
                            writer.write(r)
                            await writer.drain()
                else:
                    break
            writer.close()
            await writer.wait_closed()
            print('Done' + peer[0])
        except RuntimeError as r:
            print("Error")
        except ConnectionError as c:
            print("Connection Issue\t", peer[0])

    def handle_receive_message(self, mes: bytes):
        msg_str = mes.decode('utf8')
        print(msg_str)
        try:
            msg_dict = json.loads(msg_str)
            if msg_dict['Type'] == 'Size':
                self.receive_buffer = int(msg_dict['Size'])
                return None
            elif msg_dict['Type'] == 'Empty':
                return None
            elif msg_dict['Type'] == 'NewUser':
                return self.__signup_handler(msg_dict=msg_dict)
            elif msg_dict['Type'] == 'OldUser':
                return self.__login_handler(msg_dict=msg_dict)
        except Exception as e:
            print('Error in receive Message', msg_str)

    def __signup_handler(self, msg_dict):
        res = self.__DB.insert_new_user(msg_dict['Name'], msg_dict['Password'], msg_dict['UniqueKey'])
        if res == 1:
            self.__DB.add_active_user(msg_dict['Name'], msg_dict['UniqueKey'])
            return [Messages.Respond.RespondMessage({'Type': 'Sign',
                                                     'Result': 'Done'
                                                     }).to_json_byte()]
        else:
            return [Messages.Respond.RespondMessage({'Type': 'Sign',
                                                     'Result': 'Error'
                                                     }).to_json_byte()]

    def __login_handler(self, msg_dict):
        query_res = self.__DB.check_user(msg_dict['Name'], msg_dict['UniqueKey'])
        if query_res[1]:
            if msg_dict['Password'] == query_res[0]['Password']:
                self.__DB.add_active_user(msg_dict['Name'], msg_dict['UniqueKey'])
                return [Messages.Respond.RespondMessage({'Type': 'Login',
                                                         'Result': 'Done'
                                                         }).to_json_byte()]
            else:
                return [Messages.Respond.RespondMessage({'Type': 'Login',
                                                         'Result': 'Error'
                                                         }).to_json_byte()]

    def __get_handler(self, msg_dict):
        print(msg_dict)

    def __put_handler(self, msg_dict):
        print(msg_dict)

    def __update_handler(self, msg_dict):
        print(msg_dict)

    def __delete_handler(self, msg_dict):
        print(msg_dict)
