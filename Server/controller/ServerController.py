import asyncio
import json
import random
import socket as sk
import time
import Model.Model as model
import Messages.Respond


class Server:
    def __init__(self,db_manager):
        self.__DB = model.DB()
        db_manager.add_db(self.__DB)
        self.receive_buffer = 2048
        self.active_users = []

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
        print(self.peer)
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
            print('Done ' + self.peer[0])
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

    def handle_receive_message(self, mes: bytes):
        msg_str = mes.decode('utf8')
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
            elif msg_dict['Type'] == 'Put':
                return self.__put_handler(msg_dict=msg_dict)
            elif msg_dict['Type'] == 'Get':
                return self.__get_handler(msg_dict=msg_dict)
            elif msg_dict['Type'] == 'Update':
                return self.__update_handler(msg_dict=msg_dict)
            elif msg_dict['Type'] == 'Delete':
                return self.__delete_handler(msg_dict=msg_dict)
            else:
                return None

        except Exception as e:
            print(e)
            print('Error in receive Message', msg_str)

    def __signup_handler(self, msg_dict):
        res = self.__DB.insert_new_user(msg_dict['Name'], msg_dict['Password'], msg_dict['UniqueKey'])
        if res == 1:
            self.__DB.add_active_user(msg_dict['Name'], msg_dict['UniqueKey'], self.peer)
            return [Messages.Respond.RespondMessage({'Type': 'Sign',
                                                     'Result': 'Done'
                                                     }).to_json_byte()]
        else:
            return [Messages.Respond.RespondMessage({'Type': 'Sign',
                                                     'Result': 'Error In SignUp'
                                                     }).to_json_byte()]

    def __login_handler(self, msg_dict):
        query_res = self.__DB.check_user(msg_dict['Name'], msg_dict['UniqueKey'])
        if query_res[1]:
            if msg_dict['Password'] == query_res[0]['Password']:
                self.__DB.add_active_user(msg_dict['Name'], msg_dict['UniqueKey'], self.peer)
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
                                                              'Size': len(get_mes)
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
