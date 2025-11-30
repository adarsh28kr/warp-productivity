# Warp Productivity Setup

Your personalized Warp terminal configuration for deep work and productivity.

## Structure

```
~/.warp/
├── focus/                         # Focus Mode v3 system
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

## Focus Mode v3 - Executive-Level Deep Work System

Expert-reviewed system synthesizing neuroscience, environment design, and behavioral architecture.

**Philosophy**: Terminal as the command center for a complete life operating system—not just a focus timer, but an integrated system that optimizes your biology, environment, and behavior.

### Quick Start

```bash
gm                 # Morning ritual - circadian check + ONE essential task
focus 90           # 90-min deep work block (recommended)
prime              # Pre-focus visual priming (60 sec)
energy 4           # Log alertness level (1-5)
nsdr               # Non-Sleep Deep Rest protocol after intense work
fshutdown          # End-of-day shutdown ritual
fstats             # View your stats
```

### Core Commands

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
| `gm` | Morning ritual (circadian checks + intention) |
| `eod` | End of day review |

### Neuroscience Commands (Huberman Lab Protocols)

| Command | Description |
|---------|-------------|
| `prime` | Pre-focus visual priming (60 sec) - engage attention circuits |
| `primeq` | Quick visual focus (30 sec) |
| `nsdr` | Non-Sleep Deep Rest protocol for recovery |
| `energy 4` | Log alertness level (1-5) with factors |

### Behavioral Architecture Commands

| Command | Description |
|---------|-------------|
| `fplan` | Weekly time architecture (Sunday ritual) |
| `fdrift` | Between-session drift check |
| `fshutdown` | Shutdown complete ritual (cognitive closure) |
| `fjournal` | Identity reflection (weekly) |
| `finsights` | Behavioral analytics dashboard |
| `fdeep` | Deep commitment session (must type phrase to stop) |

### Commitment Levels

```bash
focus start 90 --commitment soft      # Press 's' to stop (easy)
focus start 90 --commitment standard  # Must explain why stopping (default)
focus start 90 --commitment deep      # Must type "I choose to break my commitment"
```

### Features

**Neuroscience Foundation**
- Pre-focus visual priming (60 sec) - faster focus onset
- Circadian optimization - morning sunlight, caffeine timing
- Ultradian rhythm enforcement - 20 min rest after 90 min sessions
- Energy tracking with peak hours analysis
- NSDR (Non-Sleep Deep Rest) for recovery

**Environment Automation**
- macOS Focus Mode integration (Do Not Disturb)
- Auto-quit distracting apps (Slack, Discord, Messages)
- Voice notifications with spoken announcements

**Behavioral Architecture**
- Commitment escalation (soft → standard → deep)
- Daily themes (Building, Thinking, Collaboration, etc.)
- Shutdown ritual with verbal cue
- Drift detection between sessions
- Identity journaling and progression tracking

### Expert Alignment

| Expert | Principle | Implementation |
|--------|-----------|----------------|
| Andrew Huberman | Ultradian rhythms (90 min) | Enforce rest after 90-min blocks |
| Andrew Huberman | Morning sunlight | Circadian prompts in `gm` |
| Andrew Huberman | NSDR for recovery | `nsdr` command |
| Andrew Huberman | Visual focus priming | `prime` command |
| Cal Newport | Fixed-schedule productivity | Weekly plan sets shutdown times |
| Cal Newport | Shutdown complete ritual | `fshutdown` with verbal cue |
| Cal Newport | Deep work blocks | 90-min default, theme days |
| Nir Eyal | Implementation intentions | "When X, I will Y" prompts |
| Nir Eyal | Environment design | macOS Focus Mode, app blocking |
| James Clear | Identity > outcomes | `fjournal`, daily identity statements |
| James Clear | Habit stacking | Morning ritual anchoring |
| BJ Fogg | Tiny habits | Pre-focus priming (60 sec) |
| Greg McKeown | Essentialism | 80/20 review, weekly questions |

### macOS Shortcuts Setup

For full environment automation, create these Shortcuts:

1. **Enable Deep Work Focus**
   - Add: Set Focus → Do Not Disturb → On

2. **Disable Deep Work Focus**
   - Add: Set Focus → Off

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

Built with behavioral science: Huberman Lab neuroscience, Cal Newport's Deep Work, Nir Eyal's Indistractable, James Clear's Atomic Habits, and Greg McKeown's Essentialism.
