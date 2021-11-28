import asyncio


async def main():
    print('Hello,',end=' ')
    await asyncio.sleep(1)
    print('World From Client')


if __name__ == '__main__':
    asyncio.run(main())
