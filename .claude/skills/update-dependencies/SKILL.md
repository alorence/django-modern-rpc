---
name: update-dependencies
description: Routine update of all project dependencies — uv itself, uv.lock (all groups), tool versions pinned in GitHub workflows and .pre-commit-config.yaml (uv, ruff, mypy...), and SHA-pinned GitHub Actions. Use when asked to "bump dependencies", "update deps", "mettre à jour les dépendances" or similar.
---

# Update dependencies

Routine maintenance task. Past examples: commits `7907fcb`, `944ca20`, `f32cd43` (`git show <sha> -- .github .pre-commit-config.yaml`).
Files usually touched: `uv.lock`, `.github/workflows/*.yml`, `.pre-commit-config.yaml`.

Start from a clean working tree (`git status`). If it is not clean, ask the user before going further.

## 1. Update uv locally

```bash
uv self update
uv --version   # remember this version: it is the target for UV_VERSION and the uv-pre-commit rev
```

If `uv self update` fails (uv installed by a system package manager), report it and use the version reported by
`uv --version`, after checking the latest release on https://github.com/astral-sh/uv/releases.

## 2. Update project dependencies

```bash
git diff --quiet uv.lock  # sanity check: lockfile untouched before update
uv sync --upgrade --all-groups
```

Then list what changed, to know which tools must be propagated elsewhere:

```bash
git diff uv.lock | grep -E '^[-+](name|version) = ' | paste - - | head -100
```

A more readable alternative: `uv tree --outdated` before the update, or compare `uv pip list` before/after.

## 3. Propagate tool versions to CI and pre-commit

Find every hard-coded tool version outside `uv.lock`:

```bash
grep -nE '_VERSION:|rev:' .github/workflows/*.yml .pre-commit-config.yaml
```

Known locations (check again with the grep above, new ones may appear):

| Tool | Location | Target version |
|---|---|---|
| uv | `env.UV_VERSION` in `tests.yml`, `benchmarks.yml`, `publish.yml` | `uv --version` (step 1) |
| uv | `astral-sh/uv-pre-commit` `rev:` in `.pre-commit-config.yaml` | same, without `v` prefix (`0.12.15`) |
| ruff | `astral-sh/ruff-pre-commit` `rev:` | ruff version in `uv.lock`, with `v` prefix (`v0.16.8`) |
| mypy | `pre-commit/mirrors-mypy` `rev:` | mypy version in `uv.lock`, with `v` prefix |
| ty, others | any `*_VERSION` variable or `rev:` added later | version in `uv.lock` |

Get a locked version with: `grep -A1 '^name = "ruff"$' uv.lock`.

Rules:

- Pre-commit hooks for tools that are also project dependencies must match the version in `uv.lock` exactly
  (don't use `pre-commit autoupdate` for them, it may pick a version newer than the lock).
- For hooks that are not project dependencies (e.g. `pre-commit/pre-commit-hooks`), check the latest release
  with `git ls-remote --tags --sort=-v:refname https://github.com/<owner>/<repo> | head` and update if needed.
- If a pre-commit mirror has not yet published a tag for the locked version, keep the previous rev and tell the user.

## 4. Check GitHub Actions versions and SHA pins

Run the helper script (stdlib only, uses GitHub API + `git ls-remote`):

```bash
python3 .claude/skills/update-dependencies/scripts/check_actions.py
```

It lists every `uses:` and, per action, the latest release tag and the commit SHA it points to:

- `[OK]`: pinned SHA is the latest release, nothing to do.
- `[OUTDATED]`: replace the SHA **and** the version in the trailing comment, everywhere the action is used
  (e.g. `sed -i 's/<old_sha>/<new_sha>/g; s/# v10.1.0,/# v10.2.0,/g' .github/workflows/*.yml`).
  Keep the existing comment format of each line (`# vX.Y.Z - <releases url>` or `# vX.Y.Z, see <releases url>`).
- `[NOT PINNED (tag ref)]` (e.g. `actions/checkout@v6`, `github/codeql-action/*@v4`): report to the user when a new
  major version exists (e.g. `v6` → `v7`), and ask whether to bump the major tag or to pin to a SHA. Don't change
  these silently.

Caveats:

- "Latest release" is not always meaningful: `github/codeql-action` publishes `codeql-bundle-*` releases, so compare
  with tags (`git ls-remote --tags https://github.com/github/codeql-action 'v4*'`) instead.
- For a major version bump of a pinned action, look at the release notes for breaking changes (inputs renamed,
  Node runtime change...) and mention them to the user.
- If the API rate limit is hit, export `GITHUB_TOKEN` or fall back to `git ls-remote` per repository.

Re-run the script after editing: every pinned action must be `[OK]`.

## 5. Verify

```bash
uv lock --check
uv run ruff check .
uv run ruff format . --check
uv run --group=type-checking mypy
uv run --group=type-checking ty check .
uv run pytest -n auto
```

A new ruff/mypy/ty version may introduce new lint or typing errors. Fix trivial ones (or auto-fix with
`uv run ruff check . --fix`); for anything non-trivial, report to the user instead of silencing rules.

## 6. Summarize

Report to the user:

- uv version before → after
- notable package updates (major/minor bumps, especially Django, ruff, mypy, ty, serialization backends)
- updated actions (old → new version)
- unpinned actions with a new major available, and any skipped item with the reason
- verification results (tests, lint, type checking)

Don't commit unless asked. Past commit messages: `Bump all dependencies` / `Bump dependencies`.
