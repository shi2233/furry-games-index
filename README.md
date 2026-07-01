<div align="center">

# 🐾 itch.io 兽游索引

### Furry Game Index — 探索 592 款兽人向独立游戏

[![Games](https://img.shields.io/badge/Games-592-e8a87c?style=for-the-badge)](https://shi2233.github.io/furry-games-index/)
[![License](https://img.shields.io/badge/License-MIT-c38ec7?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-85c1c5?style=for-the-badge)](https://www.python.org/)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Click%20Here-ff6b6b?style=for-the-badge)](https://shi2233.github.io/furry-games-index/)

</div>

---

## 📖 项目简介

这是一个自动化的 **itch.io 兽人向游戏索引工具**，包含爬虫脚本和页面生成器。

它从 itch.io 平台抓取同时带有 `furry` + `gay` / `lgbt` 标签的独立游戏，去重合并后生成一个精美的、可交互的毛玻璃风格 HTML 索引页面。

> 🎯 **目标**：让兽游爱好者能一站式搜索、浏览和发现 itch.io 上的兽人向独立游戏。

---

## ✨ 特性

### 🕷️ 爬虫脚本 (`itch_furry_gay_scraper.py`)

| 特性 | 说明 |
|---|---|
| **双标签组合抓取** | 同时爬取 `tag-furry/tag-gay` 和 `tag-furry/tag-lgbt`，最大化覆盖 |
| **自动去重** | 基于 URL 全局去重，避免重复收录 |
| **智能分页** | 自动检测 "Next page" 链接，连续 2 页空结果自动终止 |
| **请求限速** | 每页间隔 1.5 秒，对目标站点友好 |
| **断点续爬** | 支持命令行指定起始页和结束页 |
| **错误重试** | 单页失败自动重试一次 |
| **curl 后端** | 使用系统 curl 发请求，兼容无 `requests` 的环境 |

### 🎨 页面生成器 (`gen_html.py`)

| 特性 | 说明 |
|---|---|
| **毛玻璃设计** | 卡片、工具栏、按钮全部采用 `backdrop-filter` 玻璃质感 |
| **暖色暗色主题** | 渐变标题 + 动态光球背景，视觉舒适 |
| **实时搜索** | 按游戏名或作者域名即时过滤 |
| **四种排序** | 默认顺序 / A→Z / Z→A / 按作者 |
| **键盘快捷键** | `/` 聚焦搜索框，`Esc` 退出搜索 |
| **中日双语重排** | 自动识别含中文的游戏名，将中文部分前置 |
| **返回顶部** | 毛玻璃浮动按钮，滚动超过 400px 显示 |
| **入场动画** | 卡片依次淡入上滑，最多延迟 0.4s |
| **完全离线** | 纯静态 HTML，零依赖，零外部资源 |

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- `beautifulsoup4` (`pip install beautifulsoup4`)
- 系统 `curl` 命令

### 1️⃣ 爬取数据

```bash
# 爬取全部页面（默认从第 1 页到末尾）
python itch_furry_gay_scraper.py

# 只爬第 1~5 页
python itch_furry_gay_scraper.py 1 5

# 从第 3 页爬到末尾
python itch_furry_gay_scraper.py 3
```

输出文件：`itch_furry_gay_games.csv`（UTF-8 BOM 编码，兼容 Excel）

### 2️⃣ 生成页面

```bash
python gen_html.py
```

输出文件：`itch_furry_gay_games.html`（单文件，约 70KB，可直接浏览器打开）

### 3️⃣ 部署

将生成的 HTML 文件上传到任意静态托管平台即可：

- **GitHub Pages** — 推送到 repo，开启 Pages
- **Netlify Drop** — 拖拽上传，秒级部署
- **Cloudflare Pages** — 连接仓库，自动构建
- 或直接双击用浏览器打开

---

## 📁 项目结构

```
furry-games-index/
├── itch_furry_gay_scraper.py    # 爬虫脚本 — 抓取 itch.io 游戏数据
├── gen_html.py                  # 页面生成器 — CSV → 精美 HTML
├── itch_furry_gay_games.csv     # 数据文件 — 592 条游戏记录
├── itch_furry_gay_games.html    # 生成的索引页面（GitHub Pages 在线版）
├── index.html                   # 同上，Pages 入口
└── README.md                    # 你正在看的这个文件
```

---

## 📊 数据说明

| 字段 | 类型 | 说明 |
|---|---|---|
| `name` | string | 游戏名称（原始，未重排） |
| `url` | string | itch.io 游戏页面 URL |

- **数据来源**：itch.io `tag-furry/tag-gay` + `tag-furry/tag-lgbt`
- **收录标准**：游戏需同时带有 `furry` 标签和 `gay` 或 `lgbt` 标签
- **去重方式**：URL 完全匹配去重
- **CSV 编码**：UTF-8 with BOM（`utf-8-sig`）

---

## 🎮 在线演示

🔗 **[https://shi2233.github.io/furry-games-index/](https://shi2233.github.io/furry-games-index/)**

页面包含：
- 顶部统计面板（收录总数 / 当前显示数）
- 搜索框 + 排序按钮（毛玻璃工具栏，sticky 定位）
- 592 张游戏卡片（序号 + 随机动物 emoji + 游戏名 + 作者域名）
- 底部数据来源链接

---

## 🛠️ 技术细节

### 爬虫工作流程

```
开始 → 遍历标签组合 → 请求页面(curl) → 解析HTML(BeautifulSoup)
  → 提取.game_cell → 获取标题和URL → 全局去重 → 写入CSV
  → 检测Next Page → 有则继续 / 无则下一个标签 → 结束
```

### 名称重排算法

`gen_html.py` 中的 `reorder_name()` 函数会：
1. 检测游戏名是否包含 CJK 字符（中文/日文/韩文）
2. 如果同时包含 CJK 和拉丁字符，尝试按分隔符拆分
3. 将 CJK 部分前置，拉丁部分后置，用 ` · ` 连接
4. 例如：`Medicine: The Remedy of Despair / 绝望的解决手段` → `绝望的解决手段 · Medicine: The Remedy of Despair`

---

## 🤝 贡献

- 发现遗漏的游戏？请在 CSV 中手动添加（格式：`游戏名称,https://xxx.itch.io/game-name`）
- 有改进建议？欢迎提 Issue 或 PR
- 添加游戏请联系：`2958800782@qq.com`

---

## 📄 开源协议

MIT License — 随意使用、修改、分发。

数据本身来自 itch.io 公开页面，版权归原作者所有。

---

<div align="center">

**🐾 Made with curiosity for the furry gaming community 🐾**

[🌐 在线页面](https://shi2233.github.io/furry-games-index/) · [📦 GitHub Repo](https://github.com/shi2233/furry-games-index) · [🎮 itch.io](https://itch.io/games/tag-furry)

</div>
