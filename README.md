# 💬 B站视频评论 & 弹幕爬取分析工具

> 输入BV号，自动爬取视频评论和弹幕，生成交互式HTML分析报告，帮你高效吸收视频内容。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)

## ✨ 功能特性

### 📥 数据爬取
- 🎬 **视频信息** — 自动获取标题、UP主、播放量、点赞数等基本信息
- 💬 **评论爬取** — 按热度排序爬取主评论+楼中楼回复，支持分页
- 🎯 **弹幕爬取** — 爬取视频全部弹幕（XML格式），包含时间、颜色、字号

### 📊 评论分析
- 🔥 **热门评论** — TOP15高赞评论，含楼中楼回复
- 🔤 **评论词频** — 评论区关键词TOP30，快速了解讨论热点
- 😊 **情感分析** — 正面/中性/负面评论占比饼图
- ⏰ **时间分布** — 评论发布时段分布

### 🎯 弹幕分析
- 🔤 **弹幕词频** — 弹幕关键词TOP30
- ⏱️ **时间分布** — 弹幕随视频进度的密度分布，识别高能时刻
- 🔥 **高潮点识别** — 自动标记弹幕密度最高的时间段
- 📝 **高频弹幕** — TOP15重复最多的弹幕内容

### 📝 内容摘要
- 自动总结评论区最热关键词
- 弹幕最高潮时刻定位
- 最热评论摘要
- 评论情感倾向分析

### 💾 导出功能
- 交互式HTML分析报告（ECharts图表）
- 评论数据CSV导出

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
# 或手动安装
pip install requests jieba
```

### 使用方法

```bash
# 基本用法（输入BV号）
python bilibili_comment_analyzer.py BV1xx411c7mD

# 输入完整视频链接也可以
python bilibili_comment_analyzer.py https://www.bilibili.com/video/BV1xx411c7mD

# 限制爬取评论页数（默认50页）
python bilibili_comment_analyzer.py BV1xx411c7mD --max-pages 20

# 指定输出文件名
python bilibili_comment_analyzer.py BV1xx411c7mD -o my_report.html

# 只爬评论，不爬弹幕
python bilibili_comment_analyzer.py BV1xx411c7mD --no-danmaku
```

### 查看报告

运行完成后，会生成 `report_{BV号}.html` 文件，用浏览器打开即可查看交互式分析报告。

## 📊 报告预览

报告包含6个分析维度：

| 标签页 | 内容 |
|--------|------|
| 💬 评论词频 | 评论区关键词TOP30横向条形图 |
| 🔥 热门评论 | TOP15高赞评论列表（含楼中楼） |
| 😊 情感分析 | 正面/中性/负面评论占比饼图 |
| 🎯 弹幕词频 | 弹幕关键词TOP30横向条形图 |
| ⏱️ 弹幕时间分布 | 弹幕密度随视频进度变化曲线+高潮点 |
| 📝 高频弹幕 | TOP15重复最多的弹幕 |

## 🛠️ 技术栈

| 技术 | 用途 |
|------|------|
| Python 3 | 核心爬取与分析逻辑 |
| requests | HTTP请求，调用B站公开API |
| jieba | 中文分词，词频统计 |
| ECharts 5 | 交互式图表渲染（HTML报告内） |
| B站开放API | 评论、弹幕、视频信息接口 |

## 📂 项目结构

```
bilibili-comment-analyzer/
├── bilibili_comment_analyzer.py   # 主程序
├── requirements.txt               # 依赖列表
├── README.md                      # 项目说明
├── LICENSE                        # MIT协议
└── examples/                      # 示例报告
    └── ...
```

## ⚙️ 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `bvid` | 视频BV号或链接（必填） | - |
| `--max-pages` | 最大爬取评论页数 | 50 |
| `--output, -o` | 输出HTML文件路径 | `report_{BV号}.html` |
| `--no-danmaku` | 不爬取弹幕 | False |

## 🔧 API说明

本工具使用B站以下公开API：

- **视频信息**: `https://api.bilibili.com/x/web-interface/view?bvid={BV号}`
- **评论列表**: `https://api.bilibili.com/x/v2/reply/main?type=1&oid={aid}&mode=3`
- **弹幕XML**: `https://comment.bilibili.com/{cid}.xml`

> ⚠️ 请合理控制爬取频率，避免对B站服务器造成压力。建议单视频爬取间隔不低于0.5秒。

## 📝 使用场景

- 🎓 **学习视频** — 快速了解其他观众的疑问和讨论重点
- 🎮 **游戏攻略** — 查看评论区的补充技巧和彩蛋
- 🎬 **影视解说** — 了解观众反馈和争议点
- 📺 **知识科普** — 提取高频问题，针对性补充学习
- 🔬 **内容分析** — 分析热门视频的观众互动模式

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交修改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源协议。

## ⚠️ 免责声明

- 本工具仅供学习和研究使用
- 请遵守B站的用户协议和相关法律法规
- 请勿用于商业用途或大规模爬取
- 使用本工具产生的任何后果由使用者自行承担

---

**如果这个工具对你有帮助，欢迎给个 ⭐ Star 支持一下！**
