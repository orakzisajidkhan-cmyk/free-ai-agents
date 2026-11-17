"""
News Summarizer Agent — NO-KEY version (free).

Original: LangChain + GPT-4o-mini + NewsAPI key (mock data without a key).
This version: NO API keys at all, NO paid services, NO LangChain, NO LLM.

  Fetch:    Google News RSS (free, no key) + DuckDuckGo Lite fallback
            (free, no key, via curl — DDG returns an empty 202 page to
            python-requests in this sandbox).
  Summarise: extractive, deterministic — no LLM. It quotes the real
             headlines/descriptions, groups them into a Top Story,
             Key Themes (from words that actually repeat across
             headlines) and a headlines list, with source links.
             It does NOT invent stories, numbers or quotes; if no news
             is fetched, it says so.

Usage:
    python3 agent.py --topic "artificial intelligence"
    python3 agent.py --topic "climate change" --count 10

Only dependency: requests (already installed here). No .env needed.
The original key-based version is kept as agent-original.py.
"""

import argparse
import html
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from urllib.parse import quote_plus, unquote

import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}

STOPWORDS = set("""a an the and or of to in on for with at by from as is are was were be
been it its this that these those we you they he she his her their our your
new more over under after before between into about said says will would can
could should may might must also just now today yesterday here there what
when who how why not no yes if then than so such per via amid among""".split())


def clean(text):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", text or ""))).strip()


def fetch_google_news_rss(topic, count=5):
    """Google News RSS — free, no key. Returns [{title, description, url, source, published}]."""
    url = ("https://news.google.com/rss/search?q=" + quote_plus(topic) +
           "&hl=en-US&gl=US&ceid=US:en")
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    root = ET.fromstring(r.content)
    out = []
    for item in root.iter("item"):
        title = clean(item.findtext("title"))
        desc = clean(item.findtext("description"))
        link = (item.findtext("link") or "").strip()
        pub = clean(item.findtext("pubDate"))
        source_el = item.find("source")
        source = clean(source_el.text) if source_el is not None else ""
        if title:
            out.append({"title": title, "description": desc, "url": link,
                        "source": source, "published": pub})
        if len(out) >= count:
            break
    return out


def ddg_fallback(topic, count=5):
    """DuckDuckGo Lite via curl — free, no key. Headlines only, no dates."""
    try:
        page = subprocess.check_output(
            ["curl", "-s", "-A", HEADERS["User-Agent"], "-m", "20",
             "https://lite.duckduckgo.com/lite/?q=" + quote_plus(topic + " news")],
            text=True, timeout=25)
    except Exception:
        return []
    pat = (r"""<a[^>]*href="([^"]+)"[^>]*class=['"]result-link['"][^>]*>(.*?)</a>"""
           r""".*?<td class=['"]result-snippet['"][^>]*>(.*?)</td>""")
    out = []
    for href, title, snippet in re.findall(pat, page, re.S):
        m = re.search(r"uddg=([^&]+)", href)
        if m:
            href = unquote(m.group(1))
        if href.startswith("//"):
            href = "https:" + href
        out.append({"title": clean(title), "description": clean(snippet),
                    "url": href, "source": "", "published": ""})
        if len(out) >= count:
            break
    return out


def key_themes(articles, topic, n=3):
    """Words that actually repeat across headlines (minus stopwords/topic)."""
    topic_words = set(re.findall(r"[a-z]{3,}", topic.lower()))
    words = Counter()
    for a in articles:
        for w in re.findall(r"[a-z]{3,}", a["title"].lower()):
            if w not in STOPWORDS and w not in topic_words:
                words[w] += 1
    return [w for w, c in words.most_common(n) if c >= 2]


def briefing(topic, articles):
    top = articles[0]
    lines = []
    lines.append("## Top Story")
    lines.append(f"- **{top['title']}**" + (f" — {top['source']}" if top["source"] else ""))
    desc = top["description"]
    # Google News descriptions are often just the title again (with the
    # source name shuffled in) — compare punctuation-free to catch that.
    norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
    if desc and not norm(desc).startswith(norm(top["title"])[:50]):
        lines.append(f"  {desc}")
    lines.append(f"  {top['url']}")
    if top["published"]:
        lines.append(f"  Published: {top['published']}")
    themes = key_themes(articles, topic)
    lines.append("\n## Key Themes")
    if themes:
        for t in themes:
            hits = [a for a in articles if t in a["title"].lower()]
            lines.append(f"- **{t}** — appears in {len(hits)} headline(s), e.g. “{hits[0]['title']}”")
    else:
        lines.append("- No single word repeats across these headlines — the stories cover different angles.")
    lines.append("\n## What to Watch")
    lines.append("- These are the latest headlines found; follow the source links above for the full story.")
    lines.append("- Re-run with the same topic later — Google News RSS returns the newest items first.")
    lines.append("\n## Quick Headlines")
    for i, a in enumerate(articles, 1):
        src = f" ({a['source']})" if a["source"] else ""
        lines.append(f"{i}. {a['title']}{src} — {a['url']}")
    lines.append("\n_Note: extractive briefing from live Google News RSS headlines — "
                 "no LLM was used, so nothing here is rewritten or invented._")
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description="News Summarizer Agent (no keys, free)")
    p.add_argument("--topic", default="artificial intelligence", help="News topic to search")
    p.add_argument("--count", type=int, default=5, help="Number of articles to fetch")
    args = p.parse_args()

    print(f"\n📰 Fetching news about: {args.topic}\n", flush=True)
    articles = []
    try:
        articles = fetch_google_news_rss(args.topic, args.count)
    except Exception as e:
        print(f"Google News RSS failed ({e}); trying DuckDuckGo…", file=sys.stderr)
    if not articles:
        articles = ddg_fallback(args.topic, args.count)
    print(f"✅ Found {len(articles)} articles")

    print("\n" + "=" * 60)
    print(f"📋 NEWS BRIEFING: {args.topic.upper()}")
    print("=" * 60)
    if not articles:
        print("No news found. Check the topic / connection and try again.")
        return 1
    print(briefing(args.topic, articles))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
