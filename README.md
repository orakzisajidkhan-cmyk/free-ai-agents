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

### How each agent works, step by step

**news-summarizer** (`news-summarizer/agent.py`)
1. You give it a topic: `--topic "artificial intelligence"`.
2. It fetches Google News RSS for that topic — real articles, with
   title, description, source name and published date.
3. If Google News returns nothing, it falls back to DuckDuckGo Lite
   search (free, no key).
4. It builds the briefing from what it actually fetched:
   - **Top Story** — the newest, most relevant article.
   - **Key Themes** — words that actually repeat across the headlines.
   - **What to Watch** — open threads from the stories.
   - **Quick Headlines** — every headline with its source link.
5. It prints the briefing. Nothing is invented — if no word repeats,
   Key Themes says so, instead of guessing.

**social-media** (`social-media/agent.py`)
1. You give it a topic, an optional brand, and platforms:
   `--topic "The future of remote work" --brand YourBrand
   --platforms twitter,linkedin,instagram`.
2. It researches the topic first: DuckDuckGo Lite search, then the
   Wikipedia summary API, ranked by how well each source title matches
   your topic. Only the best-matching sources are kept, so junk facts
   are filtered out.
3. It turns the best fact into platform posts from templates:
   - **X / Twitter:** 2 short tweets + a thread opener, each under
     280 characters.
   - **LinkedIn:** a longer professional post, 150–200 words.
   - **Instagram:** a visual-style caption, 100–150 words.
4. Hashtags are made from your topic only (`#RemoteWork`,
   `#Remote`, `#Work`). It posts nothing itself — you copy, review
   and post.

**code-review** (`code-review/agent.py`)
1. You give it a Python file: `--file my_module.py` (or `--code`
   with inline code, or `--language python`).
2. It parses the file with Python's own `ast` module and runs
   `compile()` — so syntax errors and undefined names are caught for
   real, not guessed.
3. It runs its checks, grouped by severity:
   - **HIGH — security:** `eval()` / `exec()`, `os.system()` /
     `subprocess` with `shell=True`, hardcoded passwords, API keys
     and secrets.
   - **MEDIUM — bugs:** undefined names, unused imports, bare
     `except:` that hides errors.
   - **LOW — style:** functions over 50 lines, lines over 88
     characters, missing docstrings, TODO markers.
4. It prints every finding with file, line number, rule name and a
   one-line fix. It changes nothing in your file.

## Install

**You need:** Python 3.8 or newer, and `pip`. Nothing else. No
account, no API key, no GPU, no model download.

```bash
git clone https://github.com/orakzisajidkhan-cmyk/free-ai-agents.git
cd free-ai-agents

# news-summarizer and social-media need only the requests library
pip install -r news-summarizer/requirements.txt
pip install -r social-media/requirements.txt

# code-review needs nothing — Python standard library only
```

Then run them from their own folders:

```bash
cd news-summarizer
python3 agent.py --topic "artificial intelligence" --count 5

cd ../social-media
python3 agent.py --topic "The future of remote work" --brand YourBrand

cd ../code-review
python3 agent.py --file my_module.py
```

No `.env`, no keys, no sign-up, no spend, in any of the three.

## Which AI models does it work with?

**Short answer: none — and that is the point.** These three agents
contain no AI model at all. They do not call OpenAI, Anthropic,
Google, or any other model provider. They run on plain Python, on
any computer, with no model to download, pay for, or wait for.

| Agent | This version (free) | The original (key-based) |
| --- | --- | --- |
| news-summarizer | No model — RSS + extractive text | GPT-4o-mini (OpenAI, paid key) via LangChain |
| social-media | No model — templates + researched facts | GPT-4o-mini (OpenAI, paid key) via CrewAI |
| code-review | No model — Python AST + regex, local | GPT-4o (OpenAI, paid key) via LangChain |

**Using the output with an AI model (optional):** because the agents
print plain text, you can paste that output into any model you like
for a polish — no integration needed:

- **Claude** (Anthropic), **ChatGPT** (OpenAI), **Gemini** (Google),
  **Grok** (xAI), **DeepSeek**, or a **local model via Ollama** —
  all work the same way: paste the report / posts / review, and ask
  the model to polish it, expand it, or explain a finding.
- Example: paste a social-media post into Claude and ask *"make this
  punchier, keep it under 280 characters"*; paste a code-review
  finding and ask *"show me the fix for this"*.
- The original key-based versions are kept as `agent-original.py`
  in each folder. If you later add an OpenAI key, those run on
  **GPT-4o-mini** (news + social) and **GPT-4o** (code review) exactly
  as the upstream project wrote them — but you do not need them, and
  nothing here asks you for a key.

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
