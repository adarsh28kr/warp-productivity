# =============================================================================
# Productivity Aliases & Functions for Warp Terminal
# Source this file in your .zshrc: source ~/.warp/productivity_aliases.zsh
# =============================================================================

# -----------------------------------------------------------------------------
# Navigation Shortcuts
# -----------------------------------------------------------------------------
alias ..="cd .."
alias ...="cd ../.."
alias ....="cd ../../.."
alias ~="cd ~"
alias -- -="cd -"

# Quick directory bookmarks
alias desk="cd ~/Desktop"
alias docs="cd ~/Documents"
alias dl="cd ~/Downloads"
alias proj="cd ~/Projects 2>/dev/null || cd ~/Desktop"

# -----------------------------------------------------------------------------
# Enhanced ls Commands
# -----------------------------------------------------------------------------
alias l="ls -lah"
alias la="ls -lAh"
alias ll="ls -lh"
alias ls="ls -G"  # Colorized output on macOS
alias lt="ls -lahtr"  # Sort by time, newest last
alias lsize="ls -lahS"  # Sort by size

# -----------------------------------------------------------------------------
# Safety Nets
# -----------------------------------------------------------------------------
alias rm="rm -i"
alias cp="cp -i"
alias mv="mv -i"
alias mkdir="mkdir -pv"

# -----------------------------------------------------------------------------
# Git Productivity
# -----------------------------------------------------------------------------
alias g="git"
alias gs="git status"
alias ga="git add"
alias gaa="git add --all"
alias gc="git commit -m"
alias gca="git commit -am"
alias gp="git push"
alias gpl="git pull"
alias gf="git fetch"
alias gb="git branch"
alias gco="git checkout"
alias gcob="git checkout -b"
alias gd="git diff"
alias gds="git diff --staged"
alias gl="git log --oneline -20"
alias glg="git log --graph --oneline --decorate -20"
alias gst="git stash"
alias gstp="git stash pop"
alias grh="git reset --hard"
alias grs="git reset --soft HEAD~1"

# Quick git workflow
gquick() {
    git add --all && git commit -m "${1:-Quick update}" && git push
}

# Show changed files
alias gchanged="git diff --name-only"

# -----------------------------------------------------------------------------
# Development Shortcuts
# -----------------------------------------------------------------------------
# Python
alias py="python3"
alias pip="pip3"
alias venv="python3 -m venv venv"
alias activate="source venv/bin/activate"
alias pipreq="pip freeze > requirements.txt"

# Node.js
alias ni="npm install"
alias nr="npm run"
alias nrd="npm run dev"
alias nrb="npm run build"
alias nrt="npm run test"
alias ns="npm start"

# Yarn
alias yi="yarn install"
alias ya="yarn add"
alias yr="yarn run"
alias yd="yarn dev"
alias yb="yarn build"

# Docker
alias d="docker"
alias dc="docker compose"
alias dps="docker ps"
alias dpsa="docker ps -a"
alias dimg="docker images"
alias dexec="docker exec -it"
alias dlogs="docker logs -f"
alias dstop="docker stop \$(docker ps -q)"
alias dprune="docker system prune -af"

# Kubernetes
alias k="kubectl"
alias kgp="kubectl get pods"
alias kgs="kubectl get services"
alias kgd="kubectl get deployments"
alias klogs="kubectl logs -f"

# -----------------------------------------------------------------------------
# File Operations
# -----------------------------------------------------------------------------
# Find files quickly
ff() {
    find . -type f -name "*$1*" 2>/dev/null
}

# Find directories
fd() {
    find . -type d -name "*$1*" 2>/dev/null
}

# Search in files (grep wrapper)
search() {
    grep -rn "$1" . --include="$2" 2>/dev/null
}

# Create and cd into directory
mkcd() {
    mkdir -p "$1" && cd "$1"
}

# Extract any archive
extract() {
    if [ -f "$1" ]; then
        case "$1" in
            *.tar.bz2)   tar xjf "$1"     ;;
            *.tar.gz)    tar xzf "$1"     ;;
            *.bz2)       bunzip2 "$1"     ;;
            *.rar)       unrar x "$1"     ;;
            *.gz)        gunzip "$1"      ;;
            *.tar)       tar xf "$1"      ;;
            *.tbz2)      tar xjf "$1"     ;;
            *.tgz)       tar xzf "$1"     ;;
            *.zip)       unzip "$1"       ;;
            *.Z)         uncompress "$1"  ;;
            *.7z)        7z x "$1"        ;;
            *)           echo "'$1' cannot be extracted via extract()" ;;
        esac
    else
        echo "'$1' is not a valid file"
    fi
}

# Quick backup
backup() {
    cp "$1" "$1.backup.$(date +%Y%m%d_%H%M%S)"
}

# -----------------------------------------------------------------------------
# System & Process Management
# -----------------------------------------------------------------------------
alias ports="lsof -i -P -n | grep LISTEN"
alias myip="curl -s ifconfig.me && echo"
alias localip="ipconfig getifaddr en0"
alias cpu="top -l 1 | grep -E '^CPU'"
alias mem="top -l 1 | grep -E '^Phys'"
alias disk="df -h"

# Kill process on port
killport() {
    lsof -ti:$1 | xargs kill -9 2>/dev/null && echo "Killed process on port $1" || echo "No process on port $1"
}

# Quick process search
psg() {
    ps aux | grep -v grep | grep "$1"
}

# -----------------------------------------------------------------------------
# Productivity Utilities
# -----------------------------------------------------------------------------
# Quick note taking
note() {
    local notes_dir="$HOME/.notes"
    mkdir -p "$notes_dir"
    if [ -z "$1" ]; then
        ls -lt "$notes_dir" | head -20
    else
        echo "$(date '+%Y-%m-%d %H:%M'): $*" >> "$notes_dir/quick_notes.md"
        echo "Note added!"
    fi
}

# Timer/pomodoro
timer() {
    local seconds=$((${1:-25} * 60))
    echo "Timer set for ${1:-25} minutes..."
    sleep $seconds && osascript -e 'display notification "Time is up!" with title "Timer"' && say "Time is up"
}

# Quick HTTP server
serve() {
    local port="${1:-8000}"
    echo "Serving on http://localhost:$port"
    python3 -m http.server "$port"
}

# Weather
weather() {
    curl -s "wttr.in/${1:-}"
}

# Cheat sheet
cheat() {
    curl -s "cheat.sh/$1"
}

# -----------------------------------------------------------------------------
# Warp-Specific Enhancements
# -----------------------------------------------------------------------------
# Clear scrollback completely
alias cls="clear && printf '\e[3J'"

# Reload shell config
alias reload="source ~/.zshrc && echo 'Shell reloaded!'"

# Edit common config files
alias zshconfig="$EDITOR ~/.zshrc"
alias warpconfig="open ~/.warp"

# -----------------------------------------------------------------------------
# Startup Tips System
# -----------------------------------------------------------------------------
show_tip() {
    local tips=(
        # Navigation
        "gs|Check git status quickly|gs"
        "gquick|Stage, commit & push in one command|gquick \"your message\""
        "gl|See last 20 commits in one line each|gl"
        "glg|See commit graph with branches|glg"
        "gco|Switch branches fast|gco branch-name"
        "gcob|Create and switch to new branch|gcob feature/cool-thing"

        # File navigation
        "..|Go up one directory|.."
        "...|Go up two directories|..."
        "desk|Jump to Desktop|desk"
        "dl|Jump to Downloads|dl"
        "mkcd|Create folder and cd into it|mkcd new-project"
        "-|Go back to previous directory|-"

        # Listing files
        "ll|List files with details|ll"
        "lt|List files by time (newest last)|lt"
        "lsize|List files by size (largest first)|lsize"

        # Git workflow
        "gaa|Stage all changes|gaa"
        "gc|Commit with message|gc \"fix: resolved bug\""
        "gd|See unstaged changes|gd"
        "gds|See staged changes|gds"
        "gst|Stash changes temporarily|gst"
        "gstp|Pop stashed changes|gstp"

        # Development
        "nrd|Run npm dev server|nrd"
        "ni|Install npm packages|ni"
        "activate|Activate Python venv|activate"
        "serve|Start HTTP server in current dir|serve 3000"

        # Docker
        "dps|List running containers|dps"
        "dlogs|Follow container logs|dlogs container-name"
        "dprune|Clean up Docker (all unused)|dprune"

        # System
        "ports|Show what's using which ports|ports"
        "killport|Kill process on a port|killport 3000"
        "myip|Show your public IP|myip"
        "psg|Find a running process|psg node"

        # Productivity
        "note|Save a quick note|note Remember to review PR"
        "timer|Start a focus timer|timer 25"
        "weather|Check the weather|weather London"
        "cheat|Get command cheatsheet|cheat tar"
        "ff|Find files by name|ff config"
        "extract|Extract any archive|extract file.tar.gz"
        "backup|Quick backup a file|backup important.txt"

        # Warp specific
        "cls|Clear screen completely|cls"
        "reload|Reload shell config|reload"
        "tips|See another tip|tips"
        "alltips|Browse all tips|alltips"

        # Focus Mode (Deep Work)
        "focus|Start a deep work session (flexible duration)|focus"
        "focus 90|90-min deep work session (recommended)|focus 90"
        "gm|Morning ritual - set your ONE essential task|gm"
        "eod|End of day review and reflection|eod"
        "fstats|View your focus statistics|fstats"
        "freview|Weekly 80/20 review (Essentialism)|focus review"
    )

    local total=${#tips[@]}
    local selected=()
    local indices=()

    # Pick 5 unique random tips
    while [ ${#selected[@]} -lt 5 ]; do
        local idx=$((RANDOM % total + 1))
        # Check if already selected
        local exists=0
        for i in "${indices[@]}"; do
            [ "$i" = "$idx" ] && exists=1 && break
        done
        if [ $exists -eq 0 ]; then
            indices+=($idx)
            selected+=("${tips[$idx]}")
        fi
    done

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  💡 TODAY'S PRODUCTIVITY TIPS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    local num=1
    for tip in "${selected[@]}"; do
        local cmd=$(echo "$tip" | cut -d'|' -f1)
        local desc=$(echo "$tip" | cut -d'|' -f2)
        local example=$(echo "$tip" | cut -d'|' -f3)
        printf "  %d. %-12s %s\n" $num "$cmd" "$desc"
        printf "     └─ %s\n" "$example"
        echo ""
        ((num++))
    done

    echo "  Type 'tips' for more  •  'alltips' for full list"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# Show another random tip
tips() {
    show_tip
}

# Browse all tips
alltips() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  📚 ALL PRODUCTIVITY SHORTCUTS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "  GIT"
    echo "  ───"
    echo "  gs        → git status"
    echo "  gquick    → add all + commit + push"
    echo "  gl        → log (oneline)"
    echo "  glg       → log graph"
    echo "  gco       → checkout"
    echo "  gcob      → checkout -b (new branch)"
    echo "  gaa       → add all"
    echo "  gc \"msg\"  → commit"
    echo "  gp        → push"
    echo "  gpl       → pull"
    echo "  gd        → diff"
    echo "  gds       → diff staged"
    echo "  gst       → stash"
    echo "  gstp      → stash pop"
    echo ""
    echo "  NAVIGATION"
    echo "  ──────────"
    echo "  ..        → up one dir"
    echo "  ...       → up two dirs"
    echo "  -         → previous dir"
    echo "  desk      → ~/Desktop"
    echo "  dl        → ~/Downloads"
    echo "  mkcd dir  → mkdir + cd"
    echo ""
    echo "  FILES"
    echo "  ─────"
    echo "  ll        → list detailed"
    echo "  lt        → list by time"
    echo "  lsize     → list by size"
    echo "  ff name   → find files"
    echo "  extract   → unpack any archive"
    echo "  backup    → quick file backup"
    echo ""
    echo "  DEV"
    echo "  ───"
    echo "  nrd       → npm run dev"
    echo "  ni        → npm install"
    echo "  serve     → http server"
    echo "  activate  → python venv"
    echo "  dps       → docker ps"
    echo "  killport  → kill port process"
    echo ""
    echo "  PRODUCTIVITY"
    echo "  ────────────"
    echo "  note      → save quick note"
    echo "  timer 25  → pomodoro timer"
    echo "  ports     → show listening ports"
    echo "  myip      → show public IP"
    echo "  weather   → current weather"
    echo "  cheat     → command cheatsheet"
    echo ""
    echo "  DEEP WORK (Focus Mode v2)"
    echo "  ─────────────────────────"
    echo "  focus       → start session (prompts for duration)"
    echo "  focus 90    → 90-min deep work (recommended)"
    echo "  focus 60    → 60-min standard session"
    echo "  focus 30    → 30-min lighter task"
    echo "  gm          → morning ritual (set ONE essential task)"
    echo "  eod         → end of day review"
    echo "  fstats      → view focus statistics"
    echo "  focus review→ weekly 80/20 Essentialism review"
    echo ""
    echo "  Type 'tips' for a random tip"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# -----------------------------------------------------------------------------
# PATH & Environment
# -----------------------------------------------------------------------------
export EDITOR="code"  # Change to your preferred editor
export VISUAL="$EDITOR"

# Better history
export HISTSIZE=50000
export SAVEHIST=50000
setopt HIST_IGNORE_DUPS
setopt HIST_IGNORE_SPACE
setopt SHARE_HISTORY

# -----------------------------------------------------------------------------
# Focus Mode v2 Integration (Deep Work System)
# -----------------------------------------------------------------------------
# Based on Cal Newport, Nir Eyal, and Essentialism principles
# No gamification - just clean tracking and evidence-based practices

alias focus="python3 ~/.warp/focus/focus.py"
alias f="focus"
alias fst="focus status"
alias fb="focus break"
alias fstats="focus stats"
alias freview="focus review"

# Morning and evening rituals
alias gm="focus gm"
alias eod="focus eod"

# Quick session shortcuts (flexible duration)
f90() { focus start 90 "$@"; }   # Deep work (recommended)
f60() { focus start 60 "$@"; }   # Standard session
f30() { focus start 30 "$@"; }   # Lighter tasks

# Show startup tip
show_tip
