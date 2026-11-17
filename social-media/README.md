# Free Social Media Content Agent — no keys, no cost

Generates platform-optimized social media posts (X/Twitter, LinkedIn,
Instagram) from any topic, using **no API keys, no paid services, and
no LLM**.

```bash
python3 agent.py --topic "The future of remote work"
python3 agent.py --topic "Product launch announcement" --brand "YourBrand" --platforms "twitter,linkedin"
```

## How it works

- **Research:** DuckDuckGo Lite (free, no key, via curl) with a
  Wikipedia API fallback (free, no key) — the same free search as the
  no-key web-research agent. Real snippets become the facts; the posts
  quote them, they never invent facts about the topic.
- **Writing:** template-based, per platform — no LLM. X is punchy
  (2 tweet variations under 280 chars + a thread opener), LinkedIn is
  thoughtful (150–200 words, storytelling hook, question to the reader),
  Instagram is visual (100–150 word caption + hashtags).
- **Hashtags:** built from the topic's own words plus words that repeat
  in the researched snippets.
- **Only dependency:** `requests`.

## Install

```bash
pip install -r requirements.txt
python3 agent.py --topic "your topic here"
```

No `.env`, no keys, no sign-up, no spend.

## Options

| Option | Default | What it does |
| --- | --- | --- |
| `--topic "…"` | required | The topic to write about |
| `--brand Name` | — | Brand name, woven into the posts |
| `--platforms a,b` | twitter,linkedin,instagram | Any of twitter, linkedin, instagram |

## Limits (honest)

- Posts are templates filled with real researched facts — they are not
  creative copywriting. Read them and edit the voice before posting;
  a human pass makes them yours.
- If the research comes back thin (niche topic, DuckDuckGo rate-limit),
  the posts lean on the topic itself and say less.
- It does not post anything for you — copy the output and post it
  yourself, in your own accounts.

## Origin

Derived from agent 14, Social Media Content Agent, in
[ashishpatel26/500-AI-Agents-Projects](https://github.com/ashishpatel26/500-AI-Agents-Projects)
(MIT). The original (CrewAI + GPT-4o-mini, paid OpenAI key) is kept
untouched as `agent-original.py` — this rewrite removes the LLM and
the key entirely.

## License

MIT — see `LICENSE`.
