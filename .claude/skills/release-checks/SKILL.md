---
name: release-checks
description: Pre-release checklist — verifies that docs/ is up to date with changes since the last tag, that README.md, pyproject.toml classifiers and docs list the supported Python / Django versions, and that the pyproject.toml version matches the top of CHANGELOG.md. If every check passes, creates a local git tag for that version (not pushed). Use when asked to "prepare a release", "check before release", "vérifier avant release", "préparer une release", "tag the release" or similar.
---

# Release checks

Goal: make sure the release is consistent, then create the git tag **locally**. Never push the tag (pushing any tag
triggers `.github/workflows/publish.yml`, which publishes to PyPI): the user does it.

This skill only checks. Don't fix problems silently: report every failure, then offer to fix the trivial ones
(dates, years, version numbers, README table). Never create the tag while a check is failing.

Conventions (from previous releases, see `git show 2.1.0 --stat`):

- Tags are **lightweight** and have **no `v` prefix**: `2.1.0`, `2.0b1`.
- The release commit is `Bump X.Y.Z` and usually touches `CHANGELOG.md`, `pyproject.toml`, `uv.lock`, and once a
  year `LICENSE.txt` and `docs/conf.py` (copyright year).
- `CHANGELOG.md`: unreleased changes live under `## Next release`. At release time, this heading becomes `## vX.Y.Z`
  followed by `**Release date: YYYY-MM-DD**`. `docs/misc/changelog.rst` just includes `CHANGELOG.md`.
- The docs version comes from package metadata (`docs/conf.py`), nothing to update there except the copyright.

## 1. Mechanical checks

```bash
python3 .claude/skills/release-checks/scripts/check_release.py
```

It reports `[OK]` / `[WARN]` / `[FAIL]` for:

- `pyproject.toml` version == first `## vX.Y.Z` section of `CHANGELOG.md` (fails while it is still `Next release`),
  release date is a valid ISO date (warns if not today), section is not empty
- `uv.lock` project version matches (`uv lock` fixes it)
- tag does not exist yet, version greater than the latest tag
- clean working tree, branch `main` (warning), up to date with `origin/main`
- supported versions, using the nox test matrix (`noxfile.py`, `is_combination_supported()`) as source of truth:
  README table (columns, rows and 🟢 cells), `pyproject.toml` classifiers, `requires-python` and `django >=`
  lower bounds, minimal versions in `docs/index.rst`
- copyright year in `LICENSE.txt` and `docs/conf.py`

If the nox matrix itself looks outdated (new Django or Python release, version reaching end of life), mention it:
compare with https://docs.djangoproject.com/en/dev/faq/install/#what-python-version-can-i-use-with-django. Also check
the Django FAQ link above the README table points to a relevant version.

## 2. Documentation review (judgement)

List what changed since the last release:

```bash
LAST=$(git describe --tags --abbrev=0)
git log --oneline $LAST..HEAD
git diff --stat $LAST..HEAD -- modernrpc/ docs/ README.md
```

Then verify, reading the relevant parts of `modernrpc/` and `docs/`:

- every user-facing change (new feature, new backend, new setting, changed behavior, removed API, new
  error code...) has an entry in the release section of `CHANGELOG.md`, and conversely
- each such change is documented in `docs/`. Typical places: new setting → `docs/config/settings.rst`, new
  serialization backend → `docs/config/backends.rst` (and the optional dependency in `pyproject.toml`), auth →
  `docs/config/authentication.rst`, errors → `docs/config/error_handling.rst`, breaking change →
  `docs/misc/migration_guide.rst`
- documented names (settings, classes, functions, `automodule`/`autoclass` targets) still exist in the code
- README examples are still valid

Build the docs and look for warnings (broken references, missing modules):

```bash
uvx nox -s docs:build 2>&1 | grep -iE 'warning|error' || echo "No warnings"
```

Report each documentation gap precisely (file, missing/outdated content). A gap is a failed check.

## 3. CI status (non-blocking)

```bash
gh run list --branch main --limit 5
```

If the last `tests` run on `HEAD` failed or is still running, tell the user and ask before tagging. If `gh` is not
installed, use the public API instead:
`curl -s "https://api.github.com/repos/alorence/django-modern-rpc/actions/runs?branch=main&per_page=5" | python3 -c "import json,sys; [print(r['name'], r['head_sha'][:7], r['status'], r['conclusion']) for r in json.load(sys.stdin)['workflow_runs']]"`
and compare the SHAs with `git rev-parse --short HEAD`.

## 4. Create the tag

Only when steps 1 and 2 have no failure (warnings accepted by the user):

```bash
VERSION=$(grep -m1 '^version = ' pyproject.toml | cut -d'"' -f2)
git tag "$VERSION"
git show --no-patch --oneline "$VERSION"
```

Do **not** run `git push`. End with a summary: checks passed, warnings, tagged commit, and the command for the user to
publish when ready:

```bash
git push origin main && git push origin <VERSION>
```

If something went wrong after tagging, the local tag can be removed with `git tag -d <VERSION>`.
