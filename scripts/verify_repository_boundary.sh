#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

allowed_top_level=(
  "AGENTS.md"
  "ChatGPT-Codex-talk.md"
  "LICENSE"
  "LINKS.md"
  "README.md"
  "architecture.md"
  "docs"
  "schemas"
  "src"
  "genmodules"
  "extensions"
  "code"
  "tests"
  "notebooks"
  "examples"
  "demo"
  "reference_asset"
  "tutorial"
  "templates"
  "fixtures"
  "logs"
  "manifests"
  "prompts"
  "scripts"
  "requirements.txt"
  ".git"
  ".gitignore"
)

# Neither `.claude` nor `.github` is an allowed top-level entry. Each is
# tolerated only as the container of the exact paths enumerated below, so that
# unrelated content cannot enter the repository under a dot-directory. Allowing
# such a directory wholesale was rejected during the review of PR #43.
restricted_dirs=(
  ".claude"
  ".github"
)

allowed_restricted_paths=(
  ".claude/settings.local.json"
  ".github/workflows"
  ".github/workflows/ci.yml"
)

is_restricted_dir() {
  local candidate="$1"
  local item
  for item in "${restricted_dirs[@]}"; do
    if [[ "$item" == "$candidate" ]]; then
      return 0
    fi
  done
  return 1
}

is_allowed_restricted_path() {
  local candidate="$1"
  local item
  for item in "${allowed_restricted_paths[@]}"; do
    if [[ "$item" == "$candidate" ]]; then
      return 0
    fi
  done
  return 1
}

is_allowed_top_level() {
  local candidate="$1"
  local item
  for item in "${allowed_top_level[@]}"; do
    if [[ "$item" == "$candidate" ]]; then
      return 0
    fi
  done
  return 1
}

violations=()
while IFS= read -r -d '' entry; do
  name="${entry#$repo_root/}"
  top="${name%%/*}"
  # A restricted directory is checked path by path below. A file of the same
  # name is not exempt and falls through to the generic check.
  if is_restricted_dir "$top" && [[ -d "$repo_root/$top" ]]; then
    continue
  fi
  if ! is_allowed_top_level "$top"; then
    violations+=("$name")
  fi
done < <(find "$repo_root" -mindepth 1 -maxdepth 1 -print0)

for restricted in "${restricted_dirs[@]}"; do
  if [[ -d "$repo_root/$restricted" ]]; then
    while IFS= read -r -d '' nested; do
      nested_name="${nested#$repo_root/}"
      if ! is_allowed_restricted_path "$nested_name"; then
        violations+=("$nested_name")
      fi
    done < <(find "$repo_root/$restricted" -mindepth 1 -print0)
  fi
done

if (( ${#violations[@]} > 0 )); then
  printf 'Repository boundary violation(s):\n' >&2
  printf ' - %s\n' "${violations[@]}" >&2
  exit 1
fi

disallowed_files=(
  '*.csv' '*.tsv' '*.parquet' '*.feather' '*.rds' '*.h5ad' '*.h5'
  '*.loom' '*.sqlite' '*.db' '*.xlsx' '*.jsonl' '*.bam' '*.fastq'
  '*.fq' '*.vcf' '*.tar' '*.gz' '*.zip' '*.7z'
)

for pattern in "${disallowed_files[@]}"; do
  if find "$repo_root" -type f -name "$pattern" | grep -q .; then
    printf 'Repository boundary violation: data-like file matching %s\n' "$pattern" >&2
    find "$repo_root" -type f -name "$pattern" >&2
    exit 1
  fi
done

printf 'Repository boundary check passed.\n'
