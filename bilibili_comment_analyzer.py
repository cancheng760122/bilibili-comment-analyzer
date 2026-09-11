#!/usr/bin/env python3
"""
B站视频评论 & 弹幕爬取分析工具
输入BV号，自动爬取评论和弹幕，生成交互式HTML分析报告

使用方法:
    python bilibili_comment_analyzer.py BV1xx411c7mD
    python bilibili_comment_analyzer.py BV1xx411c7mD --max-pages 10

依赖:
    pip install requests jieba
"""

import argparse
import json
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime
from urllib.parse import quote

import requests

# ============================================================
# 配置
# ============================================================

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Origin": "https://www.bilibili.com",
}

# 全局Cookie（运行时设置）
BILIBILI_COOKIE = ""


def set_cookie(cookie):
    """设置B站Cookie到请求头"""
    global BILIBILI_COOKIE
    BILIBILI_COOKIE = cookie
    if cookie:
        HEADERS["Cookie"] = cookie

# 情感词典（简单版）
POSITIVE_WORDS = {
    "好", "棒", "赞", "喜欢", "支持", "厉害", "优秀", "精彩", "不错", "感谢",
    "牛", "强", "爱了", "绝了", "神", "完美", "期待", "加油", "学到", "有用",
    "清晰", "详细", "专业", "用心", "良心", "推荐", "宝藏", "干货", "666", "哈哈哈"
}
NEGATIVE_WORDS = {
    "差", "烂", "垃圾", "讨厌", "反对", "批评", "错误", "问题", "bug", "难用",
    "失望", "无聊", "浪费", "骗", "假", "抄袭", "水", "尬", "恶心", "无语",
    "退钱", "举报", "拉黑", "取关", "营销号", "标题党"
}

STOP_WORDS = {
    "的", "了", "是", "在", "和", "有", "就", "都", "而", "及", "与", "之", "也",
    "不", "很", "还", "这", "那", "我", "你", "他", "她", "它", "什么", "怎么",
    "一个", "一点", "全部", "看看", "视频", "B站", "bilibili", "我们", "你们",
    "他们", "这个", "那个", "可以", "已经", "还是", "就是", "不是", "没有", "自己",
    "一下", "一些", "一种", "一样", "真的", "太", "最", "更", "非常", "特别",
    "比较", "其实", "然后", "因为", "所以", "如果", "但是", "而且", "或者", "虽然",
    "不过", "以及", "等等", "之类", "这么", "那么", "怎样", "咋样", "啥", "呗",
    "呀", "啊", "吧", "呢", "嘛", "哦", "哈", "嘿", "哎", "嗯", "哦", "UP", "up",
    "主", "说", "做", "要", "会", "能", "对", "去", "来", "给", "从", "到", "被",
    "把", "让", "用", "想", "看", "听", "知道", "觉得", "感觉", "应该", "可能",
    "大概", "也许", "似乎", "好像", "比如", "例如", "关于", "对于", "通过", "根据",
    "为了", "由于", "随着", "按照", "经过", "由于", "除了", "只有", "只要", "只有",
    "不仅", "不但", "而且", "既", "又", "或者", "要么", "与其", "不如", "宁可",
    "也不", "即使", "也", "无论", "都", "不管", "总是", "向来", "从来", "一直",
    "曾经", "已经", "刚刚", "正在", "将要", "马上", "立刻", "顿时", "忽然",
    "渐渐", "逐渐", "慢慢", "悄悄", "偷偷", "明明", "偏偏", "简直", "几乎",
    "差不多", "大概", "也许", "或许", "恐怕", "难道", "究竟", "到底", "毕竟",
    "居然", "竟然", "果然", "幸亏", "难怪", "原来", "其实", "事实上", "实际上",
    "当然", "自然", "显然", "明显", "确实", "的确", "真的", "实在", "根本",
    "完全", "全部", "所有", "一切", "整个", "整个", "每", "各", "某", "另",
    "其他", "另外", "其余", "剩下", "以上", "以下", "以内", "以外", "之前",
    "之后", "以前", "以后", "上面", "下面", "里面", "外面", "前面", "后面",
    "左边", "右边", "中间", "旁边", "附近", "周围", "到处", "处处", "哪里",
    "这儿", "那儿", "这里", "那里", "此时", "此刻", "当时", "那时", "今天",
    "明天", "昨天", "现在", "过去", "将来", "未来", "以前", "从前", "曾经",
    "刚才", "刚刚", "马上", "立刻", "顿时", "忽然", "突然", "渐渐", "逐渐",
    "慢慢", "逐步", "依次", "陆续", "相继", "同时", "一起", "共同", "互相",
    "彼此", "分别", "各自", "独立", "单独", "亲自", "顺便", "趁机", "特意",
    "特地", "故意", "有意", "无意", "偶然", "偶尔", "有时", "时常", "经常",
    "常常", "总是", "永远", "一直", "始终", "从来", "向来", "历来", "一向",
    "早就", "早已", "即将", "将要", "快要", "就要", "终于", "最终", "最后",
    "结果", "总之", "总而言之", "综上所述", "由此可见", "因此", "所以",
    "因而", "从而", "以致", "以至", "于是", "然后", "接着", "随后", "最后",
    "首先", "其次", "再次", "最后", "第一", "第二", "第三", "一方面", "另一方面"
}


# ============================================================
# 工具函数
# ============================================================

def print_progress(current, total, prefix=""):
    """打印进度条"""
    percent = current / total * 100 if total > 0 else 0
    bar_len = 30
    filled = int(bar_len * current / total) if total > 0 else 0
    bar = "█" * filled + "░" * (bar_len - filled)
    print(f"\r{prefix} [{bar}] {current}/{total} ({percent:.1f}%)", end="", flush=True)
    if current >= total:
        print()


def safe_get(url, params=None, retries=3, delay=1):
    """带重试的GET请求"""
    for i in range(retries):
        try:
            resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            return resp
        except Exception as e:
            if i < retries - 1:
                time.sleep(delay)
            else:
                print(f"\n⚠️  请求失败: {e}")
                return None


def extract_bvid(input_str):
    """从输入中提取BV号"""
    match = re.search(r"BV[0-9A-Za-z]{10}", input_str)
    if match:
        return match.group()
    return input_str.strip()


# ============================================================
# B站API
# ============================================================

# WBI签名相关
MIXIN_KEY_ENC_TAB = [
    46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35,
    27, 43, 5, 49, 33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13,
    37, 48, 7, 16, 24, 55, 40, 61, 26, 17, 0, 1, 60, 51, 30, 4,
    22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11, 36, 20, 34, 44, 52
]

_wbi_keys_cache = None


def get_wbi_keys():
    """获取wbi签名的img_key和sub_key（带缓存）"""
    global _wbi_keys_cache
    if _wbi_keys_cache:
        return _wbi_keys_cache
    url = "https://api.bilibili.com/x/web-interface/nav"
    resp = safe_get(url)
    if not resp:
        return None, None
    data = resp.json()
    if data.get("code") != 0:
        return None, None
    wbi_img = data.get("data", {}).get("wbi_img", {})
    img_url = wbi_img.get("img_url", "")
    sub_url = wbi_img.get("sub_url", "")
    img_key = img_url.split("/")[-1].split(".")[0]
    sub_key = sub_url.split("/")[-1].split(".")[0]
    _wbi_keys_cache = (img_key, sub_key)
    return img_key, sub_key


def get_mixin_key(img_key, sub_key):
    """生成mixin_key"""
    raw = img_key + sub_key
    return "".join(raw[i] for i in MIXIN_KEY_ENC_TAB)[:32]


def sign_params(params):
    """对请求参数进行wbi签名"""
    import hashlib
    from urllib.parse import quote
    img_key, sub_key = get_wbi_keys()
    if not img_key or not sub_key:
        return params
    mixin_key = get_mixin_key(img_key, sub_key)
    params = dict(params)
    params["wts"] = int(time.time())
    # 按key排序
    sorted_params = dict(sorted(params.items()))
    # 对value进行URL编码并拼接
    query = "&".join(f"{k}={quote(str(v), safe='!*()')}" for k, v in sorted_params.items())
    # 计算md5
    w_rid = hashlib.md5((query + mixin_key).encode()).hexdigest()
    sorted_params["w_rid"] = w_rid
    return sorted_params


def get_video_info(bvid):
    """获取视频基本信息"""
    url = "https://api.bilibili.com/x/web-interface/view"
    params = sign_params({"bvid": bvid})
    resp = safe_get(url, params=params)
    if not resp:
        return None
    data = resp.json()
    if data.get("code") != 0:
        print(f"❌ 获取视频信息失败: {data.get('message', '未知错误')} (code={data.get('code')})")
        print(f"   请求URL: {resp.url}")
        print(f"   返回数据: {str(data)[:500]}")
        return None
    d = data["data"]
    return {
        "bvid": bvid,
        "aid": d["aid"],
        "cid": d["cid"],
        "title": d["title"],
        "owner": d["owner"]["name"],
        "desc": d.get("desc", ""),
        "view": d["stat"]["view"],
        "danmaku": d["stat"]["danmaku"],
        "reply": d["stat"]["reply"],
        "like": d["stat"]["like"],
        "coin": d["stat"]["coin"],
        "favorite": d["stat"]["favorite"],
        "share": d["stat"]["share"],
        "pubdate": datetime.fromtimestamp(d["pubdate"]).strftime("%Y-%m-%d %H:%M:%S"),
        "duration": d["duration"],
        "pic": d["pic"],
    }


def get_comments(aid, max_pages=50):
    """爬取视频评论（主评论+楼中楼）"""
    all_comments = []
    url = "https://api.bilibili.com/x/v2/reply/main"
    
    next_cursor = 0
    page = 0
    
    while page < max_pages:
        params = sign_params({
            "type": 1,
            "oid": aid,
            "mode": 3,  # 3=按热度排序
            "next": next_cursor,
            "ps": 20,
        })
        resp = safe_get(url, params=params)
        if not resp:
            break
        
        data = resp.json()
        if data.get("code") != 0:
            break
        
        replies = data.get("data", {}).get("replies")
        if not replies:
            break
        
        for reply in replies:
            # 主评论
            comment = {
                "rpid": reply["rpid"],
                "user": reply["member"]["uname"],
                "content": reply["content"]["message"],
                "like": reply["like"],
                "ctime": datetime.fromtimestamp(reply["ctime"]).strftime("%Y-%m-%d %H:%M:%S"),
                "replies_count": reply.get("rcount", 0),
                "replies": [],
            }
            # 楼中楼
            sub_replies = reply.get("replies")
            if sub_replies:
                for sub in sub_replies:
                    comment["replies"].append({
                        "user": sub["member"]["uname"],
                        "content": sub["content"]["message"],
                        "like": sub["like"],
                        "ctime": datetime.fromtimestamp(sub["ctime"]).strftime("%Y-%m-%d %H:%M:%S"),
                    })
            all_comments.append(comment)
        
        # 下一页
        cursor = data.get("data", {}).get("cursor", {})
        next_cursor = cursor.get("next", 0)
        is_end = cursor.get("is_end", False)
        
        page += 1
        print_progress(page, max_pages, "爬取评论中")
        
        if is_end:
            break
        time.sleep(0.5)
    
    return all_comments


def get_danmaku(cid):
    """爬取弹幕（XML格式）"""
    url = f"https://comment.bilibili.com/{cid}.xml"
    resp = safe_get(url)
    if not resp:
        return []
    
    resp.encoding = "utf-8"
    danmakus = []
    
    # 解析XML
    pattern = re.compile(r'<d p="([^"]+)">(.*?)</d>')
    matches = pattern.findall(resp.text)
    
    for attrs, text in matches:
        parts = attrs.split(",")
        if len(parts) >= 4:
            try:
                danmakus.append({
                    "time": float(parts[0]),  # 出现时间（秒）
                    "type": int(parts[1]),     # 弹幕类型
                    "size": int(parts[2]),     # 字号
                    "color": parts[3],         # 颜色
                    "content": text,
                })
            except (ValueError, IndexError):
                continue
    
    return danmakus


def get_video_tags(bvid):
    """获取视频标签"""
    url = "https://api.bilibili.com/x/tag/archive/tags"
    resp = safe_get(url, params={"bvid": bvid})
    if not resp:
        return []
    data = resp.json()
    if data.get("code") != 0:
        return []
    tags = []
    for t in data.get("data", []):
        tags.append({
            "tag_id": t.get("tag_id", ""),
            "tag_name": t.get("tag_name", ""),
            "count": t.get("count", 0),
            "type": t.get("type", 0),
        })
    return tags


def get_video_subtitle(bvid, cid):
    """获取视频AI字幕"""
    # 先获取字幕列表
    url = "https://api.bilibili.com/x/player/v2"
    resp = safe_get(url, params={"bvid": bvid, "cid": cid})
    if not resp:
        return None, "无法获取字幕信息"
    
    data = resp.json()
    if data.get("code") != 0:
        return None, data.get("message", "获取字幕失败")
    
    subtitle_info = data.get("data", {}).get("subtitle", {})
    subtitles = subtitle_info.get("subtitles", [])
    
    if not subtitles:
        return None, "该视频暂无AI字幕"
    
    # 获取第一个字幕（通常是中文）
    subtitle_url = subtitles[0].get("subtitle_url", "")
    if not subtitle_url:
        return None, "字幕链接为空"
    
    if subtitle_url.startswith("//"):
        subtitle_url = "https:" + subtitle_url
    
    # 下载字幕内容
    resp = safe_get(subtitle_url)
    if not resp:
        return None, "下载字幕失败"
    
    try:
        subtitle_data = resp.json()
        body = subtitle_data.get("body", [])
        subtitles_list = []
        full_text = ""
        for item in body:
            subtitles_list.append({
                "from": item.get("from", 0),
                "to": item.get("to", 0),
                "content": item.get("content", ""),
            })
            full_text += item.get("content", "") + " "
        
        return {
            "subtitles": subtitles_list,
            "full_text": full_text.strip(),
            "count": len(subtitles_list),
            "lan": subtitles[0].get("lan", ""),
        }, None
    except Exception as e:
        return None, f"解析字幕失败: {str(e)}"


def summarize_video_content(video_info, subtitle_data, tags, comments, danmakus):
    """
    智能总结视频内容
    综合：视频简介、字幕、标签、评论高频词、弹幕高频词
    """
    summary = {
        "has_subtitle": subtitle_data is not None,
        "subtitle_error": None,
        "tags": [t["tag_name"] for t in tags],
        "key_points": [],
        "high_freq_words": [],
        "content_topics": [],
        "audience_feedback": "",
        "estimated_reading_time": 0,
    }
    
    if subtitle_data is None:
        # 没有字幕时，用简介+评论+弹幕来总结
        summary["subtitle_error"] = "该视频暂无AI字幕，以下基于视频简介、评论和弹幕进行总结"
    
    # 1. 提取所有文本用于分析
    all_texts = []
    if video_info.get("desc"):
        all_texts.append(video_info["desc"])
    if subtitle_data:
        all_texts.append(subtitle_data["full_text"])
    for c in comments[:50]:  # 取前50条热门评论
        all_texts.append(c["content"])
    for d in danmakus[:200]:  # 取前200条弹幕
        all_texts.append(d["content"])
    
    # 2. 高频词分析
    try:
        import jieba
        all_words = []
        for text in all_texts:
            if not text:
                continue
            text = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9]", " ", text)
            words = jieba.lcut(text)
            for w in words:
                w = w.strip()
                if len(w) > 1 and w not in STOP_WORDS and not w.isdigit():
                    all_words.append(w)
        counter = Counter(all_words)
        summary["high_freq_words"] = counter.most_common(20)
    except ImportError:
        pass
    
    # 3. 提取关键句子（基于关键词密度和位置）
    if subtitle_data and subtitle_data["subtitles"]:
        subtitles = subtitle_data["subtitles"]
        # 计算每个句子的关键词密度得分
        key_words_set = set(w for w, _ in summary["high_freq_words"][:10])
        scored_sentences = []
        for i, sub in enumerate(subtitles):
            content = sub["content"]
            # 关键词命中数
            keyword_hits = sum(1 for w in key_words_set if w in content)
            # 位置权重（开头和结尾的句子更重要）
            position_score = 0
            if i < len(subtitles) * 0.1:  # 开头10%
                position_score = 2
            elif i > len(subtitles) * 0.9:  # 结尾10%
                position_score = 1.5
            # 长度权重（适中长度的句子信息量更大）
            length = len(content)
            length_score = 1.0
            if 10 < length < 50:
                length_score = 1.5
            elif length > 80:
                length_score = 0.8
            
            total_score = (keyword_hits * 3 + position_score) * length_score
            scored_sentences.append((total_score, sub, i))
        
        # 取得分最高的8个句子，按时间顺序排列
        top_sentences = sorted(scored_sentences, key=lambda x: x[0], reverse=True)[:8]
        top_sentences = sorted(top_sentences, key=lambda x: x[2])
        
        for score, sub, idx in top_sentences:
            time_sec = int(sub["from"])
            time_str = f"{time_sec//60}:{time_sec%60:02d}"
            summary["key_points"].append({
                "time": time_str,
                "time_sec": time_sec,
                "content": sub["content"],
                "score": round(score, 1),
            })
    
    # 4. 内容主题分类（基于高频词）
    topic_keywords = {
        "教程/教学": ["教程", "教学", "入门", "零基础", "步骤", "方法", "技巧", "攻略", "指南", "怎么", "如何"],
        "游戏/娱乐": ["游戏", "玩", "攻略", "角色", "技能", "副本", "boss", "通关", "上分", "段位"],
        "科技/数码": ["手机", "电脑", "芯片", "处理器", "显卡", "屏幕", "电池", "系统", "软件", "app"],
        "知识/科普": ["原理", "本质", "为什么", "分析", "研究", "数据", "实验", "证明", "科学", "技术"],
        "生活/日常": ["生活", "日常", "vlog", "美食", "旅行", "健身", "穿搭", "护肤", "宠物", "家居"],
        "影视/动漫": ["电影", "电视剧", "动漫", "动画", "解说", "剧情", "角色", "导演", "演员", "配音"],
        "音乐/舞蹈": ["音乐", "歌曲", "翻唱", "舞蹈", "演奏", "吉他", "钢琴", "rap", "唱歌", "mv"],
        "财经/职场": ["股票", "基金", "投资", "理财", "职场", "工作", "面试", "简历", "薪资", "创业"],
    }
    
    content_topics = []
    all_text = " ".join(all_texts)
    for topic, keywords in topic_keywords.items():
        hits = sum(1 for kw in keywords if kw in all_text)
        if hits >= 2:
            content_topics.append({"topic": topic, "hits": hits})
    content_topics = sorted(content_topics, key=lambda x: x["hits"], reverse=True)[:5]
    summary["content_topics"] = content_topics
    
    # 5. 观众反馈总结
    pos_count = 0
    neg_count = 0
    for c in comments[:100]:
        sentiment = analyze_sentiment(c["content"])
        if sentiment == "positive":
            pos_count += 1
        elif sentiment == "negative":
            neg_count += 1
    
    total = pos_count + neg_count
    if total > 0:
        pos_ratio = pos_count / total * 100
        if pos_ratio > 70:
            summary["audience_feedback"] = f"观众反馈整体正面（正面占比{pos_ratio:.0f}%），评论区氛围积极"
        elif pos_ratio > 50:
            summary["audience_feedback"] = f"观众反馈偏正面（正面占比{pos_ratio:.0f}%），有一定讨论度"
        elif pos_ratio > 30:
            summary["audience_feedback"] = f"观众反馈存在争议（正面占比{pos_ratio:.0f}%），评论区讨论激烈"
        else:
            summary["audience_feedback"] = f"观众反馈偏负面（正面占比{pos_ratio:.0f}%），建议谨慎观看"
    else:
        summary["audience_feedback"] = "评论样本不足，无法判断观众反馈"
    
    # 6. 估算阅读时间（基于字幕字数）
    if subtitle_data:
        char_count = len(subtitle_data["full_text"])
        summary["estimated_reading_time"] = max(1, int(char_count / 300))  # 按每分钟300字估算
    else:
        summary["estimated_reading_time"] = 0
    
    return summary


# ============================================================
# 数据分析
# ============================================================

def analyze_sentiment(text):
    """简单情感分析"""
    pos_count = sum(1 for w in POSITIVE_WORDS if w in text)
    neg_count = sum(1 for w in NEGATIVE_WORDS if w in text)
    if pos_count > neg_count:
        return "positive"
    elif neg_count > pos_count:
        return "negative"
    else:
        return "neutral"


def get_word_frequency(texts, top_n=30):
    """词频统计"""
    try:
        import jieba
        all_words = []
        for text in texts:
            if not text:
                continue
            # 去掉表情和特殊字符
            text = re.sub(r"\[.*?\]", "", text)
            text = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9]", " ", text)
            words = jieba.lcut(text)
            for w in words:
                w = w.strip()
                if len(w) > 1 and w not in STOP_WORDS and not w.isdigit():
                    all_words.append(w)
        counter = Counter(all_words)
        return counter.most_common(top_n)
    except ImportError:
        print("⚠️  未安装jieba，词频分析已跳过。执行: pip install jieba")
        return []


def analyze_comments(comments):
    """分析评论数据"""
    if not comments:
        return {}
    
    # 展开所有评论文本（主评论+楼中楼）
    all_texts = []
    all_comments_flat = []
    for c in comments:
        all_texts.append(c["content"])
        all_comments_flat.append(c)
        for sub in c["replies"]:
            all_texts.append(sub["content"])
            all_comments_flat.append(sub)
    
    # 热门评论（按点赞排序）
    hot_comments = sorted(comments, key=lambda x: x["like"], reverse=True)[:15]
    
    # 词频
    word_freq = get_word_frequency(all_texts)
    
    # 情感分析
    sentiments = {"positive": 0, "negative": 0, "neutral": 0}
    for c in all_comments_flat:
        sentiments[analyze_sentiment(c["content"])] += 1
    
    # 评论时间分布（按小时）
    hour_dist = Counter()
    for c in all_comments_flat:
        try:
            hour = int(c["ctime"].split(" ")[1].split(":")[0])
            hour_dist[hour] += 1
        except (IndexError, ValueError):
            pass
    
    return {
        "total": len(all_comments_flat),
        "main_count": len(comments),
        "sub_count": len(all_comments_flat) - len(comments),
        "hot_comments": hot_comments,
        "word_freq": word_freq,
        "sentiments": sentiments,
        "hour_dist": dict(sorted(hour_dist.items())),
        "all_texts": all_texts,
    }


def analyze_danmaku(danmakus, duration):
    """分析弹幕数据"""
    if not danmakus:
        return {}
    
    # 词频
    word_freq = get_word_frequency([d["content"] for d in danmakus])
    
    # 时间分布（按视频进度，每1%一个区间）
    time_bins = 100
    time_dist = [0] * time_bins
    for d in danmakus:
        if duration > 0:
            idx = min(int(d["time"] / duration * time_bins), time_bins - 1)
            time_dist[idx] += 1
    
    # 找弹幕高潮点（弹幕密度最高的时间段）
    peak_points = []
    threshold = sum(time_dist) / len(time_dist) * 2
    for i, count in enumerate(time_dist):
        if count > threshold:
            peak_time = int(i * duration / time_bins)
            peak_points.append({
                "time": peak_time,
                "time_str": f"{peak_time//60}:{peak_time%60:02d}",
                "count": count,
                "percent": f"{i}%"
            })
    peak_points = sorted(peak_points, key=lambda x: x["count"], reverse=True)[:10]
    
    # 高频弹幕
    danmaku_counter = Counter(d["content"] for d in danmakus)
    top_danmaku = danmaku_counter.most_common(15)
    
    # 弹幕颜色分布
    color_dist = Counter(d["color"] for d in danmakus)
    top_colors = color_dist.most_common(5)
    
    return {
        "total": len(danmakus),
        "word_freq": word_freq,
        "time_dist": time_dist,
        "peak_points": peak_points,
        "top_danmaku": top_danmaku,
        "top_colors": top_colors,
    }


# ============================================================
# HTML报告生成
# ============================================================

def generate_html_report(video_info, comment_analysis, danmaku_analysis, summary, output_path):
    """生成HTML分析报告"""
    
    # 准备数据
    comments_word_freq = comment_analysis.get("word_freq", [])
    danmaku_word_freq = danmaku_analysis.get("word_freq", [])
    hot_comments = comment_analysis.get("hot_comments", [])
    sentiments = comment_analysis.get("sentiments", {})
    hour_dist = comment_analysis.get("hour_dist", {})
    danmaku_time_dist = danmaku_analysis.get("time_dist", [])
    peak_points = danmaku_analysis.get("peak_points", [])
    top_danmaku = danmaku_analysis.get("top_danmaku", [])
    
    # 视频内容总结数据
    summary_tags = summary.get("tags", [])
    summary_key_points = summary.get("key_points", [])
    summary_high_freq = summary.get("high_freq_words", [])
    summary_topics = summary.get("content_topics", [])
    summary_feedback = summary.get("audience_feedback", "")
    summary_reading_time = summary.get("estimated_reading_time", 0)
    summary_has_subtitle = summary.get("has_subtitle", False)
    summary_subtitle_error = summary.get("subtitle_error", "")
    
    # 生成内容总结HTML
    tags_html = "".join(f'<span class="tag-item">{t}</span>' for t in summary_tags) if summary_tags else '<span style="color:#999;">暂无标签</span>'
    
    key_points_html = ""
    if summary_key_points:
        for i, kp in enumerate(summary_key_points, 1):
            key_points_html += f"""
            <div class="keypoint-item">
                <div class="keypoint-time">⏱️ {kp['time']}</div>
                <div class="keypoint-content">{kp['content']}</div>
            </div>
            """
    else:
        key_points_html = '<p style="color:#999;text-align:center;padding:20px;">暂无关键时间点（该视频可能无AI字幕）</p>'
    
    topics_html = ""
    if summary_topics:
        for t in summary_topics:
            topics_html += f'<span class="topic-badge">{t["topic"]} <small>({t["hits"]}次)</small></span>'
    else:
        topics_html = '<span style="color:#999;">无法识别主题</span>'
    
    # 格式化时长
    duration = video_info.get("duration", 0)
    duration_str = f"{duration//60}:{duration%60:02d}"
    
    # 生成热门评论HTML
    hot_comments_html = ""
    for i, c in enumerate(hot_comments, 1):
        sub_html = ""
        if c["replies"]:
            sub_html = '<div class="sub-replies">'
            for sub in c["replies"][:3]:
                sub_html += f'<div class="sub-reply"><span class="sub-user">{sub["user"]}</span>: {sub["content"]}</div>'
            if len(c["replies"]) > 3:
                sub_html += f'<div class="sub-more">...共{len(c["replies"])}条回复</div>'
            sub_html += "</div>"
        
        hot_comments_html += f"""
        <div class="comment-item">
            <div class="comment-rank">#{i}</div>
            <div class="comment-body">
                <div class="comment-header">
                    <span class="comment-user">{c['user']}</span>
                    <span class="comment-like">👍 {c['like']}</span>
                    <span class="comment-time">{c['ctime']}</span>
                </div>
                <div class="comment-content">{c['content']}</div>
                {sub_html}
            </div>
        </div>
        """
    
    # 生成高频弹幕HTML
    top_danmaku_html = ""
    for i, (content, count) in enumerate(top_danmaku, 1):
        top_danmaku_html += f"""
        <div class="danmaku-item">
            <span class="danmaku-rank">#{i}</span>
            <span class="danmaku-content">{content}</span>
            <span class="danmaku-count">{count}次</span>
        </div>
        """
    
    # 生成高潮点HTML
    peak_html = ""
    for p in peak_points:
        peak_html += f"""
        <div class="peak-item">
            <span class="peak-time">⏱️ {p['time_str']} ({p['percent']})</span>
            <span class="peak-count">{p['count']}条弹幕</span>
        </div>
        """
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>B站视频评论弹幕分析 - {video_info['title']}</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
            background: #f0f2f5;
            color: #333;
        }}
        .header {{
            background: linear-gradient(135deg, #fb7299 0%, #23ade5 100%);
            color: white;
            padding: 30px 40px;
        }}
        .header h1 {{ font-size: 24px; margin-bottom: 12px; line-height: 1.4; }}
        .video-meta {{ display: flex; gap: 24px; flex-wrap: wrap; font-size: 14px; opacity: 0.95; }}
        .video-meta span {{ display: flex; align-items: center; gap: 4px; }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 24px; }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        .stat-card {{
            background: white;
            border-radius: 10px;
            padding: 18px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.06);
            text-align: center;
        }}
        .stat-card .label {{ font-size: 13px; color: #999; margin-bottom: 6px; }}
        .stat-card .value {{ font-size: 24px; font-weight: 600; color: #fb7299; }}
        .tabs {{
            display: flex;
            gap: 4px;
            background: white;
            padding: 8px;
            border-radius: 10px;
            margin-bottom: 16px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.06);
            flex-wrap: wrap;
        }}
        .tab {{
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
            color: #666;
        }}
        .tab:hover {{ background: #f5f5f5; }}
        .tab.active {{ background: #fb7299; color: white; font-weight: 500; }}
        .chart-container {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.06);
            margin-bottom: 24px;
        }}
        .chart-container h3 {{
            font-size: 16px;
            margin-bottom: 16px;
            padding-left: 10px;
            border-left: 3px solid #fb7299;
        }}
        .chart {{ width: 100%; height: 400px; }}
        .hidden {{ display: none; }}
        .comment-item {{
            display: flex;
            gap: 12px;
            padding: 16px;
            border-bottom: 1px solid #f0f0f0;
        }}
        .comment-rank {{
            width: 36px;
            height: 36px;
            background: linear-gradient(135deg, #fb7299, #ff9c6e);
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 13px;
            flex-shrink: 0;
        }}
        .comment-body {{ flex: 1; }}
        .comment-header {{
            display: flex;
            gap: 12px;
            margin-bottom: 6px;
            font-size: 13px;
        }}
        .comment-user {{ color: #fb7299; font-weight: 500; }}
        .comment-like {{ color: #999; }}
        .comment-time {{ color: #bbb; margin-left: auto; }}
        .comment-content {{ font-size: 14px; line-height: 1.6; color: #333; }}
        .sub-replies {{
            margin-top: 10px;
            padding: 10px 14px;
            background: #fafafa;
            border-radius: 8px;
        }}
        .sub-reply {{ font-size: 13px; color: #666; margin-bottom: 4px; }}
        .sub-user {{ color: #23ade5; }}
        .sub-more {{ font-size: 12px; color: #999; margin-top: 4px; }}
        .danmaku-item {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 14px;
            border-bottom: 1px solid #f0f0f0;
        }}
        .danmaku-rank {{
            width: 28px;
            height: 28px;
            background: #23ade5;
            color: white;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: 600;
        }}
        .danmaku-content {{ flex: 1; font-size: 14px; }}
        .danmaku-count {{ color: #999; font-size: 13px; }}
        .peak-item {{
            display: flex;
            justify-content: space-between;
            padding: 10px 14px;
            background: #fff5f7;
            border-radius: 8px;
            margin-bottom: 8px;
            font-size: 14px;
        }}
        .peak-time {{ color: #fb7299; font-weight: 500; }}
        .peak-count {{ color: #666; }}
        .insight-box {{
            background: linear-gradient(135deg, #fff5f7 0%, #e6f7ff 100%);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 24px;
            border-left: 4px solid #fb7299;
        }}
        .insight-box h4 {{ font-size: 15px; margin-bottom: 12px; color: #fb7299; }}
        .insight-box ul {{ padding-left: 20px; }}
        .insight-box li {{ margin-bottom: 8px; font-size: 14px; line-height: 1.6; }}
        /* 视频内容总结样式 */
        .summary-overview {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        .summary-card {{
            background: #fff;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }}
        .summary-card .icon {{ font-size: 28px; margin-bottom: 8px; }}
        .summary-card .value {{ font-size: 24px; font-weight: 700; color: #fb7299; }}
        .summary-card .label {{ font-size: 13px; color: #999; margin-top: 4px; }}
        .tags-container {{ margin-bottom: 20px; }}
        .tag-item {{
            display: inline-block;
            background: #fff0f5;
            color: #fb7299;
            padding: 4px 12px;
            border-radius: 16px;
            font-size: 13px;
            margin: 4px;
        }}
        .topic-badge {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 13px;
            margin: 4px;
        }}
        .topic-badge small {{ opacity: 0.8; }}
        .keypoint-item {{
            display: flex;
            gap: 16px;
            padding: 14px 16px;
            background: #fafafa;
            border-radius: 8px;
            margin-bottom: 10px;
            border-left: 3px solid #fb7299;
        }}
        .keypoint-time {{
            flex-shrink: 0;
            color: #fb7299;
            font-weight: 600;
            font-size: 14px;
            min-width: 70px;
        }}
        .keypoint-content {{ flex: 1; font-size: 14px; line-height: 1.6; color: #333; }}
        .feedback-box {{
            background: linear-gradient(135deg, #e6f7ff 0%, #f0f9ff 100%);
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            border-left: 4px solid #1890ff;
        }}
        .feedback-box h4 {{ color: #1890ff; margin-bottom: 10px; }}
        .subtitle-warning {{
            background: #fffbe6;
            border: 1px solid #ffe58f;
            border-radius: 8px;
            padding: 12px 16px;
            margin-bottom: 16px;
            color: #ad6800;
            font-size: 13px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 {video_info['title']}</h1>
        <div class="video-meta">
            <span>👤 UP主: {video_info['owner']}</span>
            <span>▶️ 播放: {video_info['view']:,}</span>
            <span>💬 评论: {video_info['reply']:,}</span>
            <span>🎯 弹幕: {video_info['danmaku']:,}</span>
            <span>👍 点赞: {video_info['like']:,}</span>
            <span>⏱️ 时长: {duration_str}</span>
            <span>📅 发布: {video_info['pubdate']}</span>
        </div>
    </div>

    <div class="container">
        <!-- 统计卡片 -->
        <div class="stats-grid">
            <div class="stat-card"><div class="label">爬取评论</div><div class="value">{comment_analysis.get('total', 0)}</div><div class="sub">主评论 {comment_analysis.get('main_count', 0)} + 回复 {comment_analysis.get('sub_count', 0)}</div></div>
            <div class="stat-card"><div class="label">爬取弹幕</div><div class="value">{danmaku_analysis.get('total', 0)}</div><div class="sub">条弹幕</div></div>
            <div class="stat-card"><div class="label">正面评论</div><div class="value">{sentiments.get('positive', 0)}</div><div class="sub">占比 {sentiments.get('positive',0)/max(comment_analysis.get('total',1),1)*100:.1f}%</div></div>
            <div class="stat-card"><div class="label">负面评论</div><div class="value">{sentiments.get('negative', 0)}</div><div class="sub">占比 {sentiments.get('negative',0)/max(comment_analysis.get('total',1),1)*100:.1f}%</div></div>
            <div class="stat-card"><div class="label">弹幕高潮点</div><div class="value">{len(peak_points)}</div><div class="sub">个高能时刻</div></div>
        </div>

        <!-- 洞察 -->
        <div class="insight-box">
            <h4>💡 内容洞察</h4>
            <ul>
                <li>📌 评论区最热关键词：「<strong>{comments_word_freq[0][0] if comments_word_freq else '无'}</strong>」（{comments_word_freq[0][1] if comments_word_freq else 0}次）</li>
                <li>🎯 弹幕最热关键词：「<strong>{danmaku_word_freq[0][0] if danmaku_word_freq else '无'}</strong>」（{danmaku_word_freq[0][1] if danmaku_word_freq else 0}次）</li>
                <li>🔥 弹幕最高潮时刻：<strong>{peak_points[0]['time_str'] if peak_points else '无'}</strong>（{peak_points[0]['count'] if peak_points else 0}条弹幕）</li>
                <li>👍 最热评论：<strong>{hot_comments[0]['user'] if hot_comments else '无'}</strong>（{hot_comments[0]['like'] if hot_comments else 0}赞）</li>
                <li>📈 评论情感倾向：正面 {sentiments.get('positive',0)} / 中性 {sentiments.get('neutral',0)} / 负面 {sentiments.get('negative',0)}</li>
            </ul>
        </div>

        <!-- 标签页 -->
        <div class="tabs">
            <div class="tab active" data-tab="summary">📝 视频内容总结</div>
            <div class="tab" data-tab="comment-word">💬 评论词频</div>
            <div class="tab" data-tab="comment-hot">🔥 热门评论</div>
            <div class="tab" data-tab="comment-sentiment">😊 情感分析</div>
            <div class="tab" data-tab="danmaku-word">🎯 弹幕词频</div>
            <div class="tab" data-tab="danmaku-time">⏱️ 弹幕时间分布</div>
            <div class="tab" data-tab="danmaku-top">📝 高频弹幕</div>
        </div>

        <!-- 视频内容总结 -->
        <div class="chart-container" id="panel-summary">
            <h3>📝 视频内容智能总结</h3>
            {f'<div class="subtitle-warning">⚠️ {summary_subtitle_error}</div>' if summary_subtitle_error else ''}
            
            <div class="summary-overview">
                <div class="summary-card">
                    <div class="icon">⏱️</div>
                    <div class="value">{duration_str}</div>
                    <div class="label">视频时长</div>
                </div>
                <div class="summary-card">
                    <div class="icon">📖</div>
                    <div class="value">{summary_reading_time if summary_reading_time > 0 else '-'}</div>
                    <div class="label">预计阅读时间(分钟)</div>
                </div>
                <div class="summary-card">
                    <div class="icon">🏷️</div>
                    <div class="value">{len(summary_tags)}</div>
                    <div class="label">视频标签</div>
                </div>
                <div class="summary-card">
                    <div class="icon">🎯</div>
                    <div class="value">{len(summary_key_points)}</div>
                    <div class="label">关键时间点</div>
                </div>
            </div>

            <h4 style="margin-bottom:12px;color:#333;">🏷️ 视频标签</h4>
            <div class="tags-container">{tags_html}</div>

            <h4 style="margin:20px 0 12px;color:#333;">📂 内容主题识别</h4>
            <div style="margin-bottom:20px;">{topics_html}</div>

            <h4 style="margin:20px 0 12px;color:#333;">⏰ 关键内容时间线（基于字幕智能提取）</h4>
            {key_points_html}

            <div class="feedback-box">
                <h4>💬 观众反馈总结</h4>
                <p style="font-size:14px;line-height:1.6;color:#333;">{summary_feedback}</p>
            </div>
        </div>

        <!-- 评论词频 -->
        <div class="chart-container hidden" id="panel-comment-word">
            <h3>评论区关键词TOP30</h3>
            <div class="chart" id="chart-comment-word"></div>
        </div>

        <!-- 热门评论 -->
        <div class="chart-container hidden" id="panel-comment-hot">
            <h3>热门评论TOP15（按点赞排序）</h3>
            {hot_comments_html}
        </div>

        <!-- 情感分析 -->
        <div class="chart-container hidden" id="panel-comment-sentiment">
            <h3>评论情感分布</h3>
            <div class="chart" id="chart-sentiment"></div>
        </div>

        <!-- 弹幕词频 -->
        <div class="chart-container hidden" id="panel-danmaku-word">
            <h3>弹幕关键词TOP30</h3>
            <div class="chart" id="chart-danmaku-word"></div>
        </div>

        <!-- 弹幕时间分布 -->
        <div class="chart-container hidden" id="panel-danmaku-time">
            <h3>弹幕时间分布（视频进度）</h3>
            <div class="chart" id="chart-danmaku-time"></div>
            <div style="margin-top:20px;">
                <h4 style="margin-bottom:12px;color:#333;">🔥 弹幕高潮点（高能时刻）</h4>
                {peak_html if peak_html else '<p style="color:#999;">暂无明显高潮点</p>'}
            </div>
        </div>

        <!-- 高频弹幕 -->
        <div class="chart-container hidden" id="panel-danmaku-top">
            <h3>高频弹幕TOP15</h3>
            {top_danmaku_html if top_danmaku_html else '<p style="color:#999;">暂无弹幕数据</p>'}
        </div>
    </div>

    <script>
        // 标签页切换
        document.querySelectorAll('.tab').forEach(tab => {{
            tab.addEventListener('click', () => {{
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                const name = tab.dataset.tab;
                ['summary','comment-word','comment-hot','comment-sentiment','danmaku-word','danmaku-time','danmaku-top'].forEach(n => {{
                    document.getElementById('panel-' + n).classList.toggle('hidden', n !== name);
                }});
                setTimeout(() => window.dispatchEvent(new Event('resize')), 100);
            }});
        }});

        // 评论词频图
        const commentWords = {json.dumps([[w,c] for w,c in comments_word_freq], ensure_ascii=False)};
        if (commentWords.length > 0) {{
            const chart1 = echarts.init(document.getElementById('chart-comment-word'));
            chart1.setOption({{
                tooltip: {{ trigger: 'axis', formatter: '{{b}}: {{c}}次' }},
                grid: {{ left: 100, right: 40, top: 20, bottom: 30 }},
                xAxis: {{ type: 'value', name: '出现次数' }},
                yAxis: {{ type: 'category', data: commentWords.map(w=>w[0]).reverse(), axisLabel: {{fontSize:11}} }},
                series: [{{
                    data: commentWords.map(w=>w[1]).reverse(),
                    type: 'bar',
                    itemStyle: {{
                        color: new echarts.graphic.LinearGradient(0,0,1,0,[
                            {{offset:0,color:'#fb7299'}},{{offset:1,color:'#ff9c6e'}}
                        ]),
                        borderRadius: [0,4,4,0]
                    }}
                }}],
                dataZoom: [{{type:'slider',yAxisIndex:0,orient:'vertical',right:10,width:15}}]
            }});
        }}

        // 情感分析图
        const sentimentData = [
            {{name:'正面', value:{sentiments.get('positive',0)}, itemStyle:{{color:'#52c41a'}}}},
            {{name:'中性', value:{sentiments.get('neutral',0)}, itemStyle:{{color:'#1890ff'}}}},
            {{name:'负面', value:{sentiments.get('negative',0)}, itemStyle:{{color:'#ff4d4f'}}}}
        ];
        const chart2 = echarts.init(document.getElementById('chart-sentiment'));
        chart2.setOption({{
            tooltip: {{ trigger: 'item', formatter: '{{b}}: {{c}}条 ({{d}}%)' }},
            legend: {{ bottom: 10 }},
            series: [{{
                type: 'pie',
                radius: ['40%','70%'],
                center: ['50%','45%'],
                itemStyle: {{ borderRadius: 8, borderColor: '#fff', borderWidth: 2 }},
                label: {{ formatter: '{{b}}\\n{{d}}%' }},
                data: sentimentData
            }}]
        }});

        // 弹幕词频图
        const danmakuWords = {json.dumps([[w,c] for w,c in danmaku_word_freq], ensure_ascii=False)};
        if (danmakuWords.length > 0) {{
            const chart3 = echarts.init(document.getElementById('chart-danmaku-word'));
            chart3.setOption({{
                tooltip: {{ trigger: 'axis', formatter: '{{b}}: {{c}}次' }},
                grid: {{ left: 100, right: 40, top: 20, bottom: 30 }},
                xAxis: {{ type: 'value', name: '出现次数' }},
                yAxis: {{ type: 'category', data: danmakuWords.map(w=>w[0]).reverse(), axisLabel: {{fontSize:11}} }},
                series: [{{
                    data: danmakuWords.map(w=>w[1]).reverse(),
                    type: 'bar',
                    itemStyle: {{
                        color: new echarts.graphic.LinearGradient(0,0,1,0,[
                            {{offset:0,color:'#23ade5'}},{{offset:1,color:'#b37feb'}}
                        ]),
                        borderRadius: [0,4,4,0]
                    }}
                }}],
                dataZoom: [{{type:'slider',yAxisIndex:0,orient:'vertical',right:10,width:15}}]
            }});
        }}

        // 弹幕时间分布图
        const danmakuTimeData = {json.dumps(danmaku_time_dist)};
        const chart4 = echarts.init(document.getElementById('chart-danmaku-time'));
        chart4.setOption({{
            tooltip: {{ trigger: 'axis', formatter: function(params) {{
                return '视频进度 ' + params[0].dataIndex + '%: ' + params[0].value + '条弹幕';
            }}}},
            grid: {{ left: 50, right: 30, top: 30, bottom: 50 }},
            xAxis: {{
                type: 'category',
                data: danmakuTimeData.map((_,i)=>i+'%'),
                axisLabel: {{ interval: 9, fontSize: 11 }}
            }},
            yAxis: {{ type: 'value', name: '弹幕数' }},
            dataZoom: [{{type:'inside'}},{{type:'slider',height:20,bottom:10}}],
            series: [{{
                data: danmakuTimeData,
                type: 'line',
                smooth: true,
                symbol: 'none',
                itemStyle: {{ color: '#23ade5' }},
                areaStyle: {{
                    color: new echarts.graphic.LinearGradient(0,0,0,1,[
                        {{offset:0,color:'rgba(35,173,229,0.4)'}},
                        {{offset:1,color:'rgba(35,173,229,0.05)'}}
                    ])
                }}
            }}]
        }});

        window.addEventListener('resize', () => {{
            [chart1, chart2, chart3, chart4].forEach(c => c && c.resize());
        }});
    </script>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_path


# ============================================================
# 主函数
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="B站视频评论&弹幕爬取分析工具")
    parser.add_argument("bvid", help="视频BV号或视频链接")
    parser.add_argument("--max-pages", type=int, default=50, help="最大爬取评论页数（默认50）")
    parser.add_argument("--output", "-o", default="", help="输出HTML文件路径")
    parser.add_argument("--no-danmaku", action="store_true", help="不爬取弹幕")
    parser.add_argument("--cookie", default="", help="B站Cookie（从浏览器复制，必填）")
    parser.add_argument("--cookie-file", default="", help="Cookie文件路径")
    args = parser.parse_args()

    # 设置Cookie
    cookie = args.cookie
    if not cookie and args.cookie_file:
        try:
            with open(args.cookie_file, "r", encoding="utf-8") as f:
                cookie = f.read().strip()
        except Exception as e:
            print(f"❌ 读取Cookie文件失败: {e}")
            sys.exit(1)
    if not cookie:
        print("⚠️  未提供Cookie，可能无法访问B站API")
        print("   获取方法：浏览器F12 → Network → 随便点个请求 → 复制Request Headers里的Cookie值")
        print("   用法：python bilibili_comment_analyzer.py BV号 --cookie \"你的Cookie\"")
    else:
        set_cookie(cookie)
        print("✅ Cookie已设置")

    bvid = extract_bvid(args.bvid)
    print(f"🎬 开始分析视频: {bvid}")

    # 1. 获取视频信息
    print("\n📺 获取视频信息...")
    video_info = get_video_info(bvid)
    if not video_info:
        print("❌ 无法获取视频信息，请检查BV号是否正确")
        sys.exit(1)
    print(f"✅ 标题: {video_info['title']}")
    print(f"✅ UP主: {video_info['owner']}")
    print(f"✅ 播放: {video_info['view']:,} | 评论: {video_info['reply']:,} | 弹幕: {video_info['danmaku']:,}")

    # 2. 爬取评论
    print(f"\n💬 开始爬取评论（最多{args.max_pages}页）...")
    comments = get_comments(video_info["aid"], max_pages=args.max_pages)
    print(f"\n✅ 爬取到 {len(comments)} 条主评论")

    # 3. 爬取弹幕
    danmakus = []
    if not args.no_danmaku:
        print("\n🎯 开始爬取弹幕...")
        danmakus = get_danmaku(video_info["cid"])
        print(f"✅ 爬取到 {len(danmakus)} 条弹幕")

    # 3.5 获取视频标签和字幕
    print("\n🏷️ 获取视频标签...")
    tags = get_video_tags(bvid)
    print(f"✅ 获取到 {len(tags)} 个标签")

    print("\n📝 获取视频AI字幕...")
    subtitle_data, subtitle_error = get_video_subtitle(bvid, video_info["cid"])
    if subtitle_data:
        print(f"✅ 获取到 {subtitle_data['count']} 条字幕")
    else:
        print(f"⚠️  {subtitle_error}")

    # 4. 数据分析
    print("\n📊 正在分析数据...")
    comment_analysis = analyze_comments(comments)
    danmaku_analysis = analyze_danmaku(danmakus, video_info["duration"])

    # 4.5 视频内容智能总结
    print("\n🧠 正在智能总结视频内容...")
    summary = summarize_video_content(video_info, subtitle_data, tags, comments, danmakus)
    print(f"✅ 提取到 {len(summary['key_points'])} 个关键时间点")
    print(f"✅ 识别到 {len(summary['content_topics'])} 个内容主题")

    # 5. 生成报告
    output_path = args.output or f"report_{bvid}.html"
    print(f"\n📝 生成HTML报告...")
    generate_html_report(video_info, comment_analysis, danmaku_analysis, summary, output_path)

    print(f"\n🎉 分析完成！报告已保存至: {output_path}")
    print(f"   用浏览器打开即可查看交互式分析报告")

    # 6. 导出原始数据（可选）
    try:
        import csv
        csv_path = output_path.replace(".html", "_comments.csv")
        with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["用户", "评论内容", "点赞数", "评论时间"])
            for c in comments:
                writer.writerow([c["user"], c["content"], c["like"], c["ctime"]])
                for sub in c["replies"]:
                    writer.writerow([sub["user"], sub["content"], sub["like"], sub["ctime"]])
        print(f"   评论数据已导出: {csv_path}")
    except Exception as e:
        print(f"   ⚠️  CSV导出失败: {e}")


if __name__ == "__main__":
    main()
