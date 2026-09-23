# Un-TikTok-Region-Checker
Unofficial Omar-Thing API to view profile info along with the account region, donor level, followers and following

## Usage

Profile info

```bash
python profileInfo.py linkmail1
```

Followers / following, the last number is how many pages to fetch, it stops after that:

```bash
python profileInfo.py linkmail1 followers 3
python profileInfo.py linkmail1 following 2
```

## Other

```python
from profileInfo import getInfo, getFollowers, getFollowing

info = getInfo('linkmail1')

fs = getFollowers('linkmail1', pages=3)
fg = getFollowing('linkmail1', pages=2)

# continue where the previous call stopped
more = getFollowers('linkmail1', pages=3, cursor=fs['minCursor'])

# skip the profile lookup if you already have the ids
fs = getFollowers(sec_uid=info['secUid'], user_id=info['userId'], pages=3)
```
## Example Output

### Profile

```json
{
  "nickname": "Linkmail",
  "username": "linkmail1",
  "region": "N/A",
  "language": "es",
  "about": "User has no about",
  "userId": "7251063426264302597",
  "secUid": "MS4wLjABAAAAKuCX9LNsd3QUILLhTjCvkqnkZBLpyN7XMJK0yLGrp7gxN_TO75Z_WZ0zySLQ42NK",
  "bioLink": "",
  "privateAccount": false,
  "isPrivate": "No",
  "isVerified": "No",
  "isSeller": "No",
  "openLikes": "No",
  "isLive": "No",
  "roomId": "",
  "accountCreated": "2023-07-02 03:50:49",
  "nicknameModified": "2026-06-27 11:14:53",
  "uniqueIdModified": "N/A",
  "avatar": "https://p19-common-sign.tiktokcdn-eu.com/tos-alisg-avt-0068/7c35c1471a1dc725e2b7ac960336d085~tplv-tiktokx-cropcenter:1080:1080.jpeg?...",
  "stats": {
    "followers": "14081",
    "following": "68",
    "hearts": "275",
    "videos": "0",
    "friends": "33"
  },
  "userRegionCode": "N/A",
  "priorityRegion": "CO",
  "level": "21"
}
```

### Followers / Following

```json
{
  "hasMore": true,
  "minCursor": "eyJtYXhfY3Vyc29yIjoxNzg2Mzc5OTM0LCJtaW5fY3Vyc29yIjoxNzg2MzE3Nzk0fQ==",
  "userList": [
    {
      "stats": {
        "followerCount": 1932,
        "followingCount": 1715,
        "heartCount": 18806,
        "videoCount": 715
      },
      "user": {
        "avatarLarger": "https://p16-common-sign.tiktokcdn.com/tos-alisg-avt-0068/fc862c1d97a78663e3bd1944e7786df5~tplv-tiktokx-cropcenter:1080:1080.webp?dr=14579&refresh_token=8cd982c5&x-expires=1790208000&x-signature=Wl3HGVSXtMmlL%2Fd54qfpWbUuJ9o%3D&t=4d5b0474&ps=13740610&shp=30310797&shcp=74c58a1a&idc=my",
        "nickname": "Liseth Ochoa",
        "region": "Colombia",
        "uniqueId": "licethochoa1"
      }
    },
      ...
  ]
}
```
