import aiocometd

import pypuss.utils as utils
import pypuss.constants as constants

class Adaptor(aiocometd.Extension):
    async def incoming(self, payload, headers=None):
        utils.unescape(payload)

        for message in payload:
            if utils.ispublish(message):
                for _message in payload:
                    if utils.isresponse(_message):
                        message.update(_message)

    async def outgoing(self, payload, headers):
        for message in payload:
            if message.get("channel") == "/meta/handshake":
                message["ext"] = {"chatroomId": int(constants.CHATROOM_ID)}
                break

        if headers.get("Cookie") is None:
            headers["Cookie"] = constants.AUTH_COOKIE

