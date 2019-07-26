import asyncio

from pypuss.app import Master

async def main():
    my_app = Master()
    await my_app.run()

if __name__ == '__main__':
    print("[debug]", "pypuss started running")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

