import requests
import json
import sys
sys.path.insert(0, '.')
from bilibili_comment_analyzer import sign_params, get_mixin_key, BILIBILI_COOKIE, set_cookie

with open('cookie.txt', 'r', encoding='utf-8') as f:
    cookie = f.read().strip()
set_cookie(cookie)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://www.bilibili.com/video/BV1g7td6jEf7',
    'Cookie': cookie,
}

bvid = 'BV1g7td6jEf7'
cid = 41542946383

# 方式1: 普通player接口
print('=== 方式1: /x/player/v2 ===')
resp = requests.get('https://api.bilibili.com/x/player/v2', params={'bvid': bvid, 'cid': cid}, headers=headers)
data = resp.json()
subtitle_info = data.get('data', {}).get('subtitle', {})
print(f'subtitles: {subtitle_info.get("subtitles", [])}')
print(f'lan: {subtitle_info.get("lan")}')
print(f'lan_doc: {subtitle_info.get("lan_doc")}')

# 方式2: 带wbi签名的player接口
print('\n=== 方式2: /x/player/wbi/v2 (带签名) ===')
params = sign_params({'bvid': bvid, 'cid': cid})
resp = requests.get('https://api.bilibili.com/x/player/wbi/v2', params=params, headers=headers)
data = resp.json()
print(f'code: {data.get("code")}, message: {data.get("message")}')
subtitle_info = data.get('data', {}).get('subtitle', {})
print(f'subtitles count: {len(subtitle_info.get("subtitles", []))}')
for sub in subtitle_info.get('subtitles', []):
    print(f'  - {sub.get("lan_doc")}: {sub.get("subtitle_url", "")[:100]}')

# 方式3: 看看完整的data结构
print('\n=== 方式2完整data keys ===')
print(list(data.get('data', {}).keys()))
