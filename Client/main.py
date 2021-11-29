import asyncio
import Messages.NewUser as newUser
from Controller import ClientController as cc


async def main():
    # user_ms = newUser.NewUserMessage('Ayman Alkhawaleda', 'dummyPassword')
    # print(user_ms.to_json_string())
    task = asyncio.create_task(cc.Client().handle())
    await task


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Forced Closed")
