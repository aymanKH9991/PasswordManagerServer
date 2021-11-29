import asyncio
from Messages import Respond

async def main():
    respondMessage = Respond.RespondMessage("Connection Successfully")
    print(respondMessage.to_json_string())
    await asyncio.sleep(1)


if __name__ == '__main__':
    asyncio.run(main())
