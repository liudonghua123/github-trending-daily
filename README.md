# 🌟 GitHub Trending Daily — 每日新星榜

每天早上 6 点（北京时间）自动抓取 **GitHub 上前一天 star 排名前 10 的新开源项目**，生成中英文双语 Markdown 报告，并通过 **GitHub Pages（项目级）** 发布为 Web 应用。

**在线预览**：https://liudonghua123.github.io/github-trending-daily/

## ✨ 功能

- ⏰ **全自动定时**：GitHub Actions 每天 UTC 22:00（北京时间 6:00）运行
- 🌏 **双语报告**：每期生成 `-zh.md`（中文）与 `-en.md`（英文）两份报告
- 📊 **丰富内容**：Star/Fork/Watch/Issue 数、语言分布、话题标签、简介、热度点评
- 🖥️ **Web App**：单页应用，支持切换报告日期与中英文，地址栏可分享状态
- 🚀 **自动发布**：报告生成后自动 commit + push + 部署 Pages

## 📁 项目结构

```
github-trending-daily/
├── index.html              # Web 应用（前端 SPA）
├── scripts/
│   └── fetch_trending.py   # 抓取 + 报告生成脚本
├── reports/                # 生成的报告（自动更新）
│   ├── index.json          # 报告索引
│   └── YYYY-MM-DD-{zh,en}.md
└── .github/workflows/
    └── daily.yml           # 定时抓取 + Pages 部署
```

## 📖 报告口径

使用 GitHub Search API：`created:>前一天 + sort=stars`，即**前一天新建且 star 数最多的仓库**（“新星榜 / rising stars”）。这是“昨天”这个时间维度上唯一有官方客观排序的方式。

## 🛠️ 本地运行

```bash
python scripts/fetch_trending.py              # 抓昨天的
python scripts/fetch_trending.py 2026-10-24   # 指定日期
```

## ⚙️ 手动触发

在 GitHub 仓库 Actions 页面选择 "Daily Report" → "Run workflow" 即可手动补跑。

---

*Auto-generated daily by GitHub Actions.*
