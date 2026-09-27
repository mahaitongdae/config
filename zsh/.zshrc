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
# Case-insensitive completion also treats hyphens and underscores alike.
HYPHEN_INSENSITIVE="true"
ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE='fg=245'
plugins=(
  git
  history-substring-search
  zsh-autosuggestions
  zsh-syntax-highlighting
)
zstyle ':omz:update' mode reminder
source "$ZSH/oh-my-zsh.sh"

# Select completion candidates with arrow keys; Shift-Tab moves backwards.
zstyle ':completion:*' menu select
bindkey '^[[Z' reverse-menu-complete
# Match history containing the typed text, including normal-mode arrow keys.
bindkey '^[[A' history-substring-search-up
bindkey '^[[B' history-substring-search-down
# Accept the grey suggestion with Ctrl-Space (or Right at end of line).
bindkey '^ ' autosuggest-accept

alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'

# Customize the prompt with `p10k configure`.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh
