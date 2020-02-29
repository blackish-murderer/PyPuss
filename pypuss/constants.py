import os

def _get_env_var(var_name):
    var_value = os.environ.get(var_name)
    if var_value is None:
        raise RuntimeError(f"Could not obtain {var_name}")
    return var_value

CHATROOM_ID = _get_env_var("CHATROOM_ID")
AUTH_COOKIE = _get_env_var("AUTH_COOKIE")

HOST_URL = _get_env_var("HOST_URL")
BROWSE_URL = HOST_URL + "/browse"
COMETD_URL = HOST_URL + "/cometd"
COMETD_HANDSHAKE_URL = COMETD_URL + "/handshake"
PROFILE_URL = HOST_URL + "/Resources/Website/Users/"
PROFILE_PATH = "/default.png"

COMETD_HANDSHAKE_MESSAGE = [{
    "channel":"/meta/handshake",
    "ext":{"chatroomId":int(CHATROOM_ID)},
    "supportedConnectionTypes":["long-polling"],
    "version":"1.0"}]

# get account data for self
# data empty
ACCOUNT_GET_SELF = "/service/account/get-self"

# get account data for target
# data { accountId }
ACCOUNT_GET_TARGET = "/service/account/get-target"

# ban account
# data { accountId }
MODERATOR_BAN_ACCOUNT = "/service/moderator/ban-account"
# account banned
# data { data { user } success }
MODERATOR_ACCOUNT_BANNED = "/service/moderator/account-banned"

# unban account
# data { accountId }
MODERATOR_UNBAN_ACCOUNT = "/service/moderator/unban-account"
# account unbanned
# data userUuid
MODERATOR_ACCOUNT_UNBANNED = "/service/moderator/account-unbanned"

# chatroom message
# data { messageBody }
CHATROOM_MESSAGE = "/service/chatroom/message"
# response data for add
# data { userUuid messageBody timestamp username }
CHATROOM_MESSAGE_ADD = "/chatroom/message/add/" + CHATROOM_ID

# remove messages
# data { accountId }
MODERATOR_REMOVE_MESSAGES = "/service/moderator/remove-messages"
# messages removed
# data userUuid
MODERATOR_MESSAGES_REMOVED = "/service/moderator/messages-removed"
# chatroom message remove
# data userUuid
CHATROOM_MESSAGE_REMOVE = "/chatroom/message/remove/" + CHATROOM_ID

# chatroom user joined
# data { }
CHATROOM_USER_JOINED = "/chatroom/user/joined/" + CHATROOM_ID

# chatroom user left
# data userUuid
CHATROOM_USER_LEFT = "/chatroom/user/left/" + CHATROOM_ID

# conversation notification added
# data { }
CONVERSATION_NOTIFICATION_ADDED = "/service/conversation/notification/added"

# conversation notification removed
# data userUuid
CONVERSATION_NOTIFICATION_REMOVED = "/service/conversation/notification/removed"

# conversation opened
# data { conversationUserUuid }
CONVERSATION_OPENED = "/service/conversation/opened"

# conversation closed
# data userUuid
CONVERSATION_CLOSED = "/service/conversation/closed"

# conversation message
# data { conversationUserUuid messageBody }
CONVERSATION_MESSAGE = "/service/conversation/message"

# user conversation
# data { }
USER_CONVERSATION = "/channel/user/conversation/" # + userUuid

# friends add
# data { userUuid }
FRIENDS_ADD = "/service/friends/add"

# friends remove
# data { userUuid }
FRIENDS_REMOVE = "/service/friends/remove"

# user friend
# data { }
USER_FRIEND = "/channel/user/friend/" # + userUuid

# ignored add
# data { userUuid }
IGNORED_ADD = "/service/ignored/add"

# ignored remove
# data { userUuid }
IGNORED_REMOVE = "/service/ignored/remove"
