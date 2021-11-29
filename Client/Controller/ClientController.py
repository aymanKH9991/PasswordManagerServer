import asyncio
import socket as sk


class Client:
    def __init__(self, address='127.0.0.1', port='50050'):
        self.address = address
        self.port = port

    async def handle(self):
        self.re_sock, self.wr_sock = await asyncio.open_connection(self.address, self.port, family=sk.AF_INET)

        self.wr_sock.write('Hello, Server From Client'.encode(encoding='utf8'))
        await self.wr_sock.drain()

        data = await self.re_sock.read(100)
        print(data.decode(encoding='utf8'))
        self.wr_sock.close()
