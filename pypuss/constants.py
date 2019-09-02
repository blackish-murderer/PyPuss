import os

def _get_env_var(var_name):
    var_value = os.environ.get(var_name)
    if var_value is None:
        raise RuntimeError(f"Could not obtain {var_name}")
    return var_value

CHATROOM_ID = _get_env_var("CHATROOM_ID")
AUTH_COOKIE = _get_env_var("AUTH_COOKIE")

HOST_URL = _get_env_var("HOST_URL")
COMETD_URL = HOST_URL + "/cometd"
PROFILE_URL = HOST_URL + "/Resources/Website/Users/"
PROFILE_PATH = "/default.png"

import aiocometd

LONG_POLLING = aiocometd.ConnectionType.LONG_POLLING

ADD_USER = "/chatroom/user/joined/"
REMOVE_USER = "/chatroom/user/left/"
ADD_TEXT = "/chatroom/message/add/"
REMOVE_TEXT = "/chatroom/message/remove/"
ADD_FRIEND = "/service/friends/add"
REMOVE_FRIEND = "/service/friends/remove"
UPDATE_FRIEND = "/channel/user/friend/"
ADD_IGNORED = "/service/ignored/add"
REMOVE_IGNORED = "/service/ignored/remove"
ADD_BAN = "/service/moderator/ban/add"
REMOVE_BAN = "/service/moderator/ban/remove"
ADD_PV = "/service/conversation/message"
OPEN_PV = "/service/conversation/opened"
CLOSE_PV = "/service/conversation/closed"
UPDATE_PV = "/channel/user/conversation/"
CONTEXT_USER = "/service/user/context/target"
CONTEXT_SELF = "/service/user/context/self/complete"
ADD_NOTICE = "/service/conversation/notification/added"
REMOVE_NOTICE = "/service/conversation/notification/removed"
