import pypuss.utils as utils

def account_get_self(data):
    _data = {}


    room = data.get("room", {})

    _data["users"] = {}
    users = room.get("users", [])
    for user in users.values():
        uuid = user.get("userUuid")
        # assert utils.isuuid(uuid)
        _data["users"][uuid] = { "name": user.get("username"), "uuid": uuid }

    _data["texts"] = {}
    messages = room.get("messages", [])
    for message in messages:
        uuid = message["userUuid"]
        # assert utils.isuuid(uuid)
        _data["texts"][uuid] = { "name": message.get("username"), "uuid": uuid }

    _data["banned"] = {}
    banned = data.get("bannedAccounts", [])
    for user in banned:
        uuid = user.get("userUuid")
        # assert utils.isuuid(uuid)
        _data["banned"][uuid] = { "name": user.get("username"), "uuid": uuid }

    _data["myself"] = {}
    account = data.get("accountContext", {})
    uuid = account.get("userUuid")
    # assert utils.isuuid(uuid)
    _data["myself"] = { "name": account.get("username"), "uuid": uuid }

    return _data

def account_get_target(data):
    _data = {"name": data.get("username"),
            "uuid": data.get("userUuid"),
            "is_blue": data.get("isBlue"),
            "is_guest": data.get("isGuest"),
            "is_online": data.get("isOnline"),
            "is_deleted": data.get("isDeleted")}
    return _data

def moderator_account_banned(data):
    success = data.get("success")
    if not success:
        return None

    _data = {}
    user = data.get("data", {})
    uuid = user.get("userUuid")
    # assert utils.isuuid(uuid)
    _data = { "name": user.get("username"), "uuid": uuid }
    return _data

def moderator_account_unbanned(data):
    _data = data
    uuid = _data
    if not uuid: # utils.isuuid(uuid)
        return None

    return _data

def chatroom_message_add(data):
    _data = {"name": data.get("username"),
            "uuid": data.get("userUuid"),
            "text": data.get("messageBody"),
            "time": data.get("timestamp")}
    return _data

def chatroom_user_joined(data):
    _data = {"name": data.get("username"),
            "uuid": data.get("userUuid")}
    return _data

def conversation_message(data):
    key = data.get("key")
    msg = data.get("msg")
    if not key or not msg:
        return None

    key_1, key_2 = key[:len(key) // 2], key[len(key) // 2:]

    _data = {"uuid": key_1 if msg["o"] == 1 else key_2,
            "text": msg.get("m"),
            "time": msg.get("t")}
    return _data
