# 🌟 GitHub Trending Daily — 每日 / 每周 / 每月开源热榜

每天早上 6 点（北京时间）自动抓取 **GitHub 热门开源项目 Top 10**，生成**日 / 周 / 月**三个维度的中英文双语 Markdown 报告，并通过 **GitHub Pages（项目级）** 发布为 Web 应用。

**在线预览**：https://liudonghua123.github.io/github-trending-daily/

## ✨ 功能

- ⏰ **全自动定时**：GitHub Actions 每天 UTC 22:00（北京时间 6:00）运行
- 📅 **三个榜单维度**：
  - 🌱 **每日新星榜**：前一天新建且 star 最多的 10 个仓库
  - 🔥 **每周热榜**：过去 7 天 star ≥ 100 且最活跃的 10 个仓库
  - 👑 **月度热榜**：过去 30 天 star ≥ 100 且最活跃的 10 个仓库
- 🌏 **双语报告**：每期生成 `-zh.md`（中文）与 `-en.md`（英文）两份报告
- 🖥️ **Web App**：动态 SVG logo、首页焦点卡片（榜首 + TOP 2-10 快览）、周期 Tab 切换、中英文切换
- 🚀 **自动发布**：报告生成后自动 commit + push + 部署 Pages

## 📁 项目结构

```
github-trending-daily/
├── index.html              # Web 应用（SPA，含动态 logo 与焦点卡片）
├── scripts/
│   └── fetch_trending.py   # 抓取 + 报告生成脚本（支持 --period daily/weekly/monthly）
├── reports/                # 生成的报告（自动更新）
│   ├── index.json          # 报告索引 {daily, weekly, monthly}
│   └── {period}-YYYY-MM-DD-{zh,en}.md
└── .github/workflows/
    └── daily.yml           # 定时抓取 + Pages 部署
```

## 🛠️ 本地运行

```bash
# 需要 GH_TOKEN 以避免 GitHub API 限流（60 次/小时）
export GH_TOKEN=$(gh auth token)

python scripts/fetch_trending.py --period daily --backfill 6   # 近 7 天日榜
python scripts/fetch_trending.py --period weekly --backfill 6  # 近 7 天周榜
python scripts/fetch_trending.py --period monthly              # 月榜
```

## ⚙️ 手动触发

在 GitHub 仓库 Actions 页面选择 "Daily Report" → "Run workflow" 即可手动补跑。

---

*Auto-generated daily by GitHub Actions.*
