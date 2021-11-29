import asyncio
from Messages import Respond
from controller import ServerController as sc


async def main():
    task = await sc.Server().handle()
    asyncio.create_task(task)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt as e:
        print("Server Shout Down")
        pass
