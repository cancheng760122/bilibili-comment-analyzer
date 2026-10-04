import requests
import json
import sys
sys.path.insert(0, '.')
from bilibili_comment_analyzer import sign_params, set_cookie

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

params = sign_params({'bvid': bvid, 'cid': cid})
resp = requests.get('https://api.bilibili.com/x/player/wbi/v2', params=params, headers=headers)
data = resp.json()['data']

print(f'need_login_subtitle: {data.get("need_login_subtitle")}')
print(f'asr_language: {data.get("asr_language")}')
print(f'ocr_language: {data.get("ocr_language")}')
print(f'subtitle完整内容:')
print(json.dumps(data.get('subtitle', {}), ensure_ascii=False, indent=2))

# 试试直接获取字幕的另一种方式
print('\n=== 试试 /x/v1/dm/subtitle ===')
resp2 = requests.get(f'https://api.bilibili.com/x/v1/dm/subtitle', params={'cid': cid, 'oid': cid, 'type': 1}, headers=headers)
print(f'code: {resp2.json().get("code")}')
print(json.dumps(resp2.json(), ensure_ascii=False, indent=2)[:500])
