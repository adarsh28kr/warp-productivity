# Warp Productivity Setup

Your personalized Warp terminal configuration for deep work and productivity.

## Structure

```
~/.warp/
├── focus/                         # Focus Mode v2 system
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

## Focus Mode v2

Expert-reviewed deep work system based on Cal Newport, Nir Eyal, and Essentialism principles.

**Philosophy**: Minimalist system with flexible sessions and no gamification. Focus on essential work.

### Quick Start

```bash
focus              # Start session (prompts for duration)
focus 90           # 90-min deep work block (recommended)
gm                 # Morning ritual - set ONE essential task
eod                # End of day review
fstats             # View your stats
focus review       # Weekly 80/20 Essentialism review
```

### Commands

| Command | Description |
|---------|-------------|
| `focus` | Start a focus session (flexible duration) |
| `focus 90` | Start 90-min deep work session |
| `focus 60` | Start 60-min standard session |
| `focus 30` | Start 30-min lighter task session |
| `focus status` | Show current status |
| `focus stats` | Today's statistics |
| `focus stats week` | Weekly summary |
| `focus review` | Weekly 80/20 review |
| `focus break` | Take a break |
| `gm` | Morning ritual |
| `eod` | End of day review |

### Features

- **Flexible sessions**: 90 min (deep work), 60 min (standard), 30 min (lighter tasks)
- **Essentialism prompts**: "Is this essential?" before each session
- **Implementation Intentions**: "When X, I will Y" for handling distractions
- **Morning ritual**: Set your ONE essential task for the day
- **Weekly 80/20 review**: Identify what produces real results
- **Clean statistics**: No gamification, just honest tracking

### Expert Alignment

| Expert | Principle | Implementation |
|--------|-----------|----------------|
| Cal Newport | 50-90 min deep work blocks | Flexible duration, 90 min recommended |
| Nir Eyal | Implementation intentions | "When X, I will Y" prompts |
| McKeown | Essentialism | "Is this essential?" checks |
| Tim Ferriss | 80/20 analysis | Weekly review command |

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

Built with behavioral science: Deep Work principles, implementation intentions, Essentialism methodology.
