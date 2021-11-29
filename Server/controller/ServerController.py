import asyncio
import socket as sk


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

    async def handle_conn(self, reader, writer):
        print(writer.get_extra_info('peername'))
        data = await reader.read(100)
        message = data.decode()
        print(message)
        writer.write('Hello, From Server\n\n'.encode(encoding='utf8'))
        await writer.drain()
        writer.close()
        print('Done')
