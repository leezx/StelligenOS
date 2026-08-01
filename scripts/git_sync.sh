#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
branch="${1:-}"
commit_message="${2:-}"

cd "$repo_root"

if [[ -z "$branch" ]]; then
  branch="$(git rev-parse --abbrev-ref HEAD)"
fi

if [[ -z "$commit_message" ]]; then
  commit_message="chore: sync ${branch} $(date '+%Y-%m-%d %H:%M %Z')"
fi

printf 'Repository: %s\n' "$repo_root"
printf 'Branch: %s\n' "$branch"

git fetch origin "$branch"

if git rev-parse --verify "origin/$branch" >/dev/null 2>&1; then
  local_head="$(git rev-parse "$branch")"
  remote_head="$(git rev-parse "origin/$branch")"
  if [[ "$local_head" != "$remote_head" ]]; then
    if ! git diff --quiet || ! git diff --cached --quiet; then
      git pull --rebase --autostash origin "$branch"
    else
      git pull --rebase origin "$branch"
    fi
  fi
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  git add -A
  if ! git diff --cached --quiet; then
    git commit -m "$commit_message"
  fi
else
  printf 'No local changes to commit.\n'
fi

git push origin "$branch"
git status --short --branch
