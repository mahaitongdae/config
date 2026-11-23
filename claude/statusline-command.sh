#!/bin/bash
# Claude Code status line in the style of ~/.config/starship.toml:
# plain colored text, no backgrounds.
#   dir on  branch [status] · ctx N% bar · in/out · cache N% · $cost · 5h N% · model effort
input=$(cat)

# Single jq call; fields joined by US (0x1f, non-whitespace so empty fields survive `read`).
IFS=$'\x1f' read -r cwd model used tin tout cache cost five effort think < <(echo "$input" | jq -r '
  def h: if . >= 1000000 then ((. / 100000 | floor) / 10 | tostring) + "M"
         elif . >= 10000 then ((. / 1000 | round | tostring) + "k")
         elif . >= 1000 then ((. / 100 | floor) / 10 | tostring) + "k"
         else (. | round | tostring) end;
  (.context_window.current_usage // null) as $u
  | [ (.workspace.current_dir // .cwd),
      .model.display_name,
      .context_window.used_percentage,
      (.context_window.total_input_tokens  | if type == "number" then h else null end),
      (.context_window.total_output_tokens | if type == "number" then h else null end),
      (if ($u | type) == "object" and ($u.cache_read_input_tokens | type) == "number" then
         (($u.cache_read_input_tokens) + ($u.cache_creation_input_tokens // 0) + ($u.input_tokens // 0)) as $d
         | if $d > 0 then ($u.cache_read_input_tokens / $d * 100 | round) else null end
       else null end),
      .cost.total_cost_usd,
      (.rate_limits.five_hour | (.used_percentage // .utilization)),
      (.effort.level // .effort),
      (.thinking.enabled)
    ] | map(if . == null then "" else tostring end) | join("\u001f")' 2>/dev/null)
cwd=${cwd:-$PWD}

E=$'\033['
R="${E}0m"
c() { printf '%s%sm' "$E" "$1"; }   # SGR helper: c "1;35" -> bold purple
DOT=" $(c 90)·$R "
I_BRANCH=$'\xee\x82\xa0'   # U+E0A0, starship's default git_branch symbol

# color by percentage: green < 50, yellow < 80, red after
pct_color() { if [ "$1" -lt 50 ]; then echo 32; elif [ "$1" -lt 80 ]; then echo 33; else echo 31; fi; }

# directory: truncate_to_repo, at most 3 components (starship truncation_length = 3)
top=""
[ -d "$cwd" ] && top=$(GIT_OPTIONAL_LOCKS=0 git -C "$cwd" rev-parse --show-toplevel 2>/dev/null)
if [ -n "$top" ]; then
  path=${top##*/}${cwd#"$top"}
else
  path=${cwd/#$HOME/\~}
fi
path=$(printf '%s' "$path" | awk -F/ '{ n = NF; if (n > 3) { s = $(n-2) "/" $(n-1) "/" $n; print s } else print }')
line1="$(c "1;36")$path$R"

# git branch and status
if [ -n "$top" ]; then
  branch=$(GIT_OPTIONAL_LOCKS=0 git -C "$cwd" symbolic-ref --short HEAD 2>/dev/null \
    || GIT_OPTIONAL_LOCKS=0 git -C "$cwd" rev-parse --short HEAD 2>/dev/null)
  line1+=" on $(c "1;35")$I_BRANCH $branch$R"
  st=$(GIT_OPTIONAL_LOCKS=0 git -C "$cwd" status --porcelain=v1 --branch 2>/dev/null)
  flags=""
  grep -q '^[MADRC]' <<<"$st" && flags+="+"
  grep -q '^.[MD]' <<<"$st" && flags+="!"
  grep -q '^??' <<<"$st" && flags+="?"
  head=$(head -1 <<<"$st")
  [[ $head == *ahead* ]] && flags+="⇡"
  [[ $head == *behind* ]] && flags+="⇣"
  [ -n "$flags" ] && line1+=" $(c 31)[$flags]$R"
fi

# usage metrics, then the model last
parts=()
if [ -n "$used" ]; then
  pct=$(printf '%.0f' "$used")
  filled=$(( (pct * 8 + 50) / 100 )); [ "$filled" -gt 8 ] && filled=8
  bar=""
  for ((i = 0; i < 8; i++)); do [ "$i" -lt "$filled" ] && bar+="▓" || bar+="░"; done
  parts+=("ctx $(c "$(pct_color "$pct")")${pct}% $bar$R")
fi
[ -n "$tin" ] && [ -n "$tout" ] && parts+=("$(c 90)in $tin out $tout$R")
[ -n "$cache" ] && parts+=("cache $(c "$(pct_color $((100 - cache)))")${cache}%$R")
[ -n "$cost" ] && parts+=("$(c 33)$(printf '$%.2f' "$cost")$R")
if [ -n "$five" ]; then
  fpct=$(printf '%.0f' "$five")
  parts+=("5h $(c "$(pct_color "$fpct")")${fpct}%$R")
fi

# model, followed by thinking effort (dim for low/medium, magenta for high+; "think off" when disabled)
if [ -n "$model" ]; then
  m="$(c "1;34")$model$R"
  if [ "$think" = "false" ]; then
    m+=" $(c 90)think off$R"
  elif [ -n "$effort" ]; then
    case $effort in low|medium) ec=90 ;; high) ec=35 ;; *) ec="1;35" ;; esac
    m+=" $(c "$ec")$effort$R"
  fi
  parts+=("$m")
fi

out=$line1
for p in "${parts[@]}"; do out+="$DOT$p"; done
printf '%s\n' "$out"
