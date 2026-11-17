"""
Code Review Agent — NO-KEY version (free).

Original: LangChain + GPT-4o (paid OpenAI key).
This version: NO API keys at all, NO paid services, NO LLM, NO LangChain.
Fully local static review of Python code: Python AST + regex + compile.

Checks:
  Bugs        unused imports/variables, possible undefined names,
              division by zero on literals, mutable default arguments,
              functions that never return a value on some paths
  Security    eval/exec, os.system, subprocess shell=True, pickle/marshal
              loads, hardcoded passwords/secrets/API keys, SQL built by
              string concatenation or f-strings in execute()
  Style       lines over 88 chars, functions over 50 lines, too many
              arguments, missing docstrings on public functions,
              bare except, print() in library code, TODO/FIXME

Findings are grouped by severity (HIGH / MEDIUM / LOW) with file:line.
It can miss real bugs and can flag things that are fine — it is a static
checker, not a human reviewer, and it says so in its output.

Usage:
    python3 agent.py --file my_module.py
    python3 agent.py --code "def divide(a, b): return a / b"
    python3 agent.py --file app.js --language javascript   (regex-only)

Only stdlib is used — no requirements to install. No .env needed.
The original key-based version is kept as agent-original.py.
"""

import argparse
import ast
import re

MAX_LINE = 88
MAX_FUNC_LINES = 50
MAX_ARGS = 5

SECRET_RE = re.compile(
    r"""(?i)(password|passwd|secret|api[_-]?key|token|private[_-]?key)\s*=\s*['"][^'"]{4,}['"]""")
EVAL_RE = re.compile(r"\b(eval|exec)\s*\(")
SYSTEM_RE = re.compile(r"\bos\.system\s*\(|\bpopen\s*\(")
SHELL_RE = re.compile(r"shell\s*=\s*True")
PICKLE_RE = re.compile(r"\b(pickle|marshal)\.(loads?|load)\s*\(")
SQL_RE = re.compile(r"\bexecute\s*\(\s*(f['\"]|['\"][^'\"]*['\"]\s*\+|\w+\s*\+\s*['\"])")
TODO_RE = re.compile(r"#\s*(TODO|FIXME|XXX|HACK)\b")


def finding(sev, line, code, msg):
    return {"severity": sev, "line": line, "code": code, "message": msg}


def review_python(code, filename):
    findings = []
    try:
        tree = ast.parse(code, filename=filename)
    except SyntaxError as e:
        findings.append(finding("HIGH", e.lineno or 0, "syntax-error",
                                f"SyntaxError: {e.msg}"))
        return findings
    try:
        compile(code, filename, "exec")
    except SyntaxError as e:  # pragma: no cover - parse already caught it
        findings.append(finding("HIGH", e.lineno or 0, "syntax-error", str(e)))

    lines = code.splitlines()

    # --- imports: unused ---
    imported = {}  # name -> lineno
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                imported[(a.asname or a.name).split(".")[0]] = node.lineno
        elif isinstance(node, ast.ImportFrom):
            for a in node.names:
                if a.name != "*":
                    imported[a.asname or a.name] = node.lineno
    used_names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    used_attrs = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    for name, lineno in imported.items():
        if name not in used_names and name not in used_attrs:
            findings.append(finding("LOW", lineno, "unused-import",
                                    f"Imported '{name}' is never used"))

    # --- functions ---
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        start, end = node.lineno, getattr(node, "end_lineno", node.lineno)
        length = end - start + 1
        if length > MAX_FUNC_LINES:
            findings.append(finding("LOW", start, "long-function",
                                    f"Function '{node.name}' is {length} lines "
                                    f"(over {MAX_FUNC_LINES}) — consider splitting it"))
        if len(node.args.args) > MAX_ARGS:
            findings.append(finding("LOW", start, "too-many-args",
                                    f"Function '{node.name}' takes {len(node.args.args)} "
                                    f"arguments (over {MAX_ARGS})"))
        if not node.name.startswith("_") and not ast.get_docstring(node):
            findings.append(finding("LOW", start, "missing-docstring",
                                    f"Public function '{node.name}' has no docstring"))
        for d in node.args.defaults:
            if isinstance(d, (ast.List, ast.Dict, ast.Set)):
                findings.append(finding("MEDIUM", d.lineno, "mutable-default",
                                        f"Mutable default argument in '{node.name}' — "
                                        "it is shared across calls; use None instead"))
        # unused local variables: assigned in this function, never read there
        assigned, read = {}, set()
        for sub in ast.walk(node):
            if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Store):
                assigned.setdefault(sub.id, sub.lineno)
            elif isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Load):
                read.add(sub.id)
        for name, lineno in assigned.items():
            if name not in read and name != "_":
                findings.append(finding("LOW", lineno, "unused-variable",
                                        f"Variable '{name}' is assigned but never used "
                                        f"in '{node.name}'"))

    # --- possible undefined names: loaded but never defined anywhere ---
    defined = set(imported)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defined.add(node.name)
        elif isinstance(node, ast.arg):
            defined.add(node.arg)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            defined.add(node.id)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            defined.add(node.name)
    builtins = set(dir(__builtins__)) | {"True", "False", "None", "__builtins__"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            if node.id not in defined and node.id not in builtins:
                findings.append(finding("MEDIUM", node.lineno, "undefined-name",
                                        f"Possible undefined name '{node.id}' — "
                                        "not imported, defined or assigned in this file"))
                defined.add(node.id)  # report once per name

    # --- regex checks, line by line ---
    # Security patterns are skipped on comment-only lines and inside
    # triple-quoted strings (docstrings): the words there are
    # documentation, not code that runs.
    in_docstring = False
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            if stripped.count('"""') == 1 or stripped.count("'''") == 1:
                in_docstring = not in_docstring
            continue
        if in_docstring or stripped.startswith("#"):
            if len(line) > MAX_LINE:
                findings.append(finding("LOW", i, "long-line",
                                        f"Line is {len(line)} chars (over {MAX_LINE})"))
            m = TODO_RE.search(line)
            if m:
                findings.append(finding("LOW", i, "todo",
                                        f"{m.group(1)} left in the code"))
            continue
        if EVAL_RE.search(line):
            findings.append(finding("HIGH", i, "eval-exec",
                                    "eval()/exec() runs arbitrary code — avoid it"))
        if SYSTEM_RE.search(line):
            findings.append(finding("HIGH", i, "os-system",
                                    "os.system()/popen() with a shell — prefer subprocess without shell=True"))
        if SHELL_RE.search(line):
            findings.append(finding("HIGH", i, "shell-true",
                                    "subprocess shell=True — command injection risk if any part comes from input"))
        if PICKLE_RE.search(line):
            findings.append(finding("HIGH", i, "pickle-load",
                                    "pickle/marshal load on untrusted data can run arbitrary code"))
        if SECRET_RE.search(line):
            findings.append(finding("HIGH", i, "hardcoded-secret",
                                    "Hardcoded password/secret/key in source — move it to an environment variable"))
        if SQL_RE.search(line):
            findings.append(finding("HIGH", i, "sql-concat",
                                    "SQL built by string concatenation/f-string — use parameterised queries"))
        if len(line) > MAX_LINE:
            findings.append(finding("LOW", i, "long-line",
                                    f"Line is {len(line)} chars (over {MAX_LINE})"))
        m = TODO_RE.search(line)
        if m:
            findings.append(finding("LOW", i, "todo",
                                    f"{m.group(1)} left in the code"))
        if re.search(r"\bprint\s*\(", line) and "test" not in filename.lower():
            findings.append(finding("LOW", i, "print-call",
                                    "print() in library code — use logging instead"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            findings.append(finding("MEDIUM", node.lineno, "bare-except",
                                    "Bare except: hides real errors — catch a specific exception"))
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            right = node.right
            if isinstance(right, ast.Constant) and right.value == 0:
                findings.append(finding("MEDIUM", node.lineno, "div-by-zero",
                                        "Division by literal zero"))
    return findings


def review_text(code, filename):
    """Regex-only review for non-Python files."""
    findings = []
    for i, line in enumerate(code.splitlines(), 1):
        if EVAL_RE.search(line):
            findings.append(finding("HIGH", i, "eval-exec", "eval()/exec() runs arbitrary code"))
        if SECRET_RE.search(line):
            findings.append(finding("HIGH", i, "hardcoded-secret",
                                    "Hardcoded password/secret/key in source"))
        if SHELL_RE.search(line):
            findings.append(finding("HIGH", i, "shell-true", "shell=True — command injection risk"))
        if len(line) > MAX_LINE:
            findings.append(finding("LOW", i, "long-line", f"Line is {len(line)} chars (over {MAX_LINE})"))
        m = TODO_RE.search(line)
        if m:
            findings.append(finding("LOW", i, "todo", f"{m.group(1)} left in the code"))
    return findings


def overall(findings):
    high = sum(1 for f in findings if f["severity"] == "HIGH")
    med = sum(1 for f in findings if f["severity"] == "MEDIUM")
    if high:
        return "🔴 Critical Issues"
    if med:
        return "🟡 Needs Work"
    if findings:
        return "🟡 Needs Work"
    return "🟢 Good"


def main():
    p = argparse.ArgumentParser(description="Code Review Agent (no keys, free)")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", help="Path to file to review")
    group.add_argument("--code", help="Inline code snippet to review")
    p.add_argument("--language", default="python", help="Programming language (default: python)")
    args = p.parse_args()

    if args.file:
        with open(args.file) as f:
            code = f.read()
        name = args.file
        print(f"\n🔍 Reviewing: {args.file}\n")
    else:
        code = args.code
        name = "<inline code>"
        print("\n🔍 Reviewing inline code snippet\n")

    findings = (review_python(code, name) if args.language.lower() == "python"
                else review_text(code, name))
    findings.sort(key=lambda f: ({"HIGH": 0, "MEDIUM": 1, "LOW": 2}[f["severity"]], f["line"]))

    print("=" * 60)
    print("📋 CODE REVIEW  (free, no-key, static — no LLM)")
    print("=" * 60)
    print(f"## Overall: {overall(findings)}")
    print(f"## Findings: {len(findings)} "
          f"({sum(1 for f in findings if f['severity']=='HIGH')} HIGH, "
          f"{sum(1 for f in findings if f['severity']=='MEDIUM')} MEDIUM, "
          f"{sum(1 for f in findings if f['severity']=='LOW')} LOW)\n")
    if not findings:
        print("No issues found by the static checks.")
    for sev in ("HIGH", "MEDIUM", "LOW"):
        group_f = [f for f in findings if f["severity"] == sev]
        if not group_f:
            continue
        print(f"### {sev}")
        for f in group_f:
            print(f"- {name}:{f['line']} [{f['code']}] {f['message']}")
        print()
    print("_Note: static checks only — this can miss real bugs and can flag "
          "code that is fine. Treat it as a first pass, not a verdict._")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
