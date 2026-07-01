#!/usr/bin/env python3
"""
itch.io Furry + Gay/LGBT 游戏爬虫
同时爬取 tag-furry/tag-gay 和 tag-furry/tag-lgbt 两个标签组合，
按 URL 去重合并，保存为 CSV。

依赖: pip install beautifulsoup4
用法:
  python itch_furry_gay_scraper.py              # 爬取全部
  python itch_furry_gay_scraper.py 1 5           # 只爬第1~5页
  python itch_furry_gay_scraper.py 3             # 从第3页爬到末尾
"""

import csv
import os
import re
import subprocess
import sys
import tempfile
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# 两个标签组合，合并去重
TAG_URLS = [
    ("Gay",  "https://itch.io/games/tag-furry/tag-gay"),
    ("LGBT", "https://itch.io/games/tag-furry/tag-lgbt"),
]
OUTPUT_FILE = "itch_furry_gay_games.csv"
DELAY = 1.5          # 每页请求间隔（秒）
MAX_PAGES = 200      # 最大页数安全上限
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def fetch_html(url: str, page: int) -> str:
    """用 curl 抓取页面，返回 UTF-8 解码后的 HTML 文本。"""
    tmp = tempfile.NamedTemporaryFile(
        suffix=".html", delete=False, dir="/sdcard/Download"
    )
    tmp_path = tmp.name
    tmp.close()

    full_url = f"{url}?page={page}"
    try:
        result = subprocess.run(
            [
                "curl", "-s", "-L",
                "-H", f"User-Agent: {UA}",
                "-H", "Accept: text/html,application/xhtml+xml",
                "-H", "Accept-Language: en-US,en;q=0.9",
                "-o", tmp_path,
                "-w", "%{http_code}",
                "--connect-timeout", "15",
                "--max-time", "30",
                full_url,
            ],
            capture_output=True,
            text=True,
            timeout=45,
        )
        http_code = result.stdout.strip()
        if http_code and not http_code.startswith("2"):
            print(f"[!] HTTP {http_code} for page {page}")
            return ""

        with open(tmp_path, "r", encoding="utf-8", errors="replace") as f:
            html = f.read()
        return html
    except Exception as e:
        print(f"[!] curl 请求失败 (page {page}): {e}")
        return ""
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def has_next_page(soup: BeautifulSoup) -> bool:
    """检查页面是否有 'Next page' 链接。"""
    next_link = soup.find("a", string=re.compile(r"Next\s*page", re.I))
    return next_link is not None


def parse_games(soup: BeautifulSoup) -> list[dict]:
    """
    解析单页 HTML，提取游戏名称和网址。

    itch.io 游戏列表页结构:
      <div class="game_cell" data-game_id="...">
        <div class="game_title">
          <a class="title game_link" href="https://xxx.itch.io/game">游戏名称</a>
        </div>
      </div>
    """
    games = []
    seen_urls = set()

    for cell in soup.select(".game_cell"):
        title_tag = cell.select_one("a.title")
        if not title_tag:
            title_tag = cell.select_one(".game_title a")

        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        url = title_tag.get("href", "")

        if url and not url.startswith("http"):
            url = urljoin("https://itch.io", url)

        if not title or not url or url in seen_urls:
            continue

        if title in ("GIF", "Play in browser", "Download"):
            continue

        seen_urls.add(url)
        games.append({"name": title, "url": url})

    return games


def scrape_one_tag(tag_label: str, base_url: str,
                   start_page: int, end_page: int,
                   seen_urls: set, all_games: list) -> int:
    """爬取单个标签组合的所有页面，返回新增游戏数。"""
    print(f"\n{'='*60}")
    print(f"[*] 开始爬取标签: Furry + {tag_label}")
    print(f"    URL: {base_url}")
    print(f"{'='*60}")

    page = start_page
    empty_count = 0
    new_total = 0

    while page <= end_page:
        if page > start_page:
            time.sleep(DELAY)

        print(f"[*] [{tag_label}] 请求第 {page} 页...")
        html = fetch_html(base_url, page)

        if not html:
            print(f"[!] 第 {page} 页无内容，重试中...")
            time.sleep(3)
            html = fetch_html(base_url, page)
            if not html:
                print(f"[!] 重试失败，跳过第 {page} 页")
                page += 1
                continue

        soup = BeautifulSoup(html, "html.parser")
        games = parse_games(soup)

        if not games:
            empty_count += 1
            print(f"[!] 第 {page} 页未提取到游戏")
            if empty_count >= 2:
                print("[!] 连续 2 页无结果，判定已到末尾")
                break
        else:
            empty_count = 0

        new_count = 0
        for g in games:
            if g["url"] not in seen_urls:
                seen_urls.add(g["url"])
                all_games.append(g)
                new_count += 1
                new_total += 1

        print(f"    -> 本页 {len(games)} 个游戏，新增 {new_count} 个，累计 {len(all_games)} 个")

        if not has_next_page(soup):
            print(f"[*] 第 {page} 页无 'Next page' 链接，已到最后一页")
            break

        page += 1

    print(f"[*] [{tag_label}] 完成，新增 {new_total} 个游戏")
    return new_total


def scrape(start_page: int = 1, end_page: int = None):
    """主爬取流程：依次爬取所有标签组合，去重合并。"""
    all_games = []
    seen_urls = set()

    if end_page is None:
        end_page = MAX_PAGES

    print(f"[*] 将爬取 {len(TAG_URLS)} 个标签组合，最大 {MAX_PAGES} 页/组合")

    for tag_label, tag_url in TAG_URLS:
        scrape_one_tag(tag_label, tag_url, start_page, end_page,
                       seen_urls, all_games)

    # 写入 CSV
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "url"])
        writer.writeheader()
        writer.writerows(all_games)

    print(f"\n{'='*60}")
    print(f"[✓] 全部完成！共 {len(all_games)} 个游戏（去重合并），已保存到 {OUTPUT_FILE}")
    print(f"{'='*60}")
    return all_games


if __name__ == "__main__":
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    end = int(sys.argv[2]) if len(sys.argv) > 2 else None
    scrape(start_page=start, end_page=end)