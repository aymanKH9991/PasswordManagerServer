import asyncio
from Controller import ClientController as cc


async def main():
    task = asyncio.create_task(cc.Client().handle())
    await task


def exceptionHandler(loop: asyncio.AbstractEventLoop, dic: dict):
    pass


if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.set_exception_handler(exceptionHandler)
        loop.run_until_complete(main())
    except KeyboardInterrupt as e:
        print("Forced Closed")
