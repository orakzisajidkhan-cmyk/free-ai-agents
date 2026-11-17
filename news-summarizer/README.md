# Free News Summarizer Agent — no keys, no cost

Fetches real news on any topic and produces a structured briefing —
**Top Story, Key Themes, What to Watch, Quick Headlines** — with source
links, using **no API keys, no paid services, and no LLM**.

```bash
python3 agent.py --topic "artificial intelligence"
python3 agent.py --topic "climate change" --count 10
```

## How it works

- **Fetch:** Google News RSS (free, no key), newest first. If that fails,
  it falls back to DuckDuckGo Lite (free, no key, via curl).
- **Summarise:** extractive and deterministic — no LLM. It quotes the
  real headlines and descriptions. Key Themes are words that actually
  repeat across the headlines, with an example headline for each.
- **Only dependency:** `requests`.

## Install

```bash
pip install -r requirements.txt
python3 agent.py --topic "your topic here"
```

No `.env`, no keys, no sign-up, no spend.

## Sample output

```
📰 Fetching news about: artificial intelligence

✅ Found 5 articles

📋 NEWS BRIEFING: ARTIFICIAL INTELLIGENCE
## Top Story
- **<headline>** — <source>
  <description>
  <link>

## Key Themes
- **<word>** — appears in 2 headline(s), e.g. "<headline>"

## What to Watch
- These are the latest headlines found; follow the source links above...

## Quick Headlines
1. <headline> (<source>) — <link>
...
```

## Limits (honest)

- It reports headlines and descriptions, not full articles — the
  briefing is only as deep as the RSS feed.
- Key Themes come from repeated headline words, not from reading the
  articles; a quiet news day gives thin themes.
- Google News RSS can be slow or briefly unavailable; the DuckDuckGo
  fallback then gives search results instead of dated news.

## Origin

Derived from agent 06, News Summarizer Agent, in
[ashishpatel26/500-AI-Agents-Projects](https://github.com/ashishpatel26/500-AI-Agents-Projects)
(MIT). The original (LangChain + GPT-4o-mini + NewsAPI key, mock data
without a key) is kept untouched as `agent-original.py` — this rewrite
removes all three paid/keyed parts.

## License

MIT — see `LICENSE`.
