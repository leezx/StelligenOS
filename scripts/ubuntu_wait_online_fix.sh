#!/usr/bin/env bash
# Mark only disconnected Ethernet ports optional so boot does not wait for cables.
# Run from the Ubuntu machine's visible local terminal; netplan try is interactive.
set -Eeuo pipefail

readonly WIFI_IF="wlo1"
readonly ETHERNET_IFS=(enp1s0 enp3s0)
readonly ORIGIN_HINT="90-codex-wait-online-optional"
readonly OVERLAY="/etc/netplan/${ORIGIN_HINT}.yaml"
changed=0
keep_change=0
backup_dir=""

stop() {
  printf 'STOP: %s\n' "$*" >&2
  exit 1
}

rollback() {
  local exit_code=$?
  if (( changed == 1 && keep_change == 0 )); then
    printf '\n%s\n' 'Configuration was not confirmed; restoring the previous Netplan files.' >&2
    rm -f -- "$OVERLAY"
    netplan generate && netplan apply || printf '%s\n' 'Automatic restore command failed; use the backup directory printed above.' >&2
  fi
  exit "$exit_code"
}
trap rollback EXIT

if (( EUID != 0 )); then
  [[ -t 0 ]] || stop 'Run from a visible interactive terminal so sudo and netplan confirmation prompts can be answered.'
  exec sudo -- "$0" "$@"
fi
[[ -t 0 ]] || stop 'Run from a visible interactive terminal.'
command -v netplan >/dev/null || stop 'netplan is not installed.'
command -v networkctl >/dev/null || stop 'networkctl is not installed.'
[[ -d /etc/netplan ]] || stop '/etc/netplan is missing.'
[[ ! -e "$OVERLAY" ]] || stop "$OVERLAY already exists; refusing to overwrite it."

networkctl status "$WIFI_IF" --no-pager 2>/dev/null | grep -Fq 'State: routable' \
  || stop "$WIFI_IF is not currently routable; refusing to change network configuration."
for iface in "${ETHERNET_IFS[@]}"; do
  networkctl status "$iface" --no-pager 2>/dev/null | grep -Fq 'State: no-carrier' \
    || stop "$iface is no longer in no-carrier state; inspect before changing it."
done

ids_text="$(python3 - <<'PY'
import subprocess
import sys

try:
    import yaml
except Exception as exc:
    print(f"Cannot import PyYAML ({type(exc).__name__}).", file=sys.stderr)
    sys.exit(1)

try:
    result = subprocess.run(['netplan', 'get', 'ethernets'], check=True,
                            capture_output=True, text=True)
    tree = yaml.safe_load(result.stdout) or {}
except Exception as exc:
    print(f"Cannot read merged Netplan Ethernet settings ({type(exc).__name__}).", file=sys.stderr)
    sys.exit(1)

if isinstance(tree, dict) and 'network' in tree:
    tree = tree['network']
if isinstance(tree, dict) and 'ethernets' in tree:
    tree = tree['ethernets']
if not isinstance(tree, dict):
    print('Netplan Ethernet settings are not a mapping.', file=sys.stderr)
    sys.exit(1)

targets = {'enp1s0', 'enp3s0'}
found = {target: [] for target in targets}
for device_id, config in tree.items():
    if not isinstance(config, dict):
        continue
    match = config.get('match', {}) or {}
    names = {str(device_id), str(config.get('set-name', '')),
             str(match.get('name', '')) if isinstance(match, dict) else ''}
    for target in targets & names:
        found[target].append(str(device_id))

for target in sorted(targets):
    matches = found[target]
    if len(matches) != 1:
        print(f"Expected one Netplan Ethernet definition for {target}; found {len(matches)}.", file=sys.stderr)
        sys.exit(1)
    device_id = matches[0]
    if not device_id or any(ch not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for ch in device_id):
        print(f"Unsupported Netplan identifier for {target}; refusing to change it.", file=sys.stderr)
        sys.exit(1)
    print(f"{target}={device_id}")
PY
)" || stop 'Could not safely identify the Netplan IDs for both Ethernet ports.'

declare -A NETPLAN_ID_BY_IF=()
while IFS='=' read -r iface id; do
  [[ -n "$iface" && -n "$id" ]] || continue
  NETPLAN_ID_BY_IF["$iface"]="$id"
done <<< "$ids_text"
for iface in "${ETHERNET_IFS[@]}"; do
  [[ -n "${NETPLAN_ID_BY_IF[$iface]:-}" ]] || stop "No safe Netplan ID found for $iface."
done

printf 'Wi-Fi %s is routable. Disconnected ports will remain enabled but become optional at boot:\n' "$WIFI_IF"
printf '  %s -> %s\n' enp1s0 "${NETPLAN_ID_BY_IF[enp1s0]}"
printf '  %s -> %s\n' enp3s0 "${NETPLAN_ID_BY_IF[enp3s0]}"
read -r -p 'Continue? [y/N] ' answer
[[ "$answer" == [yY] ]] || stop 'No changes made.'

umask 077
backup_dir="$(mktemp -d /root/netplan-wait-online-backup.XXXXXX)"
cp -a /etc/netplan/. "$backup_dir/"
printf 'Protected backup: %s\n' "$backup_dir"

changed=1
for iface in "${ETHERNET_IFS[@]}"; do
  netplan set --origin-hint "$ORIGIN_HINT" "ethernets.${NETPLAN_ID_BY_IF[$iface]}.optional=true"
done
netplan generate

printf '\n%s\n' 'Applying with Netplan rollback protection. Confirm only if the Wi-Fi/SSH connection still works.'
netplan try --timeout 120

if ! networkctl status "$WIFI_IF" --no-pager 2>/dev/null | grep -Fq 'State: routable'; then
  stop "$WIFI_IF did not return to routable state. The script will remove its override and restore Netplan."
fi

systemctl reset-failed systemd-networkd-wait-online.service || true
systemctl start systemd-networkd-wait-online.service \
  || stop 'wait-online still fails after the change; the script will restore the previous Netplan files.'

keep_change=1
trap - EXIT
printf '\n%s\n' 'Fix confirmed. Ethernet remains enabled; wait-online no longer blocks on its absent cable.'
systemctl --no-pager --full status systemd-networkd-wait-online.service || true
