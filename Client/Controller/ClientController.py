import asyncio
import json
import socket as sk
from Controller import InputController as Ic


class Client:
    def __init__(self, address='127.0.0.1', port='50050'):
        self.address = address
        self.port = port
        self.input = Ic.CMDInput()
        self.receive_buffer = 2048

    async def handle(self):
        try:
            self.re_sock, self.wr_sock = await asyncio.open_connection(self.address, self.port, family=sk.AF_INET)
            while not self.wr_sock.is_closing():
                mes = self.handle_sending_message()
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
                    self.handle_receive_message(data)
                else:
                    self.wr_sock.close()
        except ConnectionRefusedError:
            print("No Server Respond")

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
            return [bytes(json.dumps(mes1))]
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

    def handle_receive_message(self, msg: bytes):
        msg_str = msg.decode('utf8')
        # print(msg_str)
        try:
            mes_dict = json.loads(msg_str)
            if mes_dict['Type'] == 'Respond':
                if type(mes_dict['Details']) == str:
                    print(mes_dict['Details'])
                elif type(mes_dict) == dict:
                    sub_dict = mes_dict['Details']
                    print(sub_dict)
            elif mes_dict['Type'] == 'Size':
                self.receive_buffer = mes_dict['Size']
        except Exception as e:
            print('Error in Receive Message')
