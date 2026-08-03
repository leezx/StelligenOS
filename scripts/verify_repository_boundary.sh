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
  ".git"
  ".gitignore"
)

# `.claude` is not an allowed top-level entry. It is tolerated only as the
# container of the single local tool-config file below, so that unrelated
# content cannot enter the repository under that directory.
allowed_dot_claude_paths=(
  ".claude/settings.local.json"
)

is_allowed_dot_claude_path() {
  local candidate="$1"
  local item
  for item in "${allowed_dot_claude_paths[@]}"; do
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
  # A `.claude` directory is checked path by path below. A `.claude` file is not
  # exempt and falls through to the generic check.
  if [[ "$top" == ".claude" && -d "$repo_root/.claude" ]]; then
    continue
  fi
  if ! is_allowed_top_level "$top"; then
    violations+=("$name")
  fi
done < <(find "$repo_root" -mindepth 1 -maxdepth 1 -print0)

if [[ -d "$repo_root/.claude" ]]; then
  while IFS= read -r -d '' nested; do
    nested_name="${nested#$repo_root/}"
    if ! is_allowed_dot_claude_path "$nested_name"; then
      violations+=("$nested_name")
    fi
  done < <(find "$repo_root/.claude" -mindepth 1 -print0)
fi

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
