import asyncio
import socket as sk


class Client:
    def __init__(self, address='127.0.0.1', port='50050'):
        self.address = address
        self.port = port

    async def handle(self):
        try:
            self.re_sock, self.wr_sock = await asyncio.open_connection(self.address, self.port, family=sk.AF_INET)
            while not self.wr_sock.is_closing():
                self.wr_sock.write('Hello, Server From Client'.encode(encoding='utf8'))
                await self.wr_sock.drain()

                data = await self.re_sock.read(1024)
                msg = data.decode(encoding='utf8')
                if not self.re_sock.at_eof():
                    print(msg)
                    print(len(msg))
                else:
                    self.wr_sock.close()
                # self.wr_sock.close()
                # await self.wr_sock.wait_closed()
        except ConnectionRefusedError:
            print("No Server Respond")