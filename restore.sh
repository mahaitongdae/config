#!/usr/bin/env bash
set -euo pipefail

# Run as your normal user. Dependencies are installed separately (see README).
repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
target_home="${1:-$HOME}"
if [[ "$target_home" != /* || ! -d "$target_home" ]]; then
  echo 'Usage: bash restore.sh [existing absolute home directory]' >&2
  exit 1
fi
files=(.zshrc .zprofile .p10k.zsh .profile)
kitty_files=(kitty.conf current-theme.conf quick-access-terminal.conf)
for file in "${files[@]}"; do test -f "$repo_dir/zsh/$file"; done
for file in "${kitty_files[@]}"; do test -f "$repo_dir/kitty/$file"; done
umask 077
backup_dir="$(mktemp -d "$target_home/.config-backup-$(date +%Y%m%d-%H%M%S)-XXXXXX")"
restore_file() {
  local source="$1" relative="$2" destination="$target_home/$2"
  if [[ -e "$destination" || -L "$destination" ]]; then
    mkdir -p -- "$backup_dir/$(dirname -- "$relative")"
    mv -- "$destination" "$backup_dir/$relative"
  fi
  mkdir -p -- "$(dirname -- "$destination")"
  cp -- "$source" "$destination"
}
for file in "${files[@]}"; do restore_file "$repo_dir/zsh/$file" "$file"; done
for file in "${kitty_files[@]}"; do
  restore_file "$repo_dir/kitty/$file" ".config/kitty/$file"
done
printf 'Restored configuration to: %s\nPrevious files saved to: %s\n' "$target_home" "$backup_dir"
printf 'Install the dependencies listed in README.md, then restart kitty and run: exec zsh -l\n'
