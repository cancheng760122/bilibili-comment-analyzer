import requests
import json

with open('cookie.txt', 'r', encoding='utf-8') as f:
    cookie = f.read().strip()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.bilibili.com/video/BV1g7td6jEf7',
    'Origin': 'https://www.bilibili.com',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Cookie': cookie,
}

aid = 117205849085992

# 测试不同sort参数
for sort in [0, 1, 2]:
    resp = requests.get('https://api.bilibili.com/x/v2/reply', params={
        'type': 1,
        'oid': aid,
        'sort': sort,
        'pn': 1,
        'ps': 20,
    }, headers=headers)
    data = resp.json()
    replies = data.get('data', {}).get('replies')
    print(f'sort={sort}: code={data.get("code")}, replies={len(replies) if replies else 0}')

# 测试新API不同mode
for mode in [0, 1, 2, 3]:
    resp = requests.get('https://api.bilibili.com/x/v2/reply/main', params={
        'type': 1,
        'oid': aid,
        'mode': mode,
        'next': 0,
        'ps': 20,
    }, headers=headers)
    data = resp.json()
    replies = data.get('data', {}).get('replies')
    print(f'mode={mode}: code={data.get("code")}, replies={len(replies) if replies else 0}')

# 测试第2页
resp = requests.get('https://api.bilibili.com/x/v2/reply', params={
    'type': 1,
    'oid': aid,
    'sort': 2,
    'pn': 2,
    'ps': 20,
}, headers=headers)
data = resp.json()
replies = data.get('data', {}).get('replies')
print(f'pn=2: code={data.get("code")}, replies={len(replies) if replies else 0}')
