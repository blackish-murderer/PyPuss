import aiocometd

import pypuss.utils as utils
import pypuss.constants as constants

import pypuss.cometd.extensions as extensions

class Client(aiocometd.Client):
    def __init__(self):
        aiocometd.Client.__init__(self,
                constants.COMETD_URL,
                extensions=[extensions.Adaptor()])
        self.__router = {}

    def append_route(self, channel, method):
        self.__router[channel] = method

    def remove_route(self, channel):
        return self.__router.pop(channel)

    async def connect(self):
        try:
            await self.open()
        except Exception as error:
            raise error

    async def listen(self):
        while True:
            try:
                message = await self.receive()
                await self._dispatch(message)
            except Exception as error:
                raise error

    async def request(self, channel, data):
        message = await self.publish(channel, data)
        return await self._dispatch(message)

    async def _dispatch(self, message):
        channel = message.get("channel")
        data = message.get("data")
        if (data is None or channel is None):
            print("[warning]", "message is empty for", channel)
            return
        method = self.__router.get(channel)
        if utils.isasync(method):
            return await method(data)
        if utils.issync(method):
            return method(data)
        # print("[warning]", "no method bound to" , channel)
        # print("[warning]", "attached data", data)
