#!/usr/bin/env bash
# scaffold_data_layout.sh -- create the empty external StelligenOS runtime data
# tree defined by docs/protocols/STELLIGENOS_DATA_LAYOUT_SPEC.v1.0.md
#
# Usage:
#   scripts/scaffold_data_layout.sh <target_root> [instantiation_id]
#
#   <target_root>       absolute path OUTSIDE this repository, e.g.
#                       /Volumes/Stelligen_SSD/Stelligen/DATA/StelligenOS
#   [instantiation_id]  optional; if given, also creates an Instantiation
#                       skeleton (default: none). Must match INST-<UPPER-KEBAB>-v<N>.
#
# The script creates directories and CSV header rows only (headers come from
# src/contracts/data_layout/csv_headers.yaml -- this repo stores no .csv files).
# It never writes data rows. The repo-boundary check runs on the RESOLVED
# (symlink-followed) path BEFORE anything is created: a repo-internal target is
# rejected without touching the filesystem. Requires python3 + PyYAML (the
# repo's only runtime dependency).

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
headers_yaml="${repo_root}/src/contracts/data_layout/csv_headers.yaml"

target_root="${1:-}"
instantiation_id="${2:-}"

if [[ -z "$target_root" ]]; then
  printf 'Usage: %s <target_root> [instantiation_id]\n' "$0" >&2
  exit 2
fi
case "$target_root" in
  /*) : ;;
  *) printf 'Refusing: <target_root> must be an absolute path.\n' >&2; exit 2 ;;
esac
if [[ ! -f "$headers_yaml" ]]; then
  printf 'missing %s\n' "$headers_yaml" >&2; exit 4
fi

# Resolve the target (following symlinks) WITHOUT creating anything, walking up
# to the nearest existing ancestor, then check containment against the resolved
# repo root. Only after this passes do we create directories.
abs_target="$(python3 - "$target_root" <<'PY'
import os, sys
p = os.path.abspath(sys.argv[1])
tail = []
while not os.path.exists(p):
    p, t = os.path.split(p)
    tail.append(t)
    if not t:
        break
resolved = os.path.realpath(p)
for t in reversed(tail):
    resolved = os.path.join(resolved, t)
print(resolved)
PY
)"

case "$abs_target/" in
  "$repo_root"/* | "$repo_root")
    printf 'Refusing: resolved target %s is inside the repository %s.\n' "$abs_target" "$repo_root" >&2
    printf 'Runtime data must live outside the implementation repository. Nothing was created.\n' >&2
    exit 3
    ;;
esac

# hdr <logical-header-name> <dest .csv path>
hdr() {
  local name="$1" dst="$2"
  if [[ -e "$dst" ]]; then printf 'skip (exists): %s\n' "$dst"; return 0; fi
  python3 - "$headers_yaml" "$name" > "$dst" <<'PY'
import sys, yaml
doc = yaml.safe_load(open(sys.argv[1]))
cols = doc["headers"].get(sys.argv[2])
if cols is None:
    sys.stderr.write("unknown header name: %s\n" % sys.argv[2]); sys.exit(5)
print(",".join(cols))
PY
  printf 'header: %s\n' "$dst"
}

printf 'Scaffolding StelligenOS data layout v1.0 at: %s\n' "$abs_target"

mkdir -p \
  "$abs_target/00_REGISTRY" \
  "$abs_target/10_CANDIDATES" \
  "$abs_target/15_CONTEXTS" \
  "$abs_target/20_INSTANTIATIONS" \
  "$abs_target/30_EVIDENCE_LIBRARY/PACKAGES" \
  "$abs_target/90_ARCHIVE"

hdr registry_candidate_levels "$abs_target/00_REGISTRY/candidate_levels.csv"
hdr registry_candidate_type   "$abs_target/00_REGISTRY/candidate_type_registry.csv"
hdr registry_gateset          "$abs_target/00_REGISTRY/gateset_registry.csv"
hdr registry_gate             "$abs_target/00_REGISTRY/gate_registry.csv"
hdr registry_instantiation    "$abs_target/00_REGISTRY/instantiation_registry.csv"

for lvl in \
  L00_INDICATION L01_PATIENT_TERRITORY L02_ENDPOINT L03_MODALITY L04_ADC_TARGET \
  L05_ADC_EPITOPE L06_ANTIBODY_BINDER L07_LINKER L08_PAYLOAD L09_ADC_DESIGN \
  L10_ADC_HIT L11_ADC_LEAD L12_BIOMARKER L13_DEVELOPMENT_CANDIDATE L14_REGIMEN
do
  hdr candidate "$abs_target/10_CANDIDATES/${lvl}.csv"
done

hdr context_index          "$abs_target/15_CONTEXTS/context_index.csv"
hdr library_evidence_index "$abs_target/30_EVIDENCE_LIBRARY/evidence_index.csv"
hdr library_source_index   "$abs_target/30_EVIDENCE_LIBRARY/source_index.csv"

if [[ -n "$instantiation_id" ]]; then
  if [[ ! "$instantiation_id" =~ ^INST-[A-Z0-9-]+-v[0-9]+$ ]]; then
    printf 'Refusing: instantiation_id %s does not match INST-<UPPER-KEBAB>-v<N>.\n' "$instantiation_id" >&2
    exit 2
  fi
  inst_dir="$abs_target/20_INSTANTIATIONS/$instantiation_id"
  mkdir -p "$inst_dir/MATRICES" "$inst_dir/DECISIONS" "$inst_dir/GATESETS"
  hdr instantiation_candidates "$inst_dir/candidates.csv"
  hdr decisions                "$inst_dir/DECISIONS/decisions.csv"
  printf 'instantiation skeleton: %s\n' "$inst_dir"
  printf 'NOTE: fill %s/instantiation.yaml and create GATESETS/<gateset>-vN/<GATE>/ folders per the spec.\n' "$inst_dir"
fi

printf 'Done. This tree contains only directories and CSV header rows -- no data.\n'
