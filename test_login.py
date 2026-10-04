import requests
with open('cookie.txt','r',encoding='utf-8') as f:
    cookie = f.read()
headers = {'User-Agent':'Mozilla/5.0','Referer':'https://www.bilibili.com','Cookie':cookie}
resp = requests.get('https://api.bilibili.com/x/web-interface/nav', headers=headers)
data = resp.json()
print('code:', data.get('code'))
print('message:', data.get('message'))
print('是否登录:', data.get('data',{}).get('isLogin'))
print('用户名:', data.get('data',{}).get('uname'))
print('vip状态:', data.get('data',{}).get('vipStatus'))
