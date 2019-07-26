import json
import html
import asyncio
import aiohttp

import pypuss.constants as constants

async def isbluehead(uuid):
    query_url = constants.PROFILE_URL + uuid + constants.PROFILE_PATH
    async with aiohttp.ClientSession() as session:
        async with session.get(query_url, allow_redirects=False) as response:
            return response.status == 302

def isasync(method):
    return asyncio.iscoroutinefunction(method)

def issync(method):
    return callable(method)

def unescape(payload):
    _payload = json.loads(html.unescape(json.dumps(payload).replace("&quot;", "\\\"")))
    payload.clear()
    payload.extend(_payload)

def ispublish(message):
    is_service = message.get("channel", "").startswith("/service")
    is_publish = ("id" in message and "successful" in message)
    return is_service and is_publish

def isresponse(message):
    is_service = message.get("channel", "").startswith("/service")
    has_data = "data" in message
    return is_service and has_data

def append_to(source, value):
    try:
        source.index(value)
    except ValueError:
        source.append(value)

def remove_from(source, key, value):
    needed = [item for item in source if deep_get(item, key) != value]
    source.clear()
    source.extend(needed)

def update_in(source, key, item):
    for index, _item in enumerate(source):
        if deep_get(_item, key) == deep_get(item, key):
            source[index] = item

def deep_get(source, path, not_found=None):
    if isinstance(path, str):
        return source.get(path, not_found)
    result = source.copy()
    for key in path:
        if key not in result:
            return not_found
        result = result[key]
    return result

def seek_append_to(source, master_key, master_value, other_key, other_value):
    for item in source:
        if deep_get(item, master_key) == master_value:
            deep_get(item, other_key).append(other_value)

def extract_self(data):
    return extract_user(data.get("accountContext", {}))

async def extract_full(data):
    uuid = data.get("userUuid")
    name = data.get("username")
    signature = data.get("signature")
    is_guest = data.get("isGuest")
    is_online = data.get("isOnline")
    is_deleted = data.get("isDeleted")
    is_bluehead = await isbluehead(data.get("userUuid"))
    return uuid, name, signature, is_guest, is_online, is_deleted, is_bluehead

def extract_user(data):
    uuid = data.get("userUuid")
    name = data.get("username")
    is_guest = data.get("isGuest")
    is_online = data.get("isOnline")
    is_deleted = data.get("isDeleted")
    return uuid, name, is_guest, is_online, is_deleted

def extract_chat(data, own_uuid):
    uuid = data.get("userUuid")
    name = data.get("username")
    body = data.get("messageBody")
    time = data.get("timestamp")
    is_mine = data.get("userUuid") == own_uuid
    return uuid, name, body, time, is_mine

def extract_text(data, own_uuid):
    uuid = data["key"].replace(own_uuid, "")
    body = data["msg"]["m"]
    time = data["msg"]["t"]
    mine = 1 if data["key"].startswith(own_uuid) else 2
    is_mine = data["msg"]["o"] == mine
    return uuid, body, time, is_mine

def extract_conv(data, own_uuid):
    uuid = data["otherUser"]["userUuid"]
    name = data["otherUser"]["username"]
    mine = 1 if data["key"].startswith(own_uuid) else 2
    texts = [{"is_mine": message["o"] == mine , "body": message["m"], "time": message["t"]} for message in data["messages"]]
    return uuid, name, texts

def extract_uuid(data):
    uuid = data
    return uuid

