#!/usr/bin/env python3
"""
读取 itch_furry_gay_games.csv，生成精美的可交互 HTML 页面。
- 双列卡片布局，毛玻璃风格
- 暖色系暗色主题，高对比度
- 中文名称重排
- 搜索 + 四种排序 + 键盘快捷键
- 返回顶部按钮
- 统计面板
"""
import csv
import json
import re

CSV_FILE = "itch_furry_gay_games.csv"
HTML_FILE = "itch_furry_gay_games.html"

CJK_RE = re.compile(r'[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af\uff00-\uffef]')

def reorder_name(raw: str) -> str:
    if not CJK_RE.search(raw):
        return raw
    if not re.search(r'[A-Za-z]', raw):
        return raw
    parts = re.split(r'[/／\(（\[【]', raw)
    if len(parts) >= 2:
        cleaned = []
        for p in parts:
            p = p.rstrip(r')）】\]」')
            p = p.strip()
            if p:
                cleaned.append(p)
        if len(cleaned) >= 2:
            cjk_parts = []
            other_parts = []
            for p in cleaned:
                if CJK_RE.search(p):
                    cjk_parts.append(p)
                else:
                    other_parts.append(p)
            if cjk_parts and other_parts:
                return ' · '.join(cjk_parts + other_parts)
            elif cjk_parts:
                return ' · '.join(cjk_parts)
            else:
                return ' · '.join(other_parts)
    cjk_segments = CJK_RE.findall(raw)
    if cjk_segments:
        segments = re.findall(r'[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af\uff00-\uffef\u3000-\u303f\u2018-\u201f～～]+|[^\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af\uff00-\uffef\u3000-\u303f\u2018-\u201f～～]+', raw)
        segments = [s.strip() for s in segments if s.strip() and s.strip() not in ('/', '／', '·', ' - ', '—', '–')]
        cjk_segs = [s for s in segments if CJK_RE.search(s)]
        other_segs = [s for s in segments if not CJK_RE.search(s)]
        if cjk_segs and other_segs:
            cjk_text = ' '.join(cjk_segs).strip()
            other_text = ' '.join(other_segs).strip()
            other_text = other_text.lstrip('· -—').rstrip()
            cjk_text = cjk_text.strip()
            if cjk_text and other_text:
                return f"{cjk_text} · {other_text}"
    return raw

games = []
with open(CSV_FILE, "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row.get("name", "").strip()
        url = row.get("url", "").strip()
        if name and url:
            display_name = reorder_name(name)
            games.append({"name": display_name, "url": url})

games_json = json.dumps(games, ensure_ascii=False)

print("--- 名称处理预览（含CJK的条目）---")
for g in games:
    if CJK_RE.search(g["name"]):
        print(f"  {g['name']}")
print(f"--- 共 {len(games)} 条 ---")

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>兽游索引 · Furry Game Index</title>
<style>
  :root {
    --bg: #0f0d14;
    --bg-soft: #1a1722;
    --bg-card: rgba(34, 31, 48, 0.55);
    --bg-card-hover: rgba(42, 39, 64, 0.7);
    --bg-input: rgba(26, 24, 37, 0.6);
    --border: rgba(70, 64, 100, 0.4);
    --border-hover: rgba(106, 96, 140, 0.6);
    --accent: #e8a87c;
    --accent2: #c38ec7;
    --accent3: #85c1c5;
    --accent-glow: rgba(195, 142, 199, 0.25);
    --text: #f0ede8;
    --text-dim: #9a96b0;
    --text-faint: #6b6880;
    --radius: 16px;
    --radius-sm: 10px;
    --shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    --shadow-hover: 0 16px 48px rgba(0, 0, 0, 0.5);
    --transition: .25s cubic-bezier(.4, 0, .2, 1);
    --glass-blur: 16px;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  html { scroll-behavior: smooth; }

  body {
    font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
    color: var(--text);
    min-height: 100vh;
    line-height: 1.6;
    overflow-x: hidden;
  }

  /* ===== 动态背景层 ===== */
  .bg-layer {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    z-index: -1;
    background:
      radial-gradient(ellipse 80% 60% at 20% -5%, rgba(232, 168, 124, 0.12), transparent 60%),
      radial-gradient(ellipse 70% 50% at 85% 25%, rgba(195, 142, 199, 0.10), transparent 60%),
      radial-gradient(ellipse 60% 50% at 50% 100%, rgba(133, 193, 197, 0.08), transparent 60%),
      radial-gradient(ellipse 50% 40% at 10% 60%, rgba(180, 120, 200, 0.06), transparent 60%),
      linear-gradient(180deg, #0f0d14 0%, #0c0a10 100%);
  }
  .bg-orb {
    position: fixed;
    border-radius: 50%;
    filter: blur(80px);
    opacity: 0.35;
    z-index: -1;
    pointer-events: none;
    animation: orbFloat 20s ease-in-out infinite;
  }
  .bg-orb:nth-child(1) {
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(232, 168, 124, 0.5), transparent 70%);
    top: -100px; left: -80px;
  }
  .bg-orb:nth-child(2) {
    width: 350px; height: 350px;
    background: radial-gradient(circle, rgba(195, 142, 199, 0.4), transparent 70%);
    top: 30%; right: -60px;
    animation-delay: -5s;
  }
  .bg-orb:nth-child(3) {
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(133, 193, 197, 0.3), transparent 70%);
    bottom: -50px; left: 30%;
    animation-delay: -10s;
  }
  @keyframes orbFloat {
    0%, 100% { transform: translate(0, 0) scale(1); }
    33% { transform: translate(30px, -40px) scale(1.1); }
    66% { transform: translate(-20px, 30px) scale(0.95); }
  }

  /* ===== 顶部 Header ===== */
  header {
    text-align: center;
    padding: 56px 20px 20px;
    position: relative;
  }
  header .badge {
    display: inline-block;
    font-size: 12px;
    font-weight: 600;
    color: var(--accent3);
    background: rgba(133, 193, 197, 0.1);
    border: 1px solid rgba(133, 193, 197, 0.25);
    padding: 6px 20px;
    border-radius: 20px;
    margin-bottom: 20px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
  }
  header h1 {
    font-size: 48px;
    font-weight: 800;
    background: linear-gradient(135deg, #e8a87c, #c38ec7, #85c1c5);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 10px;
    letter-spacing: -1px;
  }
  header .subtitle {
    color: var(--text-dim);
    font-size: 15px;
    max-width: 480px;
    margin: 0 auto;
  }
  header .announcement {
    margin-top: 14px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    color: var(--accent);
    background: rgba(232, 168, 124, 0.08);
    border: 1px solid rgba(232, 168, 124, 0.2);
    padding: 8px 18px;
    border-radius: 12px;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
  }

  /* ===== 统计面板 ===== */
  .stats-bar {
    display: flex;
    justify-content: center;
    gap: 40px;
    margin-top: 28px;
    flex-wrap: wrap;
  }
  .stat-item { text-align: center; }
  .stat-item .num {
    font-size: 32px;
    font-weight: 800;
    color: var(--text);
    letter-spacing: -0.5px;
  }
  .stat-item .label {
    font-size: 11px;
    color: var(--text-faint);
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin-top: 2px;
  }

  /* ===== 工具栏（毛玻璃）===== */
  .toolbar {
    max-width: 1280px;
    margin: 36px auto 24px;
    padding: 14px 24px;
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    align-items: center;
    position: sticky;
    top: 10px;
    z-index: 100;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    background: rgba(26, 24, 37, 0.65);
    backdrop-filter: blur(20px) saturate(1.2);
    -webkit-backdrop-filter: blur(20px) saturate(1.2);
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.06);
  }
  .search-box {
    flex: 1;
    min-width: 220px;
    position: relative;
  }
  .search-box input {
    width: 100%;
    padding: 11px 16px 11px 42px;
    font-size: 14px;
    background: var(--bg-input);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    color: var(--text);
    outline: none;
    transition: border-color var(--transition), box-shadow var(--transition);
    font-family: inherit;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
  }
  .search-box input:focus {
    border-color: var(--accent2);
    box-shadow: 0 0 0 3px var(--accent-glow);
  }
  .search-box input::placeholder { color: var(--text-faint); }
  .search-box .icon {
    position: absolute;
    left: 14px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 16px;
    opacity: 0.4;
  }
  .search-box .clear-btn {
    position: absolute;
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    color: var(--text-faint);
    cursor: pointer;
    font-size: 18px;
    padding: 4px 8px;
    border-radius: 6px;
    opacity: 0;
    transition: opacity var(--transition);
  }
  .search-box .clear-btn:hover { color: var(--text); }
  .search-box.has-text .clear-btn { opacity: 1; }

  .sort-group {
    display: flex;
    gap: 6px;
    background: var(--bg-input);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 4px;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
  }
  .sort-btn {
    padding: 7px 14px;
    font-size: 13px;
    font-weight: 600;
    background: transparent;
    border: none;
    border-radius: 6px;
    color: var(--text-dim);
    cursor: pointer;
    transition: all var(--transition);
    white-space: nowrap;
    font-family: inherit;
  }
  .sort-btn:hover {
    color: var(--text);
    background: rgba(255, 255, 255, 0.06);
  }
  .sort-btn.active {
    color: var(--bg);
    background: var(--accent);
  }

  /* ===== 游戏卡片网格 ===== */
  .grid {
    max-width: 640px;
    margin: 0 auto;
    padding: 0 24px 80px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  .card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px 18px;
    transition: all var(--transition);
    position: relative;
    overflow: hidden;
    text-decoration: none;
    color: inherit;
    display: flex;
    align-items: center;
    gap: 14px;
    backdrop-filter: blur(var(--glass-blur));
    -webkit-backdrop-filter: blur(var(--glass-blur));
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.06);
  }
  .card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    background: linear-gradient(180deg, var(--accent), var(--accent2));
    opacity: 0;
    transition: opacity var(--transition);
  }
  .card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 50%;
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.04), transparent);
    pointer-events: none;
  }
  .card:hover {
    background: var(--bg-card-hover);
    border-color: var(--border-hover);
    transform: translateY(-3px);
    box-shadow: var(--shadow-hover), inset 0 1px 0 rgba(255, 255, 255, 0.08);
  }
  .card:hover::before { opacity: 1; }

  .card .index-num {
    font-size: 12px;
    font-weight: 700;
    color: var(--text-faint);
    min-width: 28px;
    text-align: right;
    flex-shrink: 0;
    font-variant-numeric: tabular-nums;
  }
  .card .emoji {
    font-size: 24px;
    flex-shrink: 0;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(195, 142, 199, 0.08);
    border: 1px solid rgba(195, 142, 199, 0.12);
    border-radius: 10px;
  }
  .card .info { flex: 1; min-width: 0; }
  .card .name {
    font-size: 14px;
    font-weight: 600;
    color: var(--text);
    word-break: break-word;
    margin-bottom: 2px;
  }
  .card .domain {
    font-size: 11px;
    color: var(--text-dim);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .card .arrow {
    font-size: 14px;
    color: var(--text-faint);
    opacity: 0;
    transform: translateX(-4px);
    transition: all var(--transition);
    flex-shrink: 0;
  }
  .card:hover .arrow {
    opacity: 1;
    transform: translateX(0);
    color: var(--accent);
  }

  /* ===== 空状态 ===== */
  .empty {
    flex: 1;
    text-align: center;
    padding: 80px 20px;
    color: var(--text-dim);
  }
  .empty .emoji { font-size: 48px; margin-bottom: 16px; }
  .empty p { font-size: 15px; }
  .empty .hint { font-size: 12px; color: var(--text-faint); margin-top: 8px; }

  /* ===== 返回顶部（毛玻璃）===== */
  .back-to-top {
    position: fixed;
    bottom: 32px;
    right: 32px;
    width: 48px;
    height: 48px;
    border: 1px solid var(--border);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 20px;
    color: var(--text-dim);
    opacity: 0;
    pointer-events: none;
    transition: all var(--transition);
    z-index: 200;
    background: rgba(26, 24, 37, 0.65);
    backdrop-filter: blur(20px) saturate(1.2);
    -webkit-backdrop-filter: blur(20px) saturate(1.2);
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.06);
  }
  .back-to-top.visible {
    opacity: 1;
    pointer-events: auto;
  }
  .back-to-top:hover {
    color: var(--accent);
    border-color: var(--accent);
    transform: translateY(-3px);
  }

  /* ===== 底部 ===== */
  footer {
    text-align: center;
    padding: 32px 24px;
    color: var(--text-faint);
    font-size: 12px;
    border-top: 1px solid var(--border);
  }
  footer a {
    color: var(--accent3);
    text-decoration: none;
    transition: color var(--transition);
  }
  footer a:hover { color: var(--accent); }

  /* ===== 入场动画 ===== */
  @keyframes fadeInUp {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
  }
  .card { animation: fadeInUp .3s ease both; }

  /* ===== 响应式 ===== */
  @media (max-width: 860px) {
    header h1 { font-size: 32px; }
    .stats-bar { gap: 28px; }
    .toolbar { padding-left: 16px; padding-right: 16px; margin-left: 12px; margin-right: 12px; }
    .grid { padding-left: 16px; padding-right: 16px; }
  }
  @media (max-width: 480px) {
    header h1 { font-size: 26px; }
    .stat-item .num { font-size: 26px; }
    .card { padding: 14px; gap: 10px; }
    .card .emoji { width: 36px; height: 36px; font-size: 20px; }
    .card .name { font-size: 13px; }
    .sort-btn { padding: 6px 10px; font-size: 12px; }
  }
</style>
</head>
<body>

<div class="bg-layer"></div>
<div class="bg-orb"></div>
<div class="bg-orb"></div>
<div class="bg-orb"></div>

<header>
  <div class="badge">itch.io</div>
  <h1>兽游索引</h1>
  <p class="subtitle">探索 592 款兽人向独立游戏 · 持续收录中</p>
  <div class="announcement">📢 添加游戏请联系 2958800782@qq.com</div>
  <div class="stats-bar">
    <div class="stat-item">
      <div class="num" id="stat-total">0</div>
      <div class="label">收录游戏</div>
    </div>
    <div class="stat-item">
      <div class="num" id="stat-shown">0</div>
      <div class="label">当前显示</div>
    </div>
  </div>
</header>

<div class="toolbar">
  <div class="search-box" id="search-wrap">
    <span class="icon">🔍</span>
    <input type="text" id="search" placeholder="搜索游戏名称或作者..." autocomplete="off">
    <button class="clear-btn" id="clear-search" title="清除">✕</button>
  </div>
  <div class="sort-group">
    <button class="sort-btn active" data-sort="default">默认</button>
    <button class="sort-btn" data-sort="az">A→Z</button>
    <button class="sort-btn" data-sort="za">Z→A</button>
    <button class="sort-btn" data-sort="domain">作者</button>
  </div>
</div>

<div class="grid" id="grid"></div>

<div class="back-to-top" id="back-top" title="返回顶部">↑</div>

<footer>
  数据来源
  <a href="https://itch.io/games/tag-furry/tag-gay" target="_blank">tag-furry/tag-gay</a>
  +
  <a href="https://itch.io/games/tag-furry/tag-lgbt" target="_blank">tag-furry/tag-lgbt</a>
  · 共 <span id="footer-count">0</span> 款游戏
  · 按 <kbd>/</kbd> 快速搜索
</footer>

<script>
const GAMES = __GAMES_JSON__;

const EMOJIS = ['🐺','🦊','🐱','🐰','🐶','🦁','🐯','🐻','🐼','🐨','🦝','🐹','🦔','🐾','🐉','🦎','🐊','🦕','🦖','🦬','🐃','🐂','🐄','🦌','🐐','🦃','🐔','🦚','🦜','🦢','🦩','🐢','🐙','🦊','🐺','🐱','🐰','🦁','🐻','🐾'];

function getEmoji(url) {
  let hash = 0;
  for (let i = 0; i < url.length; i++) {
    hash = ((hash << 5) - hash) + url.charCodeAt(i);
    hash |= 0;
  }
  return EMOJIS[Math.abs(hash) % EMOJIS.length];
}

function getDomain(url) {
  try {
    const u = new URL(url);
    return u.hostname.replace('.itch.io', '');
  } catch {
    return url;
  }
}

function escapeHtml(s) {
  const div = document.createElement('div');
  div.textContent = s;
  return div.innerHTML;
}

let currentSort = 'default';
let searchTerm = '';

function render() {
  let filtered = GAMES;

  if (searchTerm) {
    const q = searchTerm.toLowerCase();
    filtered = filtered.filter(g =>
      g.name.toLowerCase().includes(q) ||
      g.url.toLowerCase().includes(q) ||
      getDomain(g.url).toLowerCase().includes(q)
    );
  }

  if (currentSort === 'az') {
    filtered = [...filtered].sort((a, b) => a.name.localeCompare(b.name, 'zh-Hans-CN', {sensitivity: 'base'}));
  } else if (currentSort === 'za') {
    filtered = [...filtered].sort((a, b) => b.name.localeCompare(a.name, 'zh-Hans-CN', {sensitivity: 'base'}));
  } else if (currentSort === 'domain') {
    filtered = [...filtered].sort((a, b) => getDomain(a.url).localeCompare(getDomain(b.url), 'en', {sensitivity: 'base'}));
  }

  const grid = document.getElementById('grid');
  document.getElementById('stat-shown').textContent = filtered.length;

  if (filtered.length === 0) {
    grid.innerHTML = '<div class="empty"><div class="emoji">🐾</div><p>没有找到匹配的游戏</p><p class="hint">试试其他关键词？</p></div>';
    return;
  }

  const cards = filtered.map((g, i) => {
    const emoji = getEmoji(g.url);
    const domain = getDomain(g.url);
    return `<a class="card" href="${escapeHtml(g.url)}" target="_blank" rel="noopener" style="animation-delay:${Math.min(i*0.015, 0.4)}s">
      <div class="index-num">${i + 1}</div>
      <div class="emoji">${emoji}</div>
      <div class="info">
        <div class="name">${escapeHtml(g.name)}</div>
        <div class="domain">${escapeHtml(domain)}</div>
      </div>
      <span class="arrow">→</span>
    </a>`;
  }).join('');

  grid.innerHTML = cards;
}

document.getElementById('stat-total').textContent = GAMES.length;
document.getElementById('footer-count').textContent = GAMES.length;

const searchInput = document.getElementById('search');
const searchWrap = document.getElementById('search-wrap');
const clearBtn = document.getElementById('clear-search');

searchInput.addEventListener('input', function() {
  searchTerm = this.value.trim();
  searchWrap.classList.toggle('has-text', searchTerm.length > 0);
  render();
});

clearBtn.addEventListener('click', function() {
  searchInput.value = '';
  searchTerm = '';
  searchWrap.classList.remove('has-text');
  searchInput.focus();
  render();
});

document.querySelectorAll('.sort-btn').forEach(btn => {
  btn.addEventListener('click', function() {
    document.querySelectorAll('.sort-btn').forEach(b => b.classList.remove('active'));
    this.classList.add('active');
    currentSort = this.dataset.sort;
    render();
  });
});

// 返回顶部
const backTop = document.getElementById('back-top');
window.addEventListener('scroll', function() {
  backTop.classList.toggle('visible', window.scrollY > 400);
});
backTop.addEventListener('click', function() {
  window.scrollTo({ top: 0, behavior: 'smooth' });
});

// 键盘快捷键: / 聚焦搜索框
document.addEventListener('keydown', function(e) {
  if (e.key === '/' && document.activeElement !== searchInput) {
    e.preventDefault();
    searchInput.focus();
  }
  if (e.key === 'Escape' && document.activeElement === searchInput) {
    searchInput.blur();
  }
});

render();
</script>

</body>
</html>"""

final_html = HTML_TEMPLATE.replace("__GAMES_JSON__", games_json)

with open(HTML_FILE, "w", encoding="utf-8") as f:
    f.write(final_html)

print(f"[✓] 已生成 {HTML_FILE}，共 {len(games)} 个游戏")