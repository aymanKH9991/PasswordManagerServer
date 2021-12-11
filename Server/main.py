import asyncio
from controller import ServerController as sc


async def main():
    task = await sc.Server().handle()
    asyncio.create_task(task)


def exception_handler(loop: asyncio.AbstractEventLoop, dic: dict):
    pass


if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.set_exception_handler(exception_handler)
        loop.run_until_complete(main())
    except KeyboardInterrupt as e:
        print("Server Shout Down")
    except RuntimeError as e:
        print('End With Error')
