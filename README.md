# Free AI Agents — no keys, no cost

Three AI agents, rewritten to run **free, with no API keys, no paid
services, and no LLM**. Each one does the job of its upstream original
with free sources and local code instead.

Derived from agents in
[ashishpatel26/500-AI-Agents-Projects](https://github.com/ashishpatel26/500-AI-Agents-Projects)
(MIT). The original key-based version of each agent is kept untouched
as `agent-original.py` in its folder — use it if you later add those keys.

## The agents

| Agent | What it does | Free instead of | Run |
| --- | --- | --- | --- |
| [news-summarizer/](news-summarizer/) | Briefing on any topic: top story, key themes, what to watch, headlines with source links | LangChain + GPT-4o-mini + NewsAPI | `python3 agent.py --topic "artificial intelligence" --count 5` |
| [social-media/](social-media/) | Platform posts for X, LinkedIn and Instagram from any topic, with hashtags | CrewAI + GPT-4o-mini | `python3 agent.py --topic "The future of remote work" --brand YourBrand` |
| [code-review/](code-review/) | Static review of Python code: bugs, security issues, style — with file:line | LangChain + GPT-4o | `python3 agent.py --file my_module.py` |

## How they work — no keys, no LLM

- **news-summarizer:** Google News RSS (free, no key), DuckDuckGo Lite
  fallback. Extractive briefing — it quotes real headlines and
  descriptions, never invents stories.
- **social-media:** facts researched via DuckDuckGo Lite / Wikipedia
  summary API (free, no key), then template-based posts per platform,
  each with its own length and style. It posts nothing itself.
- **code-review:** fully local. Python AST + regex + `compile()`.
  Stdlib only — nothing to install.

## Install

```bash
pip install -r news-summarizer/requirements.txt
pip install -r social-media/requirements.txt
# code-review needs nothing — Python stdlib only
```

No `.env`, no keys, no sign-up, no spend, in any of the three.

## Tested

- **News:** 5 real articles from Google News RSS (BBC, The Economist,
  Reuters, Brookings, Motley Fool), fresh top story dated 17 Nov 2026.
- **Social:** tweet 171/280 and 126/280 chars, LinkedIn 156 words,
  Instagram 106 words, clean hashtags, 1 relevant source.
- **Code review:** 12 findings on a planted-bug fixture (4 HIGH, 2
  MEDIUM, 6 LOW), all correct — hardcoded password + API key,
  `os.system()` with user input, `eval()`, bare `except`, undefined
  name, unused import, 56-line function, missing docstrings, TODO.

## Limits (honest)

- **News:** headlines + descriptions only, not full articles; key
  themes are thin when no word repeats across headlines.
- **Social:** posts are templates, not creative copy — a human pass is
  needed before posting. DuckDuckGo can rate-limit; the Wikipedia
  fallback does the real work then.
- **Code review:** static only — it can miss real bugs and flag fine
  code; undefined-name detection is approximate; no performance checks
  or refactor suggestions. Its own pattern definitions trigger its own
  HIGH findings when it reviews itself — those are data, not live calls.

See each agent's own README for its full details, usage and limits.

## Also in this series

- [free-web-research-agent](https://github.com/orakzisajidkhan-cmyk/free-web-research-agent)
  — web research reports, no keys, no cost.
- [video-from-code](https://github.com/orakzisajidkhan-cmyk/video-from-code)
  — create videos entirely from code.

## License

MIT — see `LICENSE`. Copyright (c) 2026 Sajid Khan.
