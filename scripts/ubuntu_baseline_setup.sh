#!/usr/bin/env bash
# Owner-run Ubuntu baseline update and Python venv setup.
# This script is interactive; it never reboots, removes packages, or runs autoremove.
set -Eeuo pipefail

readonly PLAN_UPGRADE="${TMPDIR:-/tmp}/ubuntu-upgrade-plan-${USER:-user}.txt"
readonly PLAN_VENV="${TMPDIR:-/tmp}/python3-venv-plan-${USER:-user}.txt"

stop() {
  printf 'STOP: %s\n' "$*" >&2
  exit 1
}

confirm() {
  local prompt="$1" answer
  read -r -p "$prompt [y/N] " answer
  [[ "$answer" == [yY] ]] || stop '负责人未确认；没有继续。'
}

has_removals() {
  grep -Eq '^(Remv |The following packages will be REMOVED:)' "$1"
}

command -v apt-get >/dev/null || stop '未找到 apt-get。'
command -v sudo >/dev/null || stop '未找到 sudo。'
[[ -t 0 ]] || stop '请在可交互的本机终端运行，以便查看 sudo 和 APT 确认提示。'

printf '%s\n' '此脚本将刷新 APT 索引、交互式应用普通升级并安装 python3-venv。'
printf '%s\n' '不执行 full-upgrade、autoremove、包移除或自动重启。'
printf '%s\n' '如需修改网络/防火墙配置、重启或处理异常，请停止并联系负责人。'
confirm '确认开始？'

sudo -v
sudo apt-get update

printf '\n%s\n' '模拟普通升级；计划保存在本机临时文件：' "$PLAN_UPGRADE"
if ! sudo apt-get -s upgrade 2>&1 | tee "$PLAN_UPGRADE"; then
  stop 'APT upgrade 模拟失败。'
fi
has_removals "$PLAN_UPGRADE" && stop '升级计划包含软件包移除。'
printf '\n%s\n' '请检查上方升级计划。若涉及网络/防火墙相关组件、配置变更或不确定的操作，请停止。'
confirm '确认应用普通升级？'
sudo apt-get --no-remove -o Dpkg::Options::=--force-confold upgrade

if [[ -e /var/run/reboot-required ]]; then
  printf '%s\n' '系统标记需要重启；脚本不会重启。待重启完成后，再单独运行安装/检查步骤。'
  [[ ! -r /var/run/reboot-required.pkgs ]] || cat /var/run/reboot-required.pkgs
  exit 0
fi

printf '\n%s\n' '模拟安装 python3-venv；计划保存在本机临时文件：' "$PLAN_VENV"
if ! sudo apt-get -s install python3-venv 2>&1 | tee "$PLAN_VENV"; then
  stop 'python3-venv 安装模拟失败。'
fi
has_removals "$PLAN_VENV" && stop 'python3-venv 安装计划包含软件包移除。'
printf '\n%s\n' '请检查上方安装计划。'
confirm '确认安装 python3-venv？'
sudo apt-get --no-remove install python3-venv

printf '\n%s\n' '核验 dpkg 与 Python venv：'
sudo dpkg --audit
dpkg-query -W -f='${Status}\n' python3-venv
python3 -m venv --help >/dev/null && printf '%s\n' 'Python venv module available'
apt list --upgradable 2>/dev/null || true

printf '\n%s\n' '防火墙与网络服务只读状态：'
if command -v ufw >/dev/null; then sudo ufw status verbose; else printf '%s\n' 'UFW is not installed'; fi
systemctl is-active NetworkManager.service systemd-networkd.service systemd-networkd-wait-online.service || true
systemctl --no-pager --full status systemd-networkd-wait-online.service || true

printf '\n%s\n' 'Netplan 文件仅列出路径，不打印内容（配置可能含 Wi-Fi 密码、证书或私钥）：'
if compgen -G '/etc/netplan/*.yaml' >/dev/null; then
  printf '%s\n' /etc/netplan/*.yaml
else
  printf '%s\n' 'No YAML files found in /etc/netplan'
fi

if [[ -e /var/run/reboot-required ]]; then
  printf '%s\n' 'Reboot required; do not reboot automatically.'
else
  printf '%s\n' 'No reboot required.'
fi
printf '\n%s\n' '完成。请仅分享脱敏摘要，不要发送 APT 日志或任何凭据/网络配置原文。'
