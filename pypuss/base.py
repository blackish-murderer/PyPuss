import pypuss.utils as utils
import pypuss.cometd as cometd
import pypuss.helpers as helpers
import pypuss.constants as constants

class Root():
    def __init__(self):
        self.client = cometd.Client()

        self.client.append_route(
                constants.ACCOUNT_GET_SELF,
                self._on_account_get_self)
        self.client.append_route(
                constants.ACCOUNT_GET_TARGET,
                self._on_account_get_target)
        self.client.append_route(
                constants.MODERATOR_ACCOUNT_BANNED,
                self._on_moderator_account_banned)
        self.client.append_route(
                constants.MODERATOR_ACCOUNT_UNBANNED,
                self._on_moderator_account_unbanned)
        self.client.append_route(
                constants.CHATROOM_MESSAGE_ADD,
                self._on_chatroom_message_add)
        self.client.append_route(
                constants.CHATROOM_MESSAGE_REMOVE,
                self._on_chatroom_message_remove)
        self.client.append_route(
                constants.CHATROOM_USER_JOINED,
                self._on_chatroom_user_joined)
        self.client.append_route(
                constants.CHATROOM_USER_LEFT,
                self._on_chatroom_user_left)
        self.client.append_route(
                constants.CONVERSATION_MESSAGE,
                self._on_conversation_message)

        self.last_pv = 0
        self.last_pb = 0

        self.users = {}
        self.texts = {}
        self.banned = {}
        self.myself = {}
        # self.friends = {}
        # self.ignored = {}
        # self.conversations = {}
        # self.notifications = {}

    async def run(self):
        await self.client.connect()
        await self.account_get_self()
        await self.client.listen()

    async def _on_account_get_self(self, data):
        _data = helpers.account_get_self(data)
        self.users = _data["users"]
        self.texts = _data["texts"]
        self.banned = _data["banned"]
        self.myself = _data["myself"]
        await self.on_account_get_self(_data)

    async def on_account_get_self(self, context):
        pass

    async def _on_account_get_target(self, data):
        return helpers.account_get_target(data)
        #await self.on_account_get_target(_data)

    async def on_account_get_target(self, user):
        pass

    async def _on_moderator_account_banned(self, data):
        _data = helpers.moderator_account_banned(data)
        if _data is None:
            return
        self.banned[_data["uuid"]] = _data
        await self.on_moderator_account_banned(_data)

    async def on_moderator_account_banned(self, user):
        pass

    async def _on_moderator_account_unbanned(self, data):
        _data = data # helpers.moderator_account_unbanned(data)
        if _data is None:
            return
        _data = self.banned.pop(_data, {})
        await self.on_moderator_account_unbanned(_data)

    async def on_moderator_account_unbanned(self, user):
        pass

    async def _on_chatroom_message_add(self, data):
        _data = helpers.chatroom_message_add(data)
        if _data is None:
            return
        self.texts[_data["uuid"]] = _data
        await self.on_chatroom_message_add(_data)

    async def on_chatroom_message_add(self, message):
        pass

    async def _on_chatroom_message_remove(self, data):
        _data = data # helpers.chatroom_message_remove(data)
        if _data is None:
            return
        _data = self.texts.pop(_data, {})
        await self.on_chatroom_message_remove(_data)

    async def on_chatroom_message_remove(self, message):
        pass

    async def _on_chatroom_user_joined(self, data):
        _data = helpers.chatroom_user_joined(data)
        if _data is None:
            return
        self.users[_data["uuid"]] = _data
        await self.on_chatroom_user_joined(_data)

    async def on_chatroom_user_joined(self, user):
        pass

    async def _on_chatroom_user_left(self, data):
        _data = data # helpers.chatroom_message_remove(data)
        if _data is None:
            return
        _data = self.users.pop(_data, {})
        await self.on_chatroom_user_left(_data)

    async def on_chatroom_user_left(self, user):
        pass

    async def _on_conversation_message(self, data):
        _data = helpers.conversation_message(data)
        await self.on_conversation_message(_data)

    async def on_conversation_message(self, message):
        pass

    async def account_get_self(self):
        return await self.client.publish(
                constants.ACCOUNT_GET_SELF, {})

    async def account_get_target(self, uuid):
        return await self.client.request(
                constants.ACCOUNT_GET_TARGET, { "accountId": uuid })

    async def moderator_ban_account(self, uuid):
        return await self.client.publish(
                constants.MODERATOR_BAN_ACCOUNT, { "accountId": uuid })

    async def moderator_unban_account(self, uuid):
        return await self.client.publish(
                constants.MODERATOR_UNBAN_ACCOUNT, { "accountId": uuid })

    async def chatroom_message(self, text):
        self.last_pb = await utils.wait_threshold(self.last_pb)
        return await self.client.publish(
                constants.CHATROOM_MESSAGE, { "messageBody": text })

    async def moderator_remove_messages(self, uuid):
        return await self.client.publish(
                constants.MODERATOR_REMOVE_MESSAGES, { "accountId": uuid })

    async def conversation_message(self, uuid, text):
        self.last_pv = await utils.wait_threshold(self.last_pv)
        return await self.client.publish(
                constants.CONVERSATION_MESSAGE,
                { "conversationUserUuid": uuid, "messageBody": text })
