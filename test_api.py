import requests
import json

# 读取cookie
with open('cookie.txt', 'r', encoding='utf-8') as f:
    cookie = f.read().strip()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://www.bilibili.com',
    'Cookie': cookie,
}

# 先获取aid
resp = requests.get('https://api.bilibili.com/x/web-interface/view', params={'bvid': 'BV1g7td6jEf7'}, headers=headers)
data = resp.json()
aid = data['data']['aid']
print(f'aid: {aid}')

# 测试评论API
resp = requests.get('https://api.bilibili.com/x/v2/reply', params={
    'type': 1,
    'oid': aid,
    'sort': 2,
    'pn': 1,
    'ps': 20,
}, headers=headers)
data = resp.json()
print(f'code: {data.get("code")}')
print(f'message: {data.get("message")}')
print(f'total: {data.get("data", {}).get("page", {}).get("count")}')
replies = data.get('data', {}).get('replies')
print(f'replies count: {len(replies) if replies else 0}')
if replies:
    for i, r in enumerate(replies[:3]):
        print(f'  {i+1}. {r["member"]["uname"]}: {r["content"]["message"][:40]}')

# 测试新API
print('\n--- 测试新API /x/v2/reply/main ---')
resp2 = requests.get('https://api.bilibili.com/x/v2/reply/main', params={
    'type': 1,
    'oid': aid,
    'mode': 3,
    'next': 0,
    'ps': 20,
}, headers=headers)
data2 = resp2.json()
print(f'code: {data2.get("code")}')
print(f'message: {data2.get("message")}')
replies2 = data2.get('data', {}).get('replies')
print(f'replies count: {len(replies2) if replies2 else 0}')
if replies2:
    for i, r in enumerate(replies2[:3]):
        print(f'  {i+1}. {r["member"]["uname"]}: {r["content"]["message"][:40]}')
