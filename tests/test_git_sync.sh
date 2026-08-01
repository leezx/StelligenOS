#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
sync_script="$script_dir/scripts/git_sync.sh"
tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT

remote="$tmp_root/remote.git"
repo="$tmp_root/repo"
git init --bare -q "$remote"
git init -q -b main "$repo"
git -C "$repo" config user.email test@example.com
git -C "$repo" config user.name "Git Sync Test"
printf 'initial\n' > "$repo/README.md"
git -C "$repo" add -- README.md
git -C "$repo" commit -qm 'test: initial commit'
git -C "$repo" remote add origin "$remote"
git -C "$repo" push -qu origin main

run_sync() {
  STELLIGENOS_REPO_ROOT="$repo" "$sync_script" main "$1" "${@:2}"
}

# A: an explicitly listed untracked file must be committed and pushed.
mkdir -p "$repo/schemas"
printf '{"type":"object"}\n' > "$repo/schemas/opportunity.schema.json"
run_sync 'test: add untracked schema' schemas/opportunity.schema.json >/dev/null
git -C "$repo" ls-files --error-unmatch schemas/opportunity.schema.json >/dev/null

# B: an explicitly listed tracked modification must be committed and pushed.
printf 'updated\n' >> "$repo/README.md"
run_sync 'test: update tracked file' README.md >/dev/null
git -C "$repo" log -2 --format='%s' | rg -q '^test: update tracked file$'

# C: a pre-existing unrelated staged file must cause a safe refusal.
printf 'unrelated\n' >> "$repo/README.md"
git -C "$repo" add -- README.md
if run_sync 'test: should refuse dirty index' schemas/opportunity.schema.json >/tmp/git-sync-test-c.out 2>&1; then
  printf 'Expected non-empty staging area to be rejected.\n' >&2
  exit 1
fi
rg -q 'staging area is not empty' /tmp/git-sync-test-c.out
git -C "$repo" reset -q HEAD -- README.md

# D: an omitted file list must be rejected before any network operation.
if STELLIGENOS_REPO_ROOT="$repo" "$sync_script" main 'test: missing files' >/tmp/git-sync-test-d.out 2>&1; then
  printf 'Expected missing file list to be rejected.\n' >&2
  exit 1
fi
rg -q 'explicit file list' /tmp/git-sync-test-d.out

printf 'git_sync behavior tests passed (A-D).\n'
