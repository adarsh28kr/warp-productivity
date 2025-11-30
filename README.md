# Warp Productivity Setup

Your personalized Warp terminal configuration for maximum productivity.

## Structure

```
~/.warp/
├── themes/
│   ├── productivity_dark.yaml  # Main dark theme (GitHub-inspired)
│   └── focus_mode.yaml         # Minimal distraction-free theme
├── workflows/
│   ├── git_workflows.yaml      # Git shortcuts
│   ├── dev_workflows.yaml      # Development tasks
│   └── productivity_workflows.yaml  # General productivity
├── productivity_aliases.zsh    # Shell aliases & functions
├── launch.yaml                 # Launch configurations
├── keybindings.yaml           # Keyboard shortcuts reference
└── README.md                  # This file
```

## Quick Start

1. **Apply Theme**: Warp Settings → Appearance → Themes → Import from `~/.warp/themes/`

2. **Aliases are auto-loaded** via `.zshrc` - restart terminal or run `source ~/.zshrc`

3. **Workflows**: Copy workflow files to Warp's workflow directory or use Warp's import feature

## Top Aliases

| Alias | Command |
|-------|---------|
| `gs` | git status |
| `gquick "msg"` | git add all + commit + push |
| `ll` | ls -lh |
| `mkcd dir` | mkdir + cd |
| `ports` | show listening ports |
| `killport 3000` | kill process on port |
| `serve` | start HTTP server |
| `timer 25` | pomodoro timer |
| `reload` | reload shell config |

## Key Workflows

- **Quick Commit & Push**: Stage all, commit, push in one command
- **New Feature Branch**: Create branch from updated main
- **Docker Cleanup**: Remove all stopped containers/images
- **Pomodoro Timer**: Focus timer with notification

## Customization

Edit `~/.warp/productivity_aliases.zsh` to add your own shortcuts.

Enjoy your productive terminal!
