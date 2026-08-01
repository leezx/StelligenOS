#!/usr/bin/env bash
set -euo pipefail

repo_root="${STELLIGENOS_REPO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
branch="${1:-}"
commit_message="${2:-}"
if [[ $# -ge 1 ]]; then shift; fi
if [[ $# -ge 1 ]]; then shift; fi
files=("$@")

cd "$repo_root"

if [[ -z "$branch" ]]; then
  branch="$(git rev-parse --abbrev-ref HEAD)"
fi

if [[ -z "$commit_message" ]]; then
  commit_message="chore: sync ${branch} $(date '+%Y-%m-%d %H:%M %Z')"
fi

if (( ${#files[@]} == 0 )); then
  printf 'Refusing to sync without an explicit file list.\n' >&2
  printf 'Usage: %s <branch> <commit-message> <file> [file ...]\n' "$0" >&2
  exit 2
fi

printf 'Working tree status before staging:\n'
git status --short

if ! git diff --cached --quiet; then
  printf 'Refusing to continue: staging area is not empty.\n' >&2
  git diff --cached --name-only >&2
  exit 3
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

git add -- "${files[@]}"

if git diff --cached --quiet; then
  printf 'No staged changes from the explicit file list.\n'
else
  git diff --cached --stat
  git commit -m "$commit_message"
fi

git push origin "$branch"
git status --short --branch
