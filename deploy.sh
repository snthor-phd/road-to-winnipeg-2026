#!/usr/bin/env bash
# Deploy the private Road to Winnipeg site to GitHub Pages.
# Safe to re-run: creates the repo on first run, then just pushes updates.
set -euo pipefail

OWNER="snthor-phd"
REPO="road-to-winnipeg-2026"
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "→ Road to Winnipeg deploy  ($OWNER/$REPO)"

command -v git >/dev/null || { echo "✗ git not found."; exit 1; }
command -v python3 >/dev/null || { echo "✗ python3 not found."; exit 1; }
if ! command -v gh >/dev/null; then
  echo "✗ GitHub CLI (gh) not found.  brew install gh"; exit 1
fi
if ! gh auth status >/dev/null 2>&1; then
  echo "✗ gh is not signed in. Run:  gh auth login"; exit 1
fi

# --- rebuild from data/stops.json -----------------------------------------
echo "• Rebuilding pages from data/stops.json"
python3 build.py

# --- commit ----------------------------------------------------------------
git init -q
git add -A
if git diff --cached --quiet 2>/dev/null; then
  echo "• Nothing new to commit."
else
  git commit -q -m "Update road-to-winnipeg ($(date +%Y-%m-%d))"
  echo "• Committed changes."
fi
git branch -M main

# --- repo + push -----------------------------------------------------------
if gh repo view "$OWNER/$REPO" >/dev/null 2>&1; then
  git remote get-url origin >/dev/null 2>&1 || git remote add origin "git@github.com:$OWNER/$REPO.git"
  git push -u origin main
else
  gh repo create "$OWNER/$REPO" --public --source=. --remote=origin --push \
    --description "Private companion — the road up to the 2026 NL&PB rendezvous in Winnipeg"
fi

# --- enable Pages ----------------------------------------------------------
gh api --method POST "repos/$OWNER/$REPO/pages" \
  -f "source[branch]=main" -f "source[path]=/" >/dev/null 2>&1 \
  && echo "• GitHub Pages enabled." \
  || echo "• GitHub Pages already enabled (or enable it in Settings → Pages)."

echo ""
echo "✓ Done. Live in ~30–60s at:"
echo "    https://$OWNER.github.io/$REPO/"
echo ""
echo "  Unlisted: noindex on every page, robots.txt disallows all, nothing links here."
