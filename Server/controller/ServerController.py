import asyncio
import random
import socket as sk
import time


class Server:
    async def handle(self, address='127.0.0.1', port='50050'):
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
            while not writer.is_closing() and i <= 5:
                data = await reader.read(1024)
                message = data.decode()
                if not reader.at_eof():
                    # print(message)
                    writer.write(f'Hello, From Server {random.randint(0, time.time_ns())}'.encode(encoding='utf8'))
                    await writer.drain()
                    i += 1
                    await asyncio.sleep(2)
                else:
                    break
            writer.close()
            await writer.wait_closed()
            print('Done' + peer[0])
        except RuntimeError as r:
            print("Error")
        except ConnectionError as c:
            print("Connection Issue\t", peer[0])
