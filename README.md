# Warp Productivity Setup

Your personalized Warp terminal configuration for maximum productivity.

## Structure

```
~/.warp/
├── focus/                         # Focus Mode system
│   ├── focus.py                   # CLI application
│   ├── config.yaml               # Settings
│   ├── quotes.txt                # Motivational quotes
│   └── data/                     # Session logs & stats
├── themes/
│   ├── productivity_dark.yaml    # Main dark theme
│   └── focus_mode.yaml           # Minimal focus theme
├── workflows/
│   ├── git_workflows.yaml        # Git shortcuts
│   ├── dev_workflows.yaml        # Development tasks
│   ├── productivity_workflows.yaml
│   └── focus_workflows.yaml      # Focus Mode workflows
├── productivity_aliases.zsh      # Shell aliases & functions
├── launch.yaml                   # Launch configurations
├── keybindings.yaml             # Keyboard shortcuts
└── README.md
```

## Focus Mode

Evidence-based productivity system with XP, levels, streaks, and rituals.

### Quick Start

```bash
focus              # Start 20-min focus session
gm                 # Morning ritual (set daily intention)
eod                # End of day review
fstats             # View today's stats
fstreak            # Check your streaks
```

### Commands

| Command | Description |
|---------|-------------|
| `focus` | Start a 20-min focus session |
| `focus 15 "task"` | Custom duration with task |
| `focus status` | Show current status |
| `focus stats` | Today's statistics |
| `focus stats week` | Weekly summary |
| `focus streak` | Streak progress |
| `focus break` | Take a break |
| `gm` | Morning ritual |
| `eod` | End of day review |

### Features

- **20-min sessions** matching your natural focus rhythm
- **XP & Levels**: Earn points, level up from Apprentice to Legend
- **Streaks**: Daily streaks with freeze protection
- **Implementation Intentions**: "When X, I will Y" to handle distractions
- **Morning/Evening Rituals**: Set goals, reflect, plan

## Shell Aliases

| Alias | Command |
|-------|---------|
| `gs` | git status |
| `gquick "msg"` | git add + commit + push |
| `ll` | ls -lh |
| `mkcd dir` | mkdir + cd |
| `killport 3000` | kill process on port |
| `serve` | HTTP server |
| `tips` | Random productivity tip |
| `alltips` | Full tip cheatsheet |

## Startup Tips

Every terminal shows 5 random productivity tips. Use:
- `tips` - See more tips
- `alltips` - Browse all shortcuts

## Installation

Aliases are auto-loaded via `.zshrc`. To reload:
```bash
source ~/.zshrc
```

## Dependencies

Focus Mode requires:
```bash
pip install rich click pyyaml
```

Built with behavioral science: Pomodoro, implementation intentions, variable rewards, streak psychology.
