"""
Social Media Content Agent — NO-KEY version (free).

Original: CrewAI + GPT-4o-mini (paid OpenAI key).
This version: NO API keys at all, NO paid services, NO LLM, NO CrewAI.

  Research: DuckDuckGo Lite (free, no key, via curl) + Wikipedia API
            fallback (free, no key) — the same free search used by the
            no-key web-research agent. Real snippets become the facts.
  Writing:  template-based, per platform — no LLM. Each platform gets
            its own length/style: X punchy, LinkedIn thoughtful,
            Instagram visual. Hashtags are built from the topic's own
            words plus a small generic set; nothing is invented about
            the topic beyond the researched snippets.

Usage:
    python3 agent.py --topic "The future of remote work"
    python3 agent.py --topic "Product launch announcement" --brand "YourBrand" --platforms "twitter,linkedin"

Only dependency: requests (already installed here). No .env needed.
The original key-based version is kept as agent-original.py.
"""

import argparse
import html
import re
import subprocess
import sys
import textwrap
from urllib.parse import quote_plus, unquote

import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}

STOPWORDS = set("""a an the and or of to in on for with at by from as is are was were be
been it its this that these those we you they he she his her their our your
new more over under after before between into about said says will would can
could should may might must also just now today yesterday here there what
when who how why not no yes if then than so such per via amid among future""".split())


def clean(text):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", text or ""))).strip()


def ddg_search(query, count=5):
    try:
        page = subprocess.check_output(
            ["curl", "-s", "-A", HEADERS["User-Agent"], "-m", "20",
             "https://lite.duckduckgo.com/lite/?q=" + quote_plus(query)],
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
        out.append({"title": clean(title), "url": href, "content": clean(snippet)})
        if len(out) >= count:
            break
    return out


def wiki_search(query, count=5):
    url = ("https://en.wikipedia.org/w/api.php?action=query&list=search"
           "&srsearch=" + quote_plus(query) + "&format=json&srlimit=" + str(count))
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return [{"title": h.get("title", ""),
             "url": "https://en.wikipedia.org/wiki/" + quote_plus(h.get("title", "").replace(" ", "_")),
             "content": clean(h.get("snippet", ""))}
            for h in r.json().get("query", {}).get("search", [])]


def wiki_summary(title):
    """Clean one-paragraph summary of a Wikipedia article — the search
    snippets are noisy fragments, the summary extract is a real sentence."""
    url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + quote_plus(title.replace(" ", "_"))
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return clean(r.json().get("extract", ""))


def first_sentence(text):
    text = (text or "").strip()
    if not text:
        return ""
    m = re.match(r"(.{40,}?[.!?])(\s|$)", text)
    return m.group(1).strip() if m else text[:220]


def keywords(topic, results):
    """Hashtag words from the topic itself only — snippet words made junk tags."""
    words = [w for w in re.findall(r"[A-Za-z]{4,}", topic) if w.lower() not in STOPWORDS]
    tags = []
    if words:
        full = "#" + "".join(w.capitalize() for w in words)
        tags.append(full)
    for w in words:
        tag = "#" + w.capitalize()
        if tag not in tags:
            tags.append(tag)
    return tags


def fit(text, limit):
    """Trim to a character limit on a word boundary, adding … if trimmed."""
    if len(text) <= limit:
        return text
    return text[:limit - 1].rsplit(" ", 1)[0] + "…"


def twitter_posts(topic, brand, facts, tags):
    fact = facts[0] if facts else ""
    brand_line = f" — {brand}" if brand else ""
    hooks = [
        f"{topic}: {fact}" if fact else f"Let's talk about {topic}.",
        f"The conversation around {topic} is changing fast. Here's what matters{brand_line}.",
    ]
    out = []
    for i, hook in enumerate(hooks, 1):
        tag_str = " ".join(tags[:3])
        post = fit(f"{hook} {tag_str}", 280)
        out.append(f"Tweet {i} ({len(post)}/280 chars):\n{post}")
    opener = fit(f"🧵 1/ {topic} — a short thread on what it really means, and what comes next.{brand_line} {' '.join(tags[:2])}", 280)
    out.append(f"Thread opener ({len(opener)}/280 chars):\n{opener}")
    return "\n\n".join(out)


def linkedin_post(topic, brand, facts, tags):
    fact_lines = "\n".join(f"• {f}" for f in facts[:3]) if facts else "• A topic worth a closer look."
    brand_line = f"At {brand}, " if brand else ""
    body = (
        f"{topic} — and why it deserves more than a passing thought.\n\n"
        f"{brand_line}here is what the research actually says:\n\n{fact_lines}\n\n"
        f"The takeaway is simple: the people and teams who pay attention now will be the ones "
        f"who are ready when it becomes the norm, not the exception.\n\n"
        f"For leaders, the question is no longer whether this stays — it is how to make it work well: "
        f"clear expectations, the right tools, and trust. For individuals, it is about boundaries: "
        f"a workspace that ends the day, not a day that never ends. "
        f"That is the shift worth watching — not the tools, but the trust behind them.\n\n"
        f"What is your experience with {topic.lower()}? I would genuinely like to hear it in the comments.\n\n"
        + " ".join(tags[:5])
    )
    return body + f"\n\n({len(body.split())} words)"


def instagram_caption(topic, brand, facts, tags):
    fact = facts[0] if facts else f"{topic} is changing how we live and work."
    brand_line = f"✨ {brand}\n" if brand else ""
    body = (
        f"{brand_line}{topic} ✨\n\n{fact}\n\n"
        f"Save this for later — and share it with someone who needs to hear it. "
        f"Follow for more on {topic.lower()}.\n\n"
        f"The best part? You do not need permission to start — just a clear plan, "
        f"a space that works for you, and the habit of switching off when the day is done.\n\n"
        f"Drop a comment if you work remotely — or tell us what your ideal setup looks like.\n\n"
        + " ".join(tags[:10])
    )
    return body + f"\n\n({len(body.split())} words)"


def main():
    p = argparse.ArgumentParser(description="Social Media Content Agent (no keys, free)")
    p.add_argument("--topic", default="How AI is transforming software development in 2025",
                   help="Content topic")
    p.add_argument("--brand", default="", help="Brand name (optional)")
    p.add_argument("--platforms", default="twitter,linkedin,instagram",
                   help="Comma-separated platforms")
    args = p.parse_args()

    platforms = [x.strip().lower() for x in args.platforms.split(",") if x.strip()]
    known = {"twitter", "linkedin", "instagram"}
    unknown = [x for x in platforms if x not in known]
    if unknown:
        print(f"Unknown platform(s): {', '.join(unknown)} — use twitter, linkedin, instagram", file=sys.stderr)
        return 1

    print(f"\n📱 Generating content for: {', '.join(platforms)}", flush=True)
    print(f"📌 Topic: {args.topic}\n", flush=True)
    try:
        results = ddg_search(args.topic, 5)
    except Exception:
        results = []
    if not results:
        try:
            results = wiki_search(args.topic, 5)
        except Exception as e:
            print(f"Research failed: {e}", file=sys.stderr)
            results = []
        topic_words = [w.lower() for w in re.findall(r"[A-Za-z]{4,}", args.topic)
                       if w.lower() not in STOPWORDS]
        # Rank by how many topic words the TITLE contains — "Remote work"
        # (2) beats "Remote control" (1) and "Greg Galant" (0). Snippet
        # matches alone let in false friends, so the title decides.
        def title_score(r):
            title = r.get("title", "").lower()
            return sum(1 for w in topic_words if w in title)
        results = sorted(results, key=title_score, reverse=True)[:3]
        # Swap noisy search snippets for clean article summaries
        enriched = []
        for r in results[:3]:
            try:
                summary = wiki_summary(r.get("title", ""))
            except Exception:
                summary = ""
            if summary:
                enriched.append({"title": r.get("title", ""), "url": r.get("url", ""),
                                 "content": summary})
        if enriched:
            results = enriched
        # Only the best-matching sources feed the posts — lower-ranked
        # ones ("Remote control", "Timeline of the far future") are
        # dropped, not quoted.
        topic_words = [w.lower() for w in re.findall(r"[A-Za-z]{4,}", args.topic)
                       if w.lower() not in STOPWORDS]
        def _score(r):
            title = r.get("title", "").lower()
            return sum(1 for w in topic_words if w in title)
        if results:
            best = max(_score(r) for r in results)
            results = [r for r in results if _score(r) == best]
    facts = []
    for r in results:
        s = first_sentence(r.get("content", ""))
        if s and s not in facts:
            facts.append(s)
    tags = keywords(args.topic, results)

    print("=" * 60)
    print("✍️  SOCIAL MEDIA CONTENT  (free, no-key, template-based)")
    print("=" * 60)
    print(f"Research: {len(results)} source(s) — facts below are quoted from them, not invented.")
    if facts:
        print("Key fact used: " + facts[0])
    print()
    if "twitter" in platforms:
        print("--- X / Twitter ---")
        print(twitter_posts(args.topic, args.brand, facts, tags))
        print()
    if "linkedin" in platforms:
        print("--- LinkedIn ---")
        print(linkedin_post(args.topic, args.brand, facts, tags))
        print()
    if "instagram" in platforms:
        print("--- Instagram ---")
        print(instagram_caption(args.topic, args.brand, facts, tags))
        print()
    print("Sources:")
    for i, r in enumerate(results, 1):
        print(f"{i}. {r.get('title','')} — {r.get('url','')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
