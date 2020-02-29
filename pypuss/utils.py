import re
import json
import html
import asyncio
import difflib
import time as _time
import uuid as _uuid

import aiohttp

import pypuss.constants as constants

async def isblue(uuid):
    is_blue= False
    async with aiohttp.ClientSession() as session:
        query_url = constants.PROFILE_URL + uuid + constants.PROFILE_PATH
        async with session.get(query_url, allow_redirects=False) as response:
            is_blue= (response.status == 302)
    return is_blue

async def upgrade_cookies():
    def _extract_cookies(cookie_str):
        if not cookie_str:
            return
        match = re.search(r'\w+=\w+;', cookie_str)
        return match.group()

    cookies = constants.AUTH_COOKIE
    # print("[debug]", "upgrading cookies from", constants.AUTH_COOKIE)
    async with aiohttp.ClientSession() as session:
        query_url = constants.BROWSE_URL
        async with session.get(query_url,
                headers={'Cookie': cookies}) as response:
            new_cookie = response.headers.get('Set-Cookie')
            new_cookie = _extract_cookies(new_cookie)
            assert new_cookie
            cookies += ' ' + new_cookie
            await response.read()
        query_url = constants.COMETD_HANDSHAKE_URL
        post_data = constants.COMETD_HANDSHAKE_MESSAGE
        async with session.post(query_url,
                headers={'Cookie': cookies},
                json=post_data) as response:
            new_cookie = response.headers.get('Set-Cookie')
            new_cookie = _extract_cookies(new_cookie)
            assert new_cookie
            cookies += ' ' + new_cookie
    return cookies

async def wait_threshold(last_tick):
    wait_for = 2.048 - (_time.time() - last_tick)
    try:
        assert wait_for < 0
    except AssertionError:
        await asyncio.sleep(wait_for)
    finally:
        last_tick = _time.time()
    return last_tick

def isuuid(source):
    try:
        _uuid.UUID(source)
        return True
    except Exception:
        return False

def isasync(method):
    return asyncio.iscoroutinefunction(method)

def issync(method):
    return callable(method)

def unescape(payload):
    _payload = json.loads(
            html.unescape(
                json.dumps(payload)
                .replace("&quot;", "\\\"")))
    payload.clear()
    payload.extend(_payload)

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

def find_best_match(source, key, value, acceptable_rate=0.75):
    best_item = None
    best_rate = 0
    for item in source:
        rate = compare(item.get(key), value)
        if rate > best_rate:
            best_rate = rate
            best_item = item
    if best_rate > acceptable_rate:
        return best_item
    return None
