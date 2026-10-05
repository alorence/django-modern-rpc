# ruff: noqa: T201
"""Report GitHub Actions used in .github/workflows and compare them with their latest release.

For each `uses: owner/repo[/path]@ref` found, print the current ref, the latest release tag and the commit SHA
that tag points to (annotated tags are peeled). Only the Python standard library and `git` are required.

Usage: python3 .claude/skills/update-dependencies/scripts/check_actions.py [workflows_dir]
Set GITHUB_TOKEN to avoid the 60 requests/hour unauthenticated API limit.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

USES_RE = re.compile(r"uses:\s*(?P<action>[\w.-]+/[\w.-]+)(?P<subpath>/[\w./-]+)?@(?P<ref>[\w.-]+)(?P<comment>.*)$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def latest_release(repo: str) -> str | None:
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/releases/latest")
    req.add_header("Accept", "application/vnd.github+json")
    if token := os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:  # noqa: S310
            return json.load(resp)["tag_name"]
    except Exception as exc:  # noqa: BLE001
        print(f"  ! cannot fetch latest release of {repo}: {exc}", file=sys.stderr)
        return None


def tag_sha(repo: str, tag: str) -> str | None:
    out = subprocess.run(  # noqa: S603
        ["git", "ls-remote", "--tags", f"https://github.com/{repo}", f"refs/tags/{tag}", f"refs/tags/{tag}^{{}}"],  # noqa: S607
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    refs = {}
    for line in out.splitlines():
        sha, _, ref = line.partition("\t")
        refs[ref] = sha
    # Peeled ref (^{}) is the commit for annotated tags; fall back to the lightweight tag
    return refs.get(f"refs/tags/{tag}^{{}}") or refs.get(f"refs/tags/{tag}")


def main() -> None:
    workflows_dir = Path(sys.argv[1] if len(sys.argv) > 1 else ".github/workflows")
    usages: dict[str, set[tuple[str, str]]] = {}
    for wf in sorted(workflows_dir.glob("*.y*ml")):
        for lineno, line in enumerate(wf.read_text().splitlines(), 1):
            if m := USES_RE.search(line):
                usages.setdefault(m["action"], set()).add((m["ref"], m["comment"].strip()))
                print(f"{wf.name}:{lineno}: {m['action']}{m['subpath'] or ''}@{m['ref']} {m['comment'].strip()}")

    print("\n=== Latest releases ===")
    for repo, refs in sorted(usages.items()):
        tag = latest_release(repo)
        sha = tag_sha(repo, tag) if tag else None
        for ref, comment in sorted(refs):
            status = ("OK" if ref == sha else "OUTDATED") if SHA_RE.match(ref) else "NOT PINNED (tag ref)"
            print(f"[{status}] {repo}: current={ref} {comment}")
        print(f"    latest={tag} sha={sha}")


if __name__ == "__main__":
    main()
