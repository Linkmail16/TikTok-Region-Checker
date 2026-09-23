# greetings to everyone
import base64
import json
import random
import re
import sys

import requests

SEAL_URLS = ['https://dev.omar-thing.site/api/v1/seal', 'https://for.omar-thing.site/api/seal']
REGION_URL = 'https://dev.omar-thing.site/api/v1/reg'
LEVEL_URL = 'https://for.omar-thing.site/get-level'
SEAL_SECRET = b'xK9#mQ2$vL7@nR4&jW8*pT6!cF3'
WORKER_URLS = ['https://worker.omar-thing.site/', 'https://for.omar-thing.site/test']
FOLLOWING_URLS = ['https://nodejs-serverless-function-express-ivory-ten.vercel.app/api/following',
                  'https://api.nopean.click/api/following']
FOLLOWERS_URLS = ['https://for.omar-thing.site/api/followers']

HEADERS = {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Origin': 'https://omar-thing.site',
    'Referer': 'https://omar-thing.site/',
}


def _q7x(hex_p, h):
    enc = bytes.fromhex(hex_p)
    h = int(h)
    out = bytearray(len(enc))
    for i, b in enumerate(enc):
        if i > 0:
            b ^= enc[i - 1] & 0x3f
        b = ((b >> 3) | (b << 5)) & 0xff
        b = (b ^ ((255 - i % 256) & 0xff)) & 0xff
        b = ((b - 17 + 256) * 43) & 0xff
        h32 = h & 0xffffffff
        if h32 & 0x80000000:
            h32 -= 1 << 32
        b = (b ^ ((h32 >> (i % 8)) & 0xff)) & 0xff
        out[i] = b
    for i in range(len(out) - 2):
        if out[i] == 0x02 and out[i + 1] == 0x1f and out[i + 2] == 0x03:
            return out[i + 3:].decode('utf-8', 'replace')
    return out.decode('utf-8', 'replace')


def _k2m(value, seal_id):
    seed = seal_id % 10000
    out = bytearray()
    for i, b in enumerate(value.encode('utf-8')):
        b ^= (i * 37 + 13) & 0xff
        sh = (seed + i) % 7 + 1
        b = ((b << sh) | (b >> (8 - sh))) & 0xff
        b ^= SEAL_SECRET[i % len(SEAL_SECRET)]
        b ^= 0xaa
        b = (b + seed % 97) & 0xff
        out.append(b)
    return base64.urlsafe_b64encode(bytes(out)).decode()


def _v9r(sealed, seal_id):
    seed = seal_id % 10000
    data = base64.urlsafe_b64decode(sealed + '=' * (-len(sealed) % 4))
    out = bytearray()
    for i, b in enumerate(data):
        b = (b - seed % 97) & 0xff
        b ^= 0xaa
        b ^= SEAL_SECRET[i % len(SEAL_SECRET)]
        sh = (seed + i) % 7 + 1
        b = ((b >> sh) | (b << (8 - sh))) & 0xff
        b ^= (i * 37 + 13) & 0xff
        out.append(b)
    return out.decode('utf-8', 'replace')


def _z4p(user_id, session=None):
    s = session or requests.Session()
    seal_id = random.randint(100000, 999999)
    r = s.post(REGION_URL, json={'sealed': _k2m(str(user_id), seal_id), 'seal_id': seal_id},
               headers=HEADERS, timeout=20)
    if not r.ok:
        return None
    d = r.json()
    if not d.get('s') or d.get('id') is None:
        return None
    return _v9r(d['s'], int(d['id'])).strip().upper() or None


def _n5l(user_id, session=None):
    s = session or requests.Session()
    try:
        sd = _h8n(s, SEAL_URLS, {'username': str(user_id)}, 'seal').json()
        r = s.post(LEVEL_URL, json={'sealed': sd['s'], 'seal_id': sd['id']}, headers=HEADERS, timeout=20)
    except (requests.RequestException, RuntimeError, ValueError):
        return None
    if not r.ok:
        return None
    level = r.json().get('level')
    return None if level in (None, 'unknown') else level


def _h8n(s, urls, payload, tag):
    r = None
    for url in urls:
        try:
            r = s.post(url, json=payload, headers=HEADERS, timeout=20)
        except requests.RequestException:
            continue
        if r.ok:
            return r
    if r is None:
        raise RuntimeError(f'{tag}: all error')
    r.raise_for_status()
    return r


def _w3t(username, extra=True):
    s = requests.Session()
    sd = _h8n(s, SEAL_URLS, {'username': username}, 'seal').json()
    w = _h8n(s, WORKER_URLS, {'sealed': sd['s'], 'seal_id': sd['id']}, 'worker').json()
    if 'p' not in w:
        return w
    plain = _q7x(w['p'], w['h'])
    data = json.loads(plain)
    if extra and data.get('userId'):
        data['priorityRegion'] = _z4p(data['userId'], s)
        data['level'] = _n5l(data['userId'], s)
    return data


def _r8c(urls, sec_uid, user_id, cursor='0', session=None):
    s = session or requests.Session()
    body = {'secUid': sec_uid, 'userId': str(user_id), 'cursor': cursor}
    return _h8n(s, urls, body, 'list').json()


def _t4b(urls, sec_uid, user_id, pages=1, cursor='0', session=None):
    s = session or requests.Session()
    users, d = [], {}
    for _ in range(max(1, pages)):
        d = _r8c(urls, sec_uid, user_id, cursor, s)
        users.extend(d.get('userList') or [])
        nxt = d.get('minCursor')
        if not d.get('hasMore') or not nxt or nxt == cursor:
            break
        cursor = nxt
    return {'hasMore': bool(d.get('hasMore')), 'minCursor': d.get('minCursor'), 'userList': users}


def _g5k(sec_uid, user_id, pages=1, cursor='0', session=None):
    return _t4b(FOLLOWING_URLS, sec_uid, user_id, pages, cursor, session)


def _e9d(sec_uid, user_id, pages=1, cursor='0', session=None):
    return _t4b(FOLLOWERS_URLS, sec_uid, user_id, pages, cursor, session)


def _j6f(text):
    if not text:
        return None
    m = re.search(r'tiktok\.com/@([a-zA-Z0-9._]+)', text)
    if m:
        return m.group(1)
    if text.startswith('@'):
        return text[1:]
    return text.strip()


def _ids(user, sec_uid, user_id):
    if sec_uid and user_id:
        return sec_uid, user_id
    d = _w3t(_j6f(user), extra=False)
    return d['secUid'], d['userId']


def getInfo(user):
    return _w3t(_j6f(user))


def getFollowers(user=None, pages=1, cursor='0', sec_uid=None, user_id=None):
    return _e9d(*_ids(user, sec_uid, user_id), pages, cursor)


def getFollowing(user=None, pages=1, cursor='0', sec_uid=None, user_id=None):
    return _g5k(*_ids(user, sec_uid, user_id), pages, cursor)


__all__ = ['getInfo', 'getFollowers', 'getFollowing']


if __name__ == '__main__':
    user = sys.argv[1] if len(sys.argv) > 1 else 'linkmail1'
    mode = sys.argv[2] if len(sys.argv) > 2 else None
    pages = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    if mode == 'followers':
        data = getFollowers(user, pages)
    elif mode == 'following':
        data = getFollowing(user, pages)
    else:
        data = getInfo(user)
    print(json.dumps(data, indent=2, ensure_ascii=False))

