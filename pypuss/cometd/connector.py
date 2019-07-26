import aiocometd

import pypuss.utils as utils
import pypuss.constants as constants

import pypuss.cometd.extentions as extentions

class Client():
    def __init__(self):
        self.__client = aiocometd.Client(constants.COMETD_URL, connection_types=constants.LONG_POLLING, extensions=[extentions.Adaptor()])
        self.__router = {}

    def add_route(self, channel, method):
        self.__router[channel] = method

    def remove_route(self, channel):
        method = self.__router.pop(channel)

    async def open(self):
        await self.__client.open()

    async def close(self):
        await self.__client.close()

    async def connect(self):
        try:
            await self.__client.open()
            #await self._initiate()
        except Exception as error:
            await self.__client.close()
            raise

    async def receive(self):
        while True:
            try:
                message = await self.__client.receive()
                await self._dispatch(message.get("channel"), message.get("data"))
            except Exception as error:
                print(error)
                break

    async def publish(self, channel, data={}):
        message = await self.__client.publish(channel, data)
        channel = message.get("channel")
        data = message.get("data")
        skip = True
        return await self._dispatch(channel, data, skip)

    async def _dispatch(self, channel, data, skip=False):
        if (channel is None or data is None):
            return
        method = self.__router.get(channel)
        if utils.isasync(method):
            _data = await method(data, skip)
        elif utils.issync(method):
            _data = method(data, skip)
        if skip:
            return _data

