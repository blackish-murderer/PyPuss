import json
import html
import difflib
import asyncio
import time as _time
import uuid as _uuid

import aiohttp

import pypuss.constants as constants

async def wait_threshold(last_tick):
    wait_for = 2.048 - (_time.time() - last_tick)
    try:
        assert wait_for < 0
        #print("[debug]", "we are", wait_for, "seconds ahead of threshold")
    except AssertionError:
        #print("[debug]", "we should wait for", wait_for, "seconds to send")
        await asyncio.sleep(wait_for)
    finally:
        last_tick = _time.time()
    return last_tick

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
    if path is None:
        return source
    if isinstance(path, str):
        return source.get(path, not_found)
    result = source.copy()
    for key in path:
        if key not in result:
            return not_found
        result = result[key]
    return result

def seek_unique_values(source, key):
    unique_values = []
    for item in source:
        _key = deep_get(item, key)
        if _key not in unique_values:
            unique_values.append(_key)
    return unique_values

def seek_append_to(source, master_key, master_value, other_key, other_value):
    for item in source:
        if deep_get(item, master_key) == master_value:
            deep_get(item, other_key).append(other_value)

def startswith(source, value):
    _source = source.lower()
    return _source.startswith(value)

def strip(source, value):
    _source = source[len(value):]
    return _source.strip()

def format_period(_p):
    _p = int(_p)
    _m, _s = _p // 60, _p % 60
    _h, _m = _m // 60, _m % 60
    _d, _h = _h // 24, _h % 24
    return f"{_d}:{_h:0>2d}:{_m:0>2d}:{_s:0>2d}"

def isuuid(source):
    try:
        _uuid.UUID(source)
        return True
    except Exception:
        return False

def ismatch(_a, _b, _r=0.75):
    if not isinstance(_a, str):
        _a = str(_a)
    if not isinstance(_b, str):
        _b = str(_b)
    return difflib.SequenceMatcher(None, _a.lower(), _b.lower()).ratio() >= _r

def compare(_a, _b):
    if not isinstance(_a, str):
        _a = str(_a)
    if not isinstance(_b, str):
        _b = str(_b)
    return difflib.SequenceMatcher(None, _a.lower(), _b.lower()).ratio()

def best_match(source, key, value, acceptable_rate=0.75):
    best_item = None
    best_rate = 0
    for item in source:
        rate = compare(deep_get(item, key), value)
        #print("[debug]", "compared", deep_get(item, key), "with", value, "result is", rate)
        if rate > best_rate:
            #print("[debug]", deep_get(item, key), "is a better match")
            best_rate = rate
            best_item = item
    if best_rate > acceptable_rate:
        #print("[debug]", "final match is", deep_get(best_item, key))
        return best_item
    return None

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
    texts = [{"is_mine": message["o"] == mine, "body": message["m"], "time": message["t"]} for message in data["messages"]]
    return uuid, name, texts

def extract_uuid(data):
    uuid = data
    return uuid
