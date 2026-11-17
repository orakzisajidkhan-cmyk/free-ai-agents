# Free Code Review Agent — no keys, no cost

Reviews Python code for bugs, security issues and style violations —
**no API keys, no paid services, and no LLM**. Fully local: Python AST
+ regex + `compile()`.

```bash
python3 agent.py --file my_module.py
python3 agent.py --code "def divide(a, b): return a / b"
python3 agent.py --file app.js --language javascript
```

## How it works

| Area | Checks |
| --- | --- |
| Bugs | Unused imports/variables, possible undefined names, division by literal zero, mutable default arguments, bare `except` |
| Security | `eval`/`exec`, `os.system`, `subprocess shell=True`, `pickle`/`marshal` loads, hardcoded passwords/secrets/API keys, SQL built by string concatenation or f-strings |
| Style | Lines over 88 chars, functions over 50 lines, over 5 arguments, missing docstrings on public functions, `print()` in library code, TODO/FIXME |

Findings are grouped by severity (HIGH / MEDIUM / LOW) with
`file:line`, and the overall rating is 🟢 Good / 🟡 Needs Work /
🔴 Critical Issues. Non-Python files get a regex-only pass.

## Install

No dependencies at all — Python 3 stdlib only.

```bash
python3 agent.py --file your_code.py
```

No `.env`, no keys, no sign-up, no spend.

## Sample output

```
🔍 Reviewing: example.py

📋 CODE REVIEW  (free, no-key, static — no LLM)
## Overall: 🔴 Critical Issues
## Findings: 3 (1 HIGH, 1 MEDIUM, 1 LOW)

### HIGH
- example.py:4 [hardcoded-secret] Hardcoded password/secret/key in source — move it to an environment variable

### MEDIUM
- example.py:2 [undefined-name] Possible undefined name 'x' — not imported, defined or assigned in this file

### LOW
- example.py:1 [unused-import] Imported 'os' is never used
```

## Limits (honest)

- It is a static checker, not a human reviewer. It can miss real bugs
  (it does not run the code or understand intent) and it can flag code
  that is fine — e.g. a name defined dynamically, or a `print()` that
  is deliberate. Treat it as a first pass, not a verdict.
- Undefined-name detection is approximate: names from `*` imports,
  dynamic assignment and decorators are not tracked.
- It does not check performance, and it does not suggest refactors —
  that is what the LLM version did, and it is the part a static
  checker cannot honestly do.

## Origin

Derived from agent 02, Code Review Agent, in
[ashishpatel26/500-AI-Agents-Projects](https://github.com/ashishpatel26/500-AI-Agents-Projects)
(MIT). The original (LangChain + GPT-4o, paid OpenAI key) is kept
untouched as `agent-original.py` — this rewrite removes the LLM and
the key entirely.

## License

MIT — see `LICENSE`.
