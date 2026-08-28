#!/usr/bin/env bash
# Regression checks for scripts/scaffold_data_layout.sh
# (StelligenOS Data Layout Spec v1.0). No repository file is created or
# modified: every scaffold target is a mktemp directory outside the repo.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
script="${repo_root}/scripts/scaffold_data_layout.sh"
tmpbase="$(mktemp -d)"
trap 'rm -rf "$tmpbase"' EXIT

fail() { printf 'FAIL: %s\n' "$1" >&2; exit 1; }

# A. nonexistent repo-internal target is rejected AND nothing is created there.
internal="${repo_root}/__scaffold_probe_should_not_exist__/x"
set +e
out="$(bash "$script" "$internal" 2>&1)"; rc=$?
set -e
[[ $rc -eq 3 ]] || fail "A: expected exit 3 for repo-internal target, got $rc"
[[ -e "${repo_root}/__scaffold_probe_should_not_exist__" ]] && fail "A: script created a directory inside the repo"
grep -q "inside the repository" <<<"$out" || fail "A: missing rejection message"

# B. an external symlink that resolves into the repo is rejected.
link="${tmpbase}/evil_link"
ln -s "$repo_root" "$link"
set +e
out="$(bash "$script" "${link}/sneaky" 2>&1)"; rc=$?
set -e
[[ $rc -eq 3 ]] || fail "B: expected exit 3 for symlink-into-repo target, got $rc"
[[ -e "${repo_root}/sneaky" ]] && fail "B: script created a directory inside the repo via symlink"

# C. external run creates the tree with header rows only (no data rows).
ext="${tmpbase}/StelligenOS"
bash "$script" "$ext" INST-DEMO-ADC-TARGET-v1 >/dev/null
for d in 00_REGISTRY 10_CANDIDATES 15_CONTEXTS 20_INSTANTIATIONS 30_EVIDENCE_LIBRARY/PACKAGES 90_ARCHIVE; do
  [[ -d "${ext}/${d}" ]] || fail "C: missing directory ${d}"
done
[[ -f "${ext}/10_CANDIDATES/L04_ADC_TARGET.csv" ]] || fail "C: missing L04 candidate csv"
[[ -f "${ext}/15_CONTEXTS/context_index.csv" ]] || fail "C: missing context_index.csv"
[[ -d "${ext}/20_INSTANTIATIONS/INST-DEMO-ADC-TARGET-v1/GATESETS" ]] || fail "C: missing instantiation skeleton"
while IFS= read -r -d '' f; do
  lines="$(wc -l < "$f" | tr -d ' ')"
  [[ "$lines" -le 1 ]] || fail "C: ${f} has ${lines} lines; expected header only (<=1)"
  head -1 "$f" | grep -q ',' || fail "C: ${f} header has no comma-separated columns"
done < <(find "$ext" -type f -name '*.csv' -print0)

# D. bad instantiation id is rejected.
set +e
out="$(bash "$script" "${tmpbase}/D" not-an-inst-id 2>&1)"; rc=$?
set -e
[[ $rc -eq 2 ]] || fail "D: expected exit 2 for bad instantiation_id, got $rc"

# E. idempotent: a second run over the same target skips existing headers.
out="$(bash "$script" "$ext" INST-DEMO-ADC-TARGET-v1 2>&1)"
grep -q "skip (exists)" <<<"$out" || fail "E: second run did not skip existing files"

# F. every file the scaffold created is under the external target, never the repo.
while IFS= read -r -d '' f; do
  case "$f" in
    "$repo_root"/*) fail "F: scaffold wrote inside the repo: $f" ;;
  esac
done < <(find "$ext" -type f -print0)

printf 'scaffold_data_layout behaviour tests passed (A-F).\n'
