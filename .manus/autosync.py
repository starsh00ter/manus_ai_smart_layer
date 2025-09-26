#!/usr/bin/env python3
"""
Autosync driver – credit-aware, bidirectional, self-documenting.
One invocation == one git commit (or dry-run).
Exit codes:
 0  success
 77 credit limit exceeded (git hook convention)
 99 unrecoverable conflict (needs human)
"""
import argparse, json, pathlib, subprocess, sys, os, yaml, datetime, hashlib
from typing import Dict, List

CFG   = yaml.safe_load(open(".manus/autosync.yml"))
TODAY = datetime.date.today().isoformat()
COST  = 0  # running token count

# ---------- util ----------
def tok(txt: str) -> int:
    global COST
    t = len(txt.split()) * 1.3
    COST += t
    return int(t)

def sh(cmd: List[str], cwd: pathlib.Path = None) -> str:
    return subprocess.check_output(cmd, cwd=cwd, text=True)

def credit_gate() -> bool:
    """Return True if this invocation is allowed to spend tokens."""
    daily_log = pathlib.Path(".manus/daily-tokens.log")
    if not daily_log.exists():
        return True
    spent = sum(int(line.split(",")[1]) for line in daily_log.read_text().splitlines() if line.startswith(TODAY))
    return spent + COST < CFG["credit"]["daily_limit"]

def repo_path(name: str) -> pathlib.Path:
    # Assuming all repos are cloned under /home/ubuntu/
    # This needs to be adjusted based on the actual cloning location
    # For now, using the path from autosync.yml
    for repo_cfg in CFG["repos"]:
        if repo_cfg["name"] == name:
            return pathlib.Path(repo_cfg["path"]).expanduser()
    raise ValueError(f"Repository {name} not found in autosync.yml")

# ---------- sync logic ----------
def smart_copy(master: pathlib.Path, shadow: pathlib.Path, pattern: str) -> bool:
    """Copy files matching pattern from master to shadow, return True if changed."""
    changed = False
    for src in master.rglob(pattern):
        if not src.is_file():
            continue
        rel = src.relative_to(master)
        dst = shadow / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists() or dst.read_bytes() != src.read_bytes():
            dst.write_bytes(src.read_bytes())
            changed = True
    return changed

def bidirectional_sync(rule: Dict) -> bool:
    """Two-way merge for docs, prompts, etc. Conflicts → shadow wins."""
    pat = rule["pattern"]
    # Get repo paths dynamically based on names in autosync.yml
    repo_names = [repo["name"] for repo in CFG["repos"]]
    if len(repo_names) < 2:
        raise ValueError("Not enough repositories defined for bidirectional sync.")
    
    repo_a_path = repo_path(repo_names[0])
    repo_b_path = repo_path(repo_names[1])

    changed = False
    # A → B
    if smart_copy(repo_a_path, repo_b_path, pat):
        changed = True
    # B → A
    if smart_copy(repo_b_path, repo_a_path, pat):
        changed = True
    return changed

def shadow_sync(rule: Dict) -> bool:
    """One-way: master → shadow only."""
    master_name = rule["master"]
    shadow_name = rule["shadow"]
    master = repo_path(master_name)
    shadow = repo_path(shadow_name)
    return smart_copy(master, shadow, rule["pattern"])

# ---------- git ----------
def git_commit(repo: pathlib.Path, msg: str) -> None:
    sh(["git", "add", "."], cwd=repo)
    if sh(["git", "status", "--porcelain"], cwd=repo).strip():
        sh(["git", "commit", "-m", msg], cwd=repo)

# ---------- main ----------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--source", default="manual")
    args = parser.parse_args()

    if not credit_gate():
        print("❌ autosync: credit limit exceeded")
        sys.exit(77)

    any_change = False
    for rule in CFG["sync"]:
        if rule.get("bidirectional"):
            changed = bidirectional_sync(rule)
        else:
            changed = shadow_sync(rule)
        if changed:
            any_change = True
            print(f"🔄 {rule["pattern"]} changed")

    for name in [repo["name"] for repo in CFG["repos"]]:
        repo = repo_path(name)
        if not any_change and args.dry_run:
            continue
        # always refresh doc
        subprocess.run([sys.executable, str(repo / ".manus/readme-autodoc.py")], cwd=repo)
        if not args.dry_run:
            git_commit(repo, f"autosync: {args.source} [cost {COST}T]")

    pathlib.Path(".manus/sync-cost.txt").write_text(str(COST))
    print(f"✅ autosync complete – {COST} T")

if __name__ == "__main__":
    main()


