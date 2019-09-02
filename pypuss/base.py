import pypuss.utils as utils
import pypuss.cometd as cometd
import pypuss.constants as constants

class Root():
    def __init__(self):
        self.client = cometd.Client()
        self.client.add_route(constants.CONTEXT_SELF, self._on_self_context)
        self.storage = {}
        self.tickers = []
        self.last_pv = 0
        self.last_pb = 0

    def _add_routes(self):
        chatroom_id = str(self.storage["chatroomContext"]["data"]["chatroom"]["id"])
        self.client.add_route(constants.ADD_USER + chatroom_id, self._on_user_add)
        self.client.add_route(constants.REMOVE_USER + chatroom_id, self._on_user_remove)
        self.client.add_route(constants.ADD_TEXT + chatroom_id, self._on_text_add)
        self.client.add_route(constants.REMOVE_TEXT + chatroom_id, self._on_text_remove)
        self.client.add_route(constants.ADD_FRIEND, self._on_friend_add)
        self.client.add_route(constants.REMOVE_FRIEND, self._on_friend_remove)
        self.client.add_route(constants.ADD_IGNORED, self._on_ignored_add)
        self.client.add_route(constants.REMOVE_IGNORED, self._on_ignored_remove)
        self.client.add_route(constants.ADD_BAN, self._on_ban_add)
        self.client.add_route(constants.REMOVE_BAN, self._on_ban_remove)
        self.client.add_route(constants.ADD_PV, self._on_pv_add)
        self.client.add_route(constants.OPEN_PV, self._on_pv_open)
        self.client.add_route(constants.CLOSE_PV, self._on_pv_close)
        self.client.add_route(constants.ADD_NOTICE, self._on_notice_add)
        self.client.add_route(constants.REMOVE_NOTICE, self._on_notice_remove)
        self.client.add_route(constants.CONTEXT_USER, self._on_user_context)
        for friend in self.storage["friends"]:
            self.client.add_route(constants.UPDATE_FRIEND + friend["userUuid"], self._on_friend_update)
        for conversation in self.storage["conversations"]:
            self.client.add_route(constants.UPDATE_PV + conversation["otherUser"]["userUuid"], self._on_pv_update)

    async def run(self):
        await self.client.connect()
        await self.context_self()
        await self.client.receive()

    async def _on_self_context(self, data, skip):
        uuid, name, is_guest, is_online, is_deleted = utils.extract_self(data)
        if skip:
            return data
        self.storage = data
        self._add_routes()
        return await self.on_self_context(uuid, name, is_guest, is_online, is_deleted)

    async def on_self_context(self, uuid, name, is_guest, is_online, is_deleted):
        print("[debug]", "on_self_context")
        print(uuid, name, is_guest, is_online, is_deleted)
        pass

    async def _on_ignored_add(self, data, skip):
        uuid, name, is_guest, is_online, is_deleted = utils.extract_user(data)
        if skip:
            return uuid, name, is_guest, is_online, is_deleted
        utils.append_to(self.storage["ignored"], data)
        return await self.on_ignored_add(uuid, name, is_guest, is_online, is_deleted)

    async def on_ignored_add(self, uuid, name, is_guest, is_online, is_deleted):
        print("[debug]", "on_ignore_add")
        print(uuid, name, is_guest, is_online, is_deleted)
        pass

    async def _on_ignored_remove(self, data, skip):
        uuid = utils.extract_uuid(data)
        if skip:
            return uuid
        utils.remove_from(self.storage["ignored"], "userUuid", data)
        return await self.on_ignored_remove(uuid)

    async def on_ignored_remove(self, uuid):
        print("[debug]", "on_ignore_remove")
        print(uuid)
        pass

    async def _on_friend_add(self, data, skip):
        uuid, name, is_guest, is_online, is_deleted = utils.extract_user(data)
        if skip:
            return uuid, name, is_guest, is_online, is_deleted
        utils.append_to(self.storage["friends"], data)
        self.client.add_route(constants.UPDATE_FRIEND + data["userUuid"], self._on_friend_update)
        return await self.on_friend_add(uuid, name, is_guest, is_online, is_deleted)

    async def on_friend_add(self, uuid, name, is_guest, is_online, is_deleted):
        print("[debug]", "on_friend_add")
        print(uuid, name, is_guest, is_online, is_deleted)
        pass

    async def _on_friend_remove(self, data, skip):
        uuid = utils.extract_uuid(data)
        if skip:
            return uuid
        utils.remove_from(self.storage["friends"], "userUuid", data)
        self.client.remove_route(constants.UPDATE_FRIEND + data)
        return await self.on_friend_remove(uuid)

    async def on_friend_remove(self, uuid):
        print("[debug]", "on_friend_remove")
        print(uuid)
        pass

    async def _on_friend_update(self, data, skip):
        uuid, name, is_guest, is_online, is_deleted = utils.extract_user(data)
        if skip:
            return uuid, name, is_guest, is_online, is_deleted
        friend = {"userUuid": data["userUuid"], "username": data["username"], "isOnline": data["isOnline"]}
        utils.update_in(self.storage["friends"], "userUuid", friend)
        return await self.on_friend_update(uuid, name, is_guest, is_online, is_deleted)

    async def on_friend_update(self, uuid, name, is_guest, is_online, is_deleted):
        print("[debug]", "on_friend_update")
        print(uuid, name, is_guest, is_online, is_deleted)
        pass

    async def _on_ban_add(self, data, skip):
        uuid = utils.extract_uuid(data)
        if skip:
            return uuid
        self.storage["chatroomBannedUuids"].append(data)
        return await self.on_ban_add(uuid)

    async def on_ban_add(self, uuid):
        print("[debug]", "on_ban_add")
        print(uuid)
        pass

    async def _on_ban_remove(self, data, skip):
        uuid = utils.extract_uuid(data)
        if skip:
            return uuid
        self.storage["chatroomBannedUuids"].remove(data)
        return await self.on_ban_remove(uuid)

    async def on_ban_remove(self, uuid):
        print("[debug]", "on_ban_remove")
        print(uuid)
        pass

    async def _on_user_add(self, data, skip):
        uuid, name, is_guest, is_online, is_deleted = utils.extract_user(data)
        if skip:
            return uuid, name, is_guest, is_online, is_deleted
        self.storage["chatroomContext"]["data"]["users"][data["userUuid"]] = data
        self.storage["chatroomContext"]["data"]["chatroom"]["usersCount"] += 1
        return await self.on_user_add(uuid, name, is_guest, is_online, is_deleted)

    async def on_user_add(self, uuid, name, is_guest, is_online, is_deleted):
        print("[debug]", "on_user_add")
        print(uuid, name, is_guest, is_online, is_deleted)
        pass

    async def _on_user_remove(self, data, skip):
        uuid = utils.extract_uuid(data)
        if skip:
            return uuid
        self.storage["chatroomContext"]["data"]["users"].pop(data)
        self.storage["chatroomContext"]["data"]["chatroom"]["usersCount"] -= 1
        return await self.on_user_remove(uuid)

    async def on_user_remove(self, uuid):
        print("[debug]", "on_user_remove")
        print(uuid)
        pass

    async def _on_text_add(self, data, skip):
        uuid, name, body, time, is_mine = utils.extract_chat(data, self.storage["accountContext"]["userUuid"])
        if skip:
            return uuid
        self.storage["chatroomContext"]["data"]["messages"].append(data)
        return await self.on_text_add(uuid, name, body, time, is_mine)

    async def on_text_add(self, uuid, name, body, time, is_mine):
        print("[debug]", "on_text_add")
        print(uuid, name, body, time, is_mine)
        pass

    async def _on_text_remove(self, data, skip):
        uuid = utils.extract_uuid(data)
        if skip:
            return uuid
        utils.remove_from(self.storage["chatroomContext"]["data"]["messages"], "userUuid", data)
        return await self.on_text_remove(uuid)

    async def on_text_remove(self, uuid):
        print("[debug]", "on_text_remove")
        print(uuid)
        pass

    async def _on_pv_open(self, data, skip):
        uuid, name, texts = utils.extract_conv(data, self.storage["accountContext"]["userUuid"])
        if skip:
            return uuid, name, texts
        self.storage["conversations"].append(data)
        self.client.add_route(constants.UPDATE_PV + data["otherUser"]["userUuid"], self._on_pv_update)
        return await self.on_pv_open(uuid, name, texts)

    async def on_pv_open(self, uuid, name, texts):
        print("[debug]", "on_pv_open")
        print(uuid, name, texts)
        pass

    async def _on_pv_close(self, data, skip):
        uuid = utils.extract_uuid(data)
        if skip:
            return uuid
        utils.remove_from(self.storage["conversations"], ["otherUser", "userUuid"], data)
        self.client.remove_route(constants.UPDATE_PV + data)
        return await self.on_pv_close(uuid)

    async def on_pv_close(self, uuid):
        print("[debug]", "on_pv_close")
        print(uuid)
        pass

    async def _on_pv_update(self, data, skip):
        uuid, name, is_guest, is_online, is_deleted = utils.extract_user(data)
        if skip:
            return uuid, name, is_guest, is_online, is_deleted
        otherUser = {"userUuid": data["userUuid"], "username": data["username"], "isOnline": data["isOnline"]}
        utils.update_in(self.storage["conversations"], ["otherUser", "userUuid"], otherUser)
        return await self.on_pv_update(uuid, name, is_guest, is_online, is_deleted)

    async def on_pv_update(self, uuid, name, is_guest, is_online, is_deleted):
        print("[debug]", "on_pv_update")
        print(uuid, name, is_guest, is_online, is_deleted)
        pass

    async def _on_pv_add(self, data, skip):
        uuid, body, time, is_mine = utils.extract_text(data, self.storage["accountContext"]["userUuid"])
        if skip:
            return uuid, body, time, is_mine
        utils.seek_append_to(self.storage["conversations"], "key", data["key"], "messages", data["msg"])
        return await self.on_pv_add(uuid, body, time, is_mine)

    async def on_pv_add(self, uuid, body, time, is_mine):
        print("[debug]", "on_pv_add")
        print(uuid, body, time, is_mine)
        pass

    async def _on_notice_add(self, data, skip):
        uuid, name, is_guest, is_online, is_deleted = utils.extract_user(data)
        if skip:
            return uuid, name, is_guest, is_online, is_deleted    
        utils.append_to(self.storage["conversationNotifications"], data)
        return await self.on_notice_add(uuid, name, is_guest, is_online, is_deleted)

    async def on_notice_add(self, uuid, name, is_guest, is_online, is_deleted):
        print("[debug]", "on_notice_add")
        print(uuid, name, is_guest, is_online, is_deleted)
        pass

    async def _on_notice_remove(self, data, skip):
        uuid = utils.extract_uuid(data)
        if skip:
            return uuid
        utils.remove_from(self.storage["conversationNotifications"], "userUuid", data)
        return await self.on_notice_remove(uuid)

    async def on_notice_remove(self, uuid):
        print("[debug]", "on_notice_remove")
        print(uuid)
        pass

    async def _on_user_context(self, data, skip):
        uuid, name, signature, is_guest, is_online, is_deleted, is_bluehead = await utils.extract_full(data)
        if skip:
            return uuid, name, signature, is_guest, is_online, is_deleted, is_bluehead
        return await self.on_user_context(uuid, name, signature, is_guest, is_online, is_deleted, is_bluehead)

    async def on_user_context(self, uuid, name, signature, is_guest, is_online, is_deleted, is_bluehead):
        print("[debug]", "on_user_context")
        print(uuid, name, signature, is_guest, is_online, is_deleted, is_bluehead)
        pass

    async def context_self(self):
        return await self.client.publish("/service/user/context/self/complete", {})

    async def add_pv(self, uuid, text):
        self.last_pv = await utils.wait_threshold(self.last_pv)
        return await self.client.publish("/service/conversation/message", {"conversationUserUuid": uuid, "messageBody": text})

    async def remove_notice(self, uuid):
        return await self.client.publish("/service/conversation/notification/removed", {"notificationUserUuid": uuid})

    async def open_pv(self, uuid):
        return await self.client.publish("/service/conversation/opened", {"conversationUserUuid": uuid})

    async def close_pv(self, uuid):
        return await self.client.publish("/service/conversation/closed", {"conversationUserUuid": uuid})

    async def add_ignored(self, uuid):
        return await self.client.publish("/service/ignored/add", {"userUuid": uuid})

    async def remove_ignored(self, uuid):
        return await self.client.publish("/service/ignored/remove", {"userUuid": uuid})

    async def add_friend(self, uuid):
        return await self.client.publish("/service/friends/add", {"userUuid": uuid})

    async def remove_firend(self, uuid):
        return await self.client.publish("/service/friends/remove", {"userUuid": uuid})

    async def add_ban(self, uuid):
        return await self.client.publish("/service/moderator/ban/add", {"targetUserUuid": uuid})

    async def remove_ban(self, uuid):
        return await self.client.publish("/service/moderator/ban/remove", {"targetUserUuid": uuid})

    async def add_text(self, text):
        self.last_pb = await utils.wait_threshold(self.last_pb)
        return await self.client.publish("/service/chatroom/message", {"messageBody": text})

    async def remove_text(self, uuid):
        return await self.client.publish("/service/moderator/messages/remove", {"targetUserUuid": uuid})

    async def context_user(self, uuid, short=False):
        uuid, name, signature, is_guest, is_online, is_deleted, is_bluehead = await self.client.publish("/service/user/context/target", {"userUuid": uuid})
        if short:
            return {"userUuid": uuid, "username": name}
        return uuid, name, signature, is_guest, is_online, is_deleted, is_bluehead = 

    async def batch_context_users(self, uuids):
        users = []
        for _uuid in uuids:
            uuid, name, signature, is_guest, is_online, is_deleted, is_bluehead = await self.context_user(_uuid)
            users.append({"userUuid": uuid, "username": name})
        return users
