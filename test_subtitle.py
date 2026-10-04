import requests
import json

with open('cookie.txt', 'r', encoding='utf-8') as f:
    cookie = f.read().strip()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://www.bilibili.com/video/BV1g7td6jEf7',
    'Cookie': cookie,
}

bvid = 'BV1g7td6jEf7'

# 获取视频信息（含cid）
resp = requests.get('https://api.bilibili.com/x/web-interface/view', params={'bvid': bvid}, headers=headers)
data = resp.json()
cid = data['data']['cid']
print(f'cid: {cid}')

# 获取字幕列表
resp = requests.get('https://api.bilibili.com/x/player/v2', params={'bvid': bvid, 'cid': cid}, headers=headers)
data = resp.json()
print(f'code: {data.get("code")}')
print(f'message: {data.get("message")}')
subtitle_info = data.get('data', {}).get('subtitle', {})
print(f'subtitle_info keys: {list(subtitle_info.keys())}')
subtitles = subtitle_info.get('subtitles', [])
print(f'subtitles count: {len(subtitles)}')
for sub in subtitles:
    print(f'  - lan: {sub.get("lan")}, lan_doc: {sub.get("lan_doc")}, url: {sub.get("subtitle_url", "")[:80]}')
