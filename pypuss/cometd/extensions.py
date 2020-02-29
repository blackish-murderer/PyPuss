import aiocometd

import pypuss.utils as utils
import pypuss.constants as constants

class Adaptor(aiocometd.Extension):
    def __init__(self):
        aiocometd.Extension.__init__(self)
        self.__cookies = constants.AUTH_COOKIE

    async def incoming(self, payload, headers=None):
        utils.unescape(payload)

        response = None
        for message in payload:
            channel = message.get("channel")
            if channel == constants.ACCOUNT_GET_TARGET and "data" in message:
                is_blue = await utils.isblue(message["data"]["userUuid"])
                message["data"]["isBlue"] = is_blue
                response = message

        if response is None:
            return

        for message in payload:
            channel = message.get("channel")
            if channel == constants.ACCOUNT_GET_TARGET and "id" in message:
                message.update(response)

    async def outgoing(self, payload, headers):
        for message in payload:
            channel = message.get("channel")
            if channel == "/meta/handshake":
                self.__cookies = await utils.upgrade_cookies()
                message["ext"] = {"chatroomId": int(constants.CHATROOM_ID)}

        headers["Cookie"] = self.__cookies
