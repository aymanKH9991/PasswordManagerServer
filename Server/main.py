import asyncio
from controller import ServerController as sc
from Model import Manager

db_manager = Manager.DBManager()


async def main():
    task = await sc.Server(db_manager).handle()
    asyncio.create_task(task)


def exception_handler(loop: asyncio.AbstractEventLoop, dic: dict):
    db_manager.delete_active_user_col()
    pass


if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.set_exception_handler(exception_handler)
        loop.run_until_complete(main())
    except KeyboardInterrupt as e:
        db_manager.delete_active_user_col()
        print("Server Shout Down")
    except RuntimeError as e:
        print('End With Error')
