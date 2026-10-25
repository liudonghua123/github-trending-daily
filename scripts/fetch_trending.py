"""GitHub Trending Daily 报告生成器（daily / weekly / monthly）.

抓取 GitHub 上某个时间维度内 star 排名前 10 的开源项目，生成中英文双语 Markdown 报告。

周期口径（均为 GitHub Search API 的客观排序）：
- daily   : created:>前一天        —— 前一天新建且 star 最多的仓库（新星榜）
- weekly  : pushed:>一周前 stars:>=100 + sort=stars   —— 过去 7 天最活跃的高星项目
- monthly : pushed:>一个月前 stars:>=100 + sort=stars —— 过去 30 天最活跃的高星项目
"""

import json
import os
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

API_URL = "https://api.github.com/search/repositories"
PER_PAGE = 10
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(REPO_ROOT, "reports")


def _headers():
    h = {"User-Agent": "github-trending-daily-bot", "Accept": "application/vnd.github+json"}
    # 有 token 用 token，速率从 60/h 提升到 5000/h
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def fetch_top_repos(period: str, day: datetime, per_page: int = PER_PAGE):
    if period == "daily":
        q = f"created:>={day.date().isoformat()}"
    elif period == "weekly":
        since = (day - timedelta(days=7)).date().isoformat()
        q = f"pushed:>={since} stars:>=100"
    elif period == "monthly":
        since = (day - timedelta(days=30)).date().isoformat()
        q = f"pushed:>={since} stars:>=100"
    else:
        raise ValueError(f"unknown period: {period}")
    params = f"?q={urllib.parse.quote(q)}&sort=stars&order=desc&per_page={per_page}"
    last_err = None
    for attempt in range(3):
        req = urllib.request.Request(API_URL + params, headers=_headers())
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data.get("items", [])
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code in (403, 429):  # 限流，退避重试
                wait = 15 * (attempt + 1)
                print(f"rate limited ({e.code}), retry in {wait}s...")
                time.sleep(wait)
            else:
                raise
    raise last_err


def fmt_num(n) -> str:
    return f"{n:,}" if isinstance(n, int) else str(n)


def star_comment(stars: int) -> tuple[str, str]:
    """返回 (中文点评, 英文点评)"""
    if stars >= 100000:
        return "传奇殿堂 👑", "Legendary 👑"
    if stars >= 10000:
        return "现象级 🔥", "Phenomenal 🔥"
    if stars >= 1000:
        return "持续升温 📈", "Trending ⭐"
    return "新星萌芽 🌱", "Rising 🌱"


def repo_row(repo, rank: int) -> dict:
    lang = repo.get("language") or "Other"
    return {
        "rank": rank,
        "full_name": repo["full_name"],
        "url": repo["html_url"],
        "stars": repo.get("stargazers_count", 0),
        "forks": repo.get("forks_count", 0),
        "watchers": repo.get("subscribers_count", 0) or 0,
        "issues": repo.get("open_issues_count", 0),
        "language": lang,
        "owner_type": repo.get("owner", {}).get("type", "-"),
        "topics": ", ".join(repo.get("topics", [])[:6]) or "-",
        "description": (repo.get("description") or "").strip(),
        "created_at": repo.get("created_at", "")[:10],
        "pushed_at": repo.get("pushed_at", "")[:10],
    }


def build_report(period: str, day: datetime, repos) -> tuple[str, str]:
    day_s = day.date().isoformat()
    gen_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    repo_url = os.environ.get("REPO_URL", "https://github.com/liudonghua123/github-trending-daily")

    meta = {
        "daily": {
            "title": f"GitHub Daily Top 10 — {day_s}",
            "zh_title": f"GitHub 每日 Top 10 — {day_s}",
            "zh_desc": "前一天新建且 star 最多",
            "en_desc": "top repos created yesterday, ranked by stars",
        },
        "weekly": {
            "title": f"GitHub Weekly Top 10 — {day_s}",
            "zh_title": f"GitHub 每周 Top 10 — {day_s}",
            "zh_desc": "过去 7 天 star ≥ 100 且最近有推送",
            "en_desc": "most starred repos (stars>=100) with pushes in the last 7 days",
        },
        "monthly": {
            "title": f"GitHub Monthly Top 10 — {day_s}",
            "zh_title": f"GitHub 每月 Top 10 — {day_s}",
            "zh_desc": "过去 30 天 star ≥ 100 且最近有推送",
            "en_desc": "most starred repos (stars>=100) with pushes in the last 30 days",
        },
    }[period]

    en_rows, zh_rows = [], []
    for i, r in enumerate(repos, 1):
        row = repo_row(r, i)
        link = f"[{row['full_name']}]({row['url']})"
        zh_c, en_c = star_comment(row["stars"])
        en_rows.append(f"| {i} | {link} | ⭐ {fmt_num(row['stars'])} | 🍴 {fmt_num(row['forks'])} | {row['language']} | {en_c} |")
        zh_rows.append(f"| {i} | {link} | ⭐ {fmt_num(row['stars'])} | 🍴 {fmt_num(row['forks'])} | {row['language']} | {zh_c} |")

    en_details, zh_details = [], []
    for i, r in enumerate(repos, 1):
        row = repo_row(r, i)
        en_details.append(
            f"### {i}. [{row['full_name']}]({row['url']})\n\n"
            f"- ⭐ Stars: **{fmt_num(row['stars'])}** | 🍴 Forks: **{fmt_num(row['forks'])}** | 👀 Watchers: **{fmt_num(row['watchers'])}** | 🐛 Open issues: **{fmt_num(row['issues'])}**\n"
            f"- 🧠 Language: **{row['language']}** | Owner: {row['owner_type']} | Created: {row['created_at']} | Last push: {row['pushed_at']}\n"
            f"- 🏷️ Topics: {row['topics']}\n\n"
            f"> {row['description'] or '_No description provided._'}\n"
        )
        zh_details.append(
            f"### {i}. [{row['full_name']}]({row['url']})\n\n"
            f"- ⭐ Star 数：**{fmt_num(row['stars'])}** | 🍴 Fork 数：**{fmt_num(row['forks'])}** | 👀 关注数：**{fmt_num(row['watchers'])}** | 🐛 未关闭 issue：**{fmt_num(row['issues'])}**\n"
            f"- 🧠 主要语言：**{row['language']}** | 归属：{row['owner_type']} | 创建：{row['created_at']} | 最近推送：{row['pushed_at']}\n"
            f"- 🏷️ 话题标签：{row['topics']}\n\n"
            f"> {row['description'] or '_（仓库未填写简介）_'}\n"
        )

    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    langs = {}
    for r in repos:
        lang = r.get("language") or "Other"
        langs[lang] = langs.get(lang, 0) + 1
    top_lang = max(langs, key=langs.get) if langs else "-"
    top_repo = repos[0]["full_name"] if repos else "-"
    top_stars = repos[0].get("stargazers_count", 0) if repos else 0

    en = f"""# 🌟 {meta['title']}

> Generated at {gen_time} · Data source: [GitHub Search API](https://docs.github.com/en/rest/search)
> Criteria: {meta['en_desc']}

## 📊 Snapshot

| Metric | Value |
| --- | --- |
| Date | {day_s} |
| Repos listed | {len(repos)} |
| Combined stars | ⭐ {fmt_num(total_stars)} |
| Hottest repo | **{top_repo}** (⭐ {fmt_num(top_stars)}) |
| Dominant language | **{top_lang}** |

## 🏆 Top 10 at a glance

| # | Repository | Stars | Forks | Language | Verdict |
| --- | --- | --- | --- | --- | --- |
{chr(10).join(en_rows)}

## 🔍 Repo details

{chr(10).join(en_details)}
---

*Auto-generated by [github-trending-daily]({repo_url}).*
"""

    zh = f"""# 🌟 {meta['zh_title']}

> 生成时间：{gen_time} · 数据来源：[GitHub Search API](https://docs.github.com/en/rest/search)
> 榜单口径：{meta['zh_desc']}

## 📊 今日快照

| 指标 | 数值 |
| --- | --- |
| 统计日期 | {day_s} |
| 上榜仓库数 | {len(repos)} |
| 合计 Star 数 | ⭐ {fmt_num(total_stars)} |
| 最火仓库 | **{top_repo}** (⭐ {fmt_num(top_stars)}) |
| 主导语言 | **{top_lang}** |

## 🏆 十强一览

| 排名 | 仓库 | Star | Fork | 语言 | 点评 |
| --- | --- | --- | --- | --- | --- |
{chr(10).join(zh_rows)}

## 🔍 仓库详情

{chr(10).join(zh_details)}
---

*本报告由 [github-trending-daily]({repo_url}) 自动生成。*
"""
    return en, zh


def build_entry(period: str, day: datetime, repos) -> dict:
    return {
        "date": day.date().isoformat(),
        "top_repo": repos[0]["full_name"] if repos else "-",
        "top_stars": repos[0].get("stargazers_count", 0) if repos else 0,
        "total_stars": sum(r.get("stargazers_count", 0) for r in repos),
        "top_repo_desc": (repos[0].get("description") or "") if repos else "",
        "top_repo_lang": (repos[0].get("language") or "Other") if repos else "-",
    }


def load_index() -> dict:
    index_path = os.path.join(REPORTS_DIR, "index.json")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
            except Exception:
                pass
    return {"daily": [], "weekly": [], "monthly": []}


def save_index(index: dict):
    index_path = os.path.join(REPORTS_DIR, "index.json")
    os.makedirs(REPORTS_DIR, exist_ok=True)
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def write_report(period: str, day: datetime):
    repos = fetch_top_repos(period, day)
    if not repos:
        print(f"WARN: no repos found for {period} {day.date().isoformat()}, skipped")
        return None
    en, zh = build_report(period, day, repos)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    day_s = day.date().isoformat()
    paths = []
    for suffix, content in (("en", en), ("zh", zh)):
        p = os.path.join(REPORTS_DIR, f"{period}-{day_s}-{suffix}.md")
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
        paths.append(p)

    index = load_index()
    bucket = index.setdefault(period, [])
    entry = build_entry(period, day, repos)
    bucket[:] = [e for e in bucket if e["date"] != day_s]
    bucket.append(entry)
    bucket.sort(key=lambda e: e["date"], reverse=True)
    save_index(index)

    print(f"OK {period} report for {day_s}: {len(repos)} repos, top={entry['top_repo']} (⭐{entry['top_stars']})")
    return paths


def main():
    import argparse

    parser = argparse.ArgumentParser(description="GitHub trending report generator")
    parser.add_argument("--period", choices=["daily", "weekly", "monthly"], default="daily")
    parser.add_argument("--date", help="YYYY-MM-DD, defaults to yesterday (UTC)")
    parser.add_argument("--backfill", type=int, default=0,
                        help="also generate reports for the previous N days")
    args = parser.parse_args()

    if args.date:
        day = datetime.fromisoformat(args.date).replace(tzinfo=timezone.utc)
    else:
        day = datetime.now(timezone.utc) - timedelta(days=1)

    days = [day - timedelta(days=i) for i in range(max(0, args.backfill) + 1)]
    for d in reversed(days):
        write_report(args.period, d)


if __name__ == "__main__":
    main()
