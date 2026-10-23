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
try_log=""

stop() {
  printf 'STOP: %s\n' "$*" >&2
  exit 1
}

rollback() {
  local exit_code=$?
  [[ -z "$try_log" ]] || rm -f -- "$try_log"
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
    if not isinstance(match, dict):
        print(f"Unsupported match stanza for {device_id}; refusing to guess.", file=sys.stderr)
        sys.exit(1)
    # A Netplan ID is often a logical key, not an interface name. Only accept
    # an exact ID without match rules, or a name-only match for the target.
    for target in targets:
        exact_id = str(device_id) == target and not match and not config.get('set-name')
        exact_name_match = match == {'name': target} and config.get('set-name') in (None, target)
        if str(device_id) == target or match.get('name') == target or config.get('set-name') == target:
            if exact_id or exact_name_match:
                found[target].append(str(device_id))
            else:
                print(f"Ambiguous Netplan definition for {target}; refusing to change it.", file=sys.stderr)
                sys.exit(1)

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
try_log="$(mktemp /run/netplan-wait-online-try.XXXXXX)"
chmod 600 "$try_log"
if ! LC_ALL=C netplan try --timeout 120 2>&1 | tee "$try_log"; then
  stop 'netplan try failed; the script will restore the previous Netplan files.'
fi
grep -Fxq 'Configuration accepted.' "$try_log" \
  || stop 'Netplan did not report explicit acceptance; the script will restore the previous Netplan files.'
rm -f -- "$try_log"
try_log=""

# Netplan documents that a timeout/cancellation can return control after rollback.
# Do not trust the command's exit status alone: verify the accepted on-disk
# configuration and the generated networkd requirement for both exact IDs.
[[ -f "$OVERLAY" ]] || stop 'Netplan try did not retain the overlay; it may have been rejected or rolled back.'
python3 - "${NETPLAN_ID_BY_IF[enp1s0]}" "${NETPLAN_ID_BY_IF[enp3s0]}" <<'PY' \
  || stop 'Could not verify the accepted optional settings; the script will restore Netplan.'
import subprocess
import sys
import yaml

try:
    result = subprocess.run(['netplan', 'get', 'ethernets'], check=True,
                            capture_output=True, text=True)
    tree = yaml.safe_load(result.stdout) or {}
    if 'network' in tree:
        tree = tree['network']
    if 'ethernets' in tree:
        tree = tree['ethernets']
    for device_id in sys.argv[1:]:
        if tree[device_id].get('optional') is not True:
            raise ValueError('optional setting not retained')
except Exception as exc:
    print(f"Accepted Netplan settings could not be verified ({type(exc).__name__}).", file=sys.stderr)
    sys.exit(1)
PY
for iface in "${ETHERNET_IFS[@]}"; do
  generated="/run/systemd/network/10-netplan-${NETPLAN_ID_BY_IF[$iface]}.network"
  [[ -r "$generated" ]] && grep -Eq '^RequiredForOnline=no([[:space:]]|$)' "$generated" \
    || stop "Generated networkd config for $iface does not show RequiredForOnline=no."
done

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
