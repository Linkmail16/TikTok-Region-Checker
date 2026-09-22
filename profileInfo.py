# greetings to everyone
import base64
import json
import random
import re
import sys

import requests

SEAL_URLS = ['https://dev.omar-thing.site/api/v1/seal', 'https://for.omar-thing.site/api/seal']
REGION_URL = 'https://dev.omar-thing.site/api/v1/reg'
SEAL_SECRET = b'xK9#mQ2$vL7@nR4&jW8*pT6!cF3'
WORKER_URLS = ['https://worker.omar-thing.site/', 'https://for.omar-thing.site/test']

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


def _w3t(username):
    s = requests.Session()
    sd = _h8n(s, SEAL_URLS, {'username': username}, 'seal').json()
    w = _h8n(s, WORKER_URLS, {'sealed': sd['s'], 'seal_id': sd['id']}, 'worker').json()
    if 'p' not in w:
        return w
    plain = _q7x(w['p'], w['h'])
    data = json.loads(plain)
    if data.get('userId'):
        data['priorityRegion'] = _z4p(data['userId'], s)
    return data


def _j6f(text):
    if not text:
        return None
    m = re.search(r'tiktok\.com/@([a-zA-Z0-9._]+)', text)
    if m:
        return m.group(1)
    if text.startswith('@'):
        return text[1:]
    return text.strip()


if __name__ == '__main__':
    user = _j6f(sys.argv[1] if len(sys.argv) > 1 else 'linkmail1')
    data = _w3t(user)
    print(json.dumps(data, indent=2, ensure_ascii=False))
