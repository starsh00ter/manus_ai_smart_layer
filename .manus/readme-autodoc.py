#!/usr/bin/env python3
"""
Runs at the END of every successful autosync.
Parses the *actual* file tree and rewrites README.md so it never lies.
Costs ~ 200 T (local file I/O only).
"""
import json, pathlib, textwrap, datetime, os, yaml

ROOT      = pathlib.Path.cwd()
AUTOSYNC  = ROOT / ".manus/autosync.yml"
README    = ROOT / "README.md"
COST_LOG  = ROOT / ".manus/daily-tokens.log"

def main():
    # ---- load declarative rules ----
    rules = yaml.safe_load(AUTOSYNC.read_text())
    # ---- scan real tree ----
    py_files   = list(ROOT.rglob("*.py"))
    sql_files  = list(ROOT.rglob("*.sql"))
    md_files   = list(ROOT.rglob("*.md"))
    total_size = sum(f.stat().st_size for f in py_files) // 1024
    # ---- read credit spend ----
    today = datetime.date.today().isoformat()
    today_tokens = sum(int(line.split(",")[1]) for line in COST_LOG.read_text().splitlines() if line.startswith(str(today)))
    # ---- rewrite README ----
    badge = f"![credit](https://img.shields.io/badge/today-{today_tokens}-blue)"
    toc   = "\n".join(f"- `{f.relative_to(ROOT)}` – {f.stat().st_size//1024} KB" for f in sorted(py_files)[:10])
    new_readme = textwrap.dedent(f"""\
        # {ROOT.name}
        {badge}

        Auto-generated on {datetime.datetime.utcnow():%Y-%m-%d %H:%M UTC}.

        ## Credit spend today
        {today_tokens} / {rules["credit"]["daily_limit"]} tokens

        ## File manifest (top 10)
        {toc}
        ## Autosync rules
        See `.manus/autosync.yml`
        """)
    README.write_text(new_readme)
    print(f"📖 README.md updated – {len(py_files)} files, {total_size} KB, {today_tokens} T")

if __name__ == "__main__":
    main()


