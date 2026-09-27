# Enable Powerlevel10k instant prompt near the top of this file.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# Keep user-installed commands available, including Codex.
typeset -U path PATH
path=("$HOME/.local/bin" "$HOME/bin" $path)
export PATH

export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="powerlevel10k/powerlevel10k"
plugins=(git)
zstyle ':omz:update' mode reminder
source "$ZSH/oh-my-zsh.sh"

alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'

# Customize the prompt with `p10k configure`.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh
