#!/usr/bin/env python3
"""
Focus Mode v3: Executive-Level Deep Work Architecture

Synthesizes three expert perspectives:
1. Neuroscience (Huberman Lab): Dopamine optimization, ultradian rhythms, circadian alignment
2. Environment Design: macOS automation, distraction blocking, environmental cues
3. Behavioral Architecture (Clear/Fogg): Habit stacking, commitment devices, identity

Philosophy: Terminal as command center for a complete life operating system.
"""

import json
import subprocess
import sys
import time
import threading
from datetime import datetime, date, timedelta
from pathlib import Path

import click
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.table import Table

# Initialize Rich console
console = Console()

# Paths
FOCUS_DIR = Path.home() / ".warp" / "focus"
CONFIG_FILE = FOCUS_DIR / "config.yaml"
DATA_DIR = FOCUS_DIR / "data"
SESSIONS_FILE = DATA_DIR / "sessions.json"
STATS_FILE = DATA_DIR / "stats.json"
ACTIVE_SESSION_FILE = DATA_DIR / ".active_session.json"
BLOCKLIST_FILE = FOCUS_DIR / "blocklist.txt"


# =============================================================================
# Core Utilities
# =============================================================================

def load_config() -> dict:
    """Load configuration from YAML file."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return yaml.safe_load(f) or {}
    return get_default_config()


def get_default_config() -> dict:
    """Return default configuration."""
    return {
        "session": {"suggested_durations": [90, 60, 30], "short_break": 5, "long_break": 15},
        "notifications": {"enabled": True, "sound": "Glass", "voice": True},
        "neuroscience": {
            "pre_focus_priming": {"enabled": True, "auto_prompt": True, "visual_focus_duration": 60},
            "circadian": {"track_wake_time": True, "prompt_sunlight": True, "track_caffeine": True},
            "ultradian": {"enforce_rest_after_90": True, "minimum_rest_minutes": 20, "prompt_nsdr": True},
            "energy_tracking": {"enabled": True}
        },
        "environment": {
            "macos_focus_mode": {"enabled": True, "mode_name": "Do Not Disturb"},
            "blocking": {"apps": {"quit_on_start": ["Slack", "Discord"]}, "websites": {"enabled": False}},
            "visual_cues": {"enable_night_shift": False}
        },
        "behavioral": {
            "daily_themes": {
                "enabled": True,
                "themes": {
                    "Monday": {"name": "Deep Work - Building", "description": "Heads-down coding and creation"},
                    "Tuesday": {"name": "Deep Work - Thinking", "description": "Architecture, design, complex problems"},
                    "Wednesday": {"name": "Collaboration Day", "description": "Meetings, pairing, code review"},
                    "Thursday": {"name": "Deep Work - Finishing", "description": "Complete what was started"},
                    "Friday": {"name": "Review & Close", "description": "PR reviews, documentation, planning"},
                    "Saturday": {"name": "Rest or Light Admin", "description": "Catch-up only if needed"},
                    "Sunday": {"name": "Weekly Planning", "description": "Plan the week, journal, rest"}
                }
            },
            "commitment": {"default_level": "standard"},
            "shutdown": {"enabled": True, "weekday_time": "17:30"}
        }
    }


def load_stats() -> dict:
    """Load stats from JSON file."""
    if STATS_FILE.exists():
        with open(STATS_FILE) as f:
            return json.load(f)
    return get_default_stats()


def get_default_stats() -> dict:
    """Return default stats structure."""
    return {
        "total_sessions": 0,
        "total_focus_minutes": 0,
        "today": {
            "date": str(date.today()),
            "sessions": 0,
            "focus_minutes": 0,
            "essential_task": None,
            "energy_readings": [],
            "circadian": {},
            "habit_anchor": None,
            "first_session_time": None,
            "identity_statement": None,
            "shutdown_complete": False
        },
        "weekly_reviews": [],
        "weekly_plans": [],
        "identity_progression": [],
        "implementation_intentions": {}
    }


def save_stats(stats: dict):
    """Save stats to JSON file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)


def load_sessions() -> list:
    """Load session history."""
    if SESSIONS_FILE.exists():
        with open(SESSIONS_FILE) as f:
            return json.load(f)
    return []


def save_sessions(sessions: list):
    """Save session history."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(SESSIONS_FILE, "w") as f:
        json.dump(sessions, f, indent=2)


def ensure_today_stats(stats: dict) -> dict:
    """Ensure today's stats are initialized."""
    if stats.get("today", {}).get("date") != str(date.today()):
        yesterday = stats.get("today", {})
        stats["today"] = get_default_stats()["today"]
        stats["today"]["essential_task"] = yesterday.get("tomorrow_priority")
    return stats


def notify(title: str, message: str, sound: bool = True):
    """Send macOS notification."""
    config = load_config()
    if not config.get("notifications", {}).get("enabled", True):
        return
    sound_part = f'sound name "{config["notifications"].get("sound", "Glass")}"' if sound else ""
    script = f'display notification "{message}" with title "{title}" {sound_part}'
    subprocess.run(["osascript", "-e", script], capture_output=True)


def say(message: str):
    """Speak a message using macOS say command."""
    config = load_config()
    if config.get("notifications", {}).get("voice", True):
        subprocess.run(["say", message], capture_output=True)


def format_duration(minutes: int) -> str:
    """Format minutes as Xh Ym."""
    if minutes >= 60:
        return f"{minutes // 60}h {minutes % 60}m"
    return f"{minutes}m"


def get_todays_theme(config: dict) -> dict:
    """Get today's theme from config."""
    day = datetime.now().strftime("%A")
    themes = config.get("behavioral", {}).get("daily_themes", {}).get("themes", {})
    return themes.get(day, {"name": "Focus Day", "description": "Deep work"})


def get_week_sessions(sessions: list) -> list:
    """Get sessions from current week."""
    week_start = date.today() - timedelta(days=date.today().weekday())
    return [s for s in sessions if s.get("timestamp", "")[:10] >= str(week_start)]


# =============================================================================
# Environment Automation
# =============================================================================

def enable_macos_focus_mode(config: dict):
    """Enable macOS Focus/DND mode."""
    if not config.get("environment", {}).get("macos_focus_mode", {}).get("enabled"):
        return

    # Try to run Shortcuts if available
    try:
        result = subprocess.run(
            ["shortcuts", "run", "Enable Deep Work Focus"],
            capture_output=True, timeout=5
        )
        if result.returncode == 0:
            console.print("[dim]macOS Focus Mode enabled[/dim]")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        # Shortcuts not available, try direct AppleScript for DND
        pass


def disable_macos_focus_mode(config: dict):
    """Disable macOS Focus mode."""
    if not config.get("environment", {}).get("macos_focus_mode", {}).get("enabled"):
        return

    try:
        subprocess.run(
            ["shortcuts", "run", "Disable Deep Work Focus"],
            capture_output=True, timeout=5
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass


def quit_distraction_apps(config: dict):
    """Quit distracting apps when focus starts."""
    apps = config.get("environment", {}).get("blocking", {}).get("apps", {}).get("quit_on_start", [])
    for app in apps:
        subprocess.run(
            ["osascript", "-e", f'tell application "{app}" to quit'],
            capture_output=True
        )
    if apps:
        console.print(f"[dim]Closed: {', '.join(apps)}[/dim]")


# =============================================================================
# Session UI
# =============================================================================

def display_session_ui(task: str, duration_minutes: int, goal: str, intention: str, commitment: str):
    """Display the focus session UI with progress bar."""
    total_seconds = duration_minutes * 60
    start_time = time.time()
    distractions = 0
    paused = False
    pause_time = 0

    console.clear()

    try:
        with Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=40),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("•"),
            TimeRemainingColumn(),
            console=console,
            refresh_per_second=1
        ) as progress:

            task_id = progress.add_task(f"[cyan]Deep Work: {task}", total=total_seconds)

            while not progress.finished:
                if paused:
                    console.print("\n[yellow]PAUSED[/yellow] - Press Enter to resume, 's' to stop")
                    try:
                        import select
                        if select.select([sys.stdin], [], [], 0.5)[0]:
                            key = sys.stdin.read(1)
                            if key == 's':
                                if handle_stop_request(commitment, intention):
                                    return {"completed": False, "distractions": distractions, "reason": "stopped"}
                            paused = False
                            pause_time += time.time() - pause_start
                    except:
                        time.sleep(0.5)
                    continue

                elapsed = time.time() - start_time - pause_time
                remaining = total_seconds - elapsed

                if remaining <= 0:
                    break

                progress.update(task_id, completed=elapsed)

                # Check for keyboard input (non-blocking)
                try:
                    import select
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        key = sys.stdin.read(1)
                        if key == 'p':
                            paused = True
                            pause_start = time.time()
                        elif key == 's':
                            if handle_stop_request(commitment, intention):
                                return {"completed": False, "distractions": distractions, "reason": "stopped", "minutes": int(elapsed / 60)}
                        elif key == 'd':
                            distractions += 1
                            console.print(f"\n[yellow]Distraction logged ({distractions}). Remember: {intention}[/yellow]")
                            time.sleep(2)
                except:
                    time.sleep(0.1)

                time.sleep(0.9)

        return {"completed": True, "distractions": distractions, "minutes": duration_minutes}

    except KeyboardInterrupt:
        return {"completed": False, "distractions": distractions, "reason": "interrupted", "minutes": int((time.time() - start_time) / 60)}


def handle_stop_request(commitment: str, intention: str) -> bool:
    """Handle stop request based on commitment level. Returns True if should stop."""
    if commitment == "soft":
        return True

    elif commitment == "standard":
        console.print("\n[yellow]COMMITMENT CHECK[/yellow]")
        console.print("[dim]You committed to this session.[/dim]")
        reason = Prompt.ask("[cyan]Why are you stopping? (minimum 20 characters)[/cyan]", default="")
        if len(reason) < 20:
            console.print("[red]Please provide a meaningful reason (20+ characters).[/red]")
            return False
        console.print(f"[dim]Logged: {reason}[/dim]")
        return True

    elif commitment == "deep":
        console.print("\n[red]DEEP COMMITMENT MODE[/red]")
        console.print("[dim]You requested maximum commitment.[/dim]")
        phrase = "I choose to break my commitment"
        typed = Prompt.ask(f"[cyan]Type exactly: '{phrase}'[/cyan]", default="")
        if typed != phrase:
            console.print("[green]Phrase didn't match. Returning to session.[/green]")
            console.print(f"[dim]Remember: {intention}[/dim]")
            return False
        return True

    return True


# =============================================================================
# CLI Commands
# =============================================================================

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Focus Mode v3: Executive-Level Deep Work System"""
    if ctx.invoked_subcommand is None:
        if ACTIVE_SESSION_FILE.exists():
            ctx.invoke(status)
        else:
            ctx.invoke(start)


# -----------------------------------------------------------------------------
# Core Session Commands
# -----------------------------------------------------------------------------

@cli.command()
@click.argument("duration", type=int, default=0)
@click.argument("task", type=str, default="")
@click.option('--commitment', '-c', type=click.Choice(['soft', 'standard', 'deep']), default=None,
              help="Commitment level: soft/standard/deep")
@click.option('--no-env', is_flag=True, help="Skip environment automation")
def start(duration: int, task: str, commitment: str, no_env: bool):
    """Start a focus session."""
    config = load_config()
    stats = load_stats()
    stats = ensure_today_stats(stats)

    # Set commitment level
    if commitment is None:
        commitment = config.get("behavioral", {}).get("commitment", {}).get("default_level", "standard")

    session_num = stats["today"]["sessions"] + 1

    # Show today's theme
    theme = get_todays_theme(config)
    console.print(Panel.fit(
        f"[bold cyan]DEEP WORK SESSION[/bold cyan]\n"
        f"[dim]Today's theme: {theme['name']}[/dim]",
        border_style="cyan"
    ))

    # Pre-focus priming prompt
    if config.get("neuroscience", {}).get("pre_focus_priming", {}).get("auto_prompt"):
        if Confirm.ask("\n[cyan]Run pre-focus priming? (60 sec visual focus)[/cyan]", default=False):
            do_visual_focus(60)

    # Flexible duration - ask if not provided
    if duration == 0:
        console.print("\n[bold]How long will you focus?[/bold]")
        console.print("  [dim]90 min - Deep work (recommended)[/dim]")
        console.print("  [dim]60 min - Standard block[/dim]")
        console.print("  [dim]30 min - Lighter tasks[/dim]")
        duration = IntPrompt.ask("\n[cyan]Duration (minutes)[/cyan]", default=90)

    # Get task if not provided
    if not task:
        task = Prompt.ask("[cyan]What are you working on?[/cyan]", default="Deep work")

    console.print(f"\n[bold]Task:[/bold] {task}")
    console.print(f"[bold]Duration:[/bold] {duration} minutes")
    console.print(f"[bold]Session:[/bold] #{session_num} today")
    console.print(f"[bold]Commitment:[/bold] {commitment}")

    # Essentialism check
    console.print()
    is_essential = Confirm.ask("[cyan]Is this essential to your goals?[/cyan]", default=True)
    if not is_essential:
        console.print("[yellow]Consider: Is this the right thing to be working on?[/yellow]")
        if not Confirm.ask("[cyan]Continue anyway?[/cyan]", default=True):
            console.print("[dim]Session cancelled. Focus on what's essential.[/dim]")
            return

    # Goal clarification (Flow trigger)
    goal = Prompt.ask("[cyan]What specific outcome marks this session complete?[/cyan]")

    # Implementation intention
    distraction = Prompt.ask("[cyan]What might distract you?[/cyan]", default="notifications")
    response = Prompt.ask(f"[cyan]When you want to check {distraction}, you will:[/cyan]", default="note it and continue")
    intention = f"When I want to check {distraction}, I will {response}"

    # Save implementation intention for future reference
    if "implementation_intentions" not in stats:
        stats["implementation_intentions"] = {}
    stats["implementation_intentions"][distraction] = response

    console.print()
    console.print(Panel.fit(
        f"[bold green]SESSION ACTIVE[/bold green]\n\n"
        f"[dim]Goal: {goal}[/dim]\n"
        f"[dim]Intention: {intention}[/dim]\n\n"
        f"[dim][p] pause  [s] stop  [d] log distraction[/dim]",
        border_style="green"
    ))

    # Enable environment automation
    if not no_env:
        enable_macos_focus_mode(config)
        quit_distraction_apps(config)

    # Store active session
    active_session = {
        "start_time": datetime.now().isoformat(),
        "task": task,
        "duration": duration,
        "goal": goal,
        "intention": intention,
        "is_essential": is_essential,
        "commitment": commitment
    }
    with open(ACTIVE_SESSION_FILE, "w") as f:
        json.dump(active_session, f)

    notify("Focus Mode", f"Starting {duration}-minute deep work session")

    result = display_session_ui(task, duration, goal, intention, commitment)

    # Remove active session file
    if ACTIVE_SESSION_FILE.exists():
        ACTIVE_SESSION_FILE.unlink()

    # Disable environment automation
    if not no_env:
        disable_macos_focus_mode(config)

    console.clear()

    if result["completed"]:
        notify("Focus Mode", "Session complete! Great work!", sound=True)
        say("Deep work session complete.")

        console.print(Panel.fit(
            f"[bold green]SESSION COMPLETE - {duration} minutes[/bold green]",
            border_style="green"
        ))

        # Quick reflection
        console.print()
        goal_achieved = Prompt.ask(
            "[cyan]Did you achieve your goal?[/cyan]",
            choices=["y", "n", "partial"],
            default="y"
        )

        resume_note = Prompt.ask("[cyan]Note for next session[/cyan]", default="")

        # Save session data
        session_data = {
            "task": task,
            "goal": goal,
            "goal_achieved": goal_achieved,
            "distractions": result.get("distractions", 0),
            "duration": duration,
            "is_essential": is_essential,
            "commitment": commitment,
            "resume_note": resume_note,
            "timestamp": datetime.now().isoformat()
        }

        # Update stats
        stats["total_sessions"] += 1
        stats["total_focus_minutes"] += duration
        stats["today"]["sessions"] += 1
        stats["today"]["focus_minutes"] += duration

        # Save
        sessions = load_sessions()
        sessions.append(session_data)
        save_sessions(sessions)
        save_stats(stats)

        # Show stats
        console.print()
        console.print(f"[bold]Today:[/bold] {stats['today']['sessions']} sessions | {format_duration(stats['today']['focus_minutes'])}")

        week_sessions = get_week_sessions(sessions)
        week_minutes = sum(s.get("duration", 0) for s in week_sessions)
        console.print(f"[bold]This week:[/bold] {len(week_sessions)} sessions | {format_duration(week_minutes)}")

        # Ultradian rest enforcement for 90+ min sessions
        if duration >= 80 and config.get("neuroscience", {}).get("ultradian", {}).get("enforce_rest_after_90"):
            console.print()
            console.print(Panel.fit(
                "[bold cyan]ULTRADIAN REST REQUIRED[/bold cyan]\n\n"
                "You completed a full focus cycle.\n"
                "Your brain needs 20+ minutes of TRUE rest:\n\n"
                "  [green]GOOD:[/green] Walk outside, stretch, NSDR\n"
                "  [yellow]AVOID:[/yellow] Email, social media, screens\n\n"
                "[dim]This is not optional - it's how your brain works.[/dim]",
                border_style="cyan"
            ))
            if Confirm.ask("\n[cyan]Start NSDR protocol? (10-20 min)[/cyan]", default=True):
                do_nsdr_timer(10)
            else:
                do_break(20)
        else:
            # Standard break
            sessions_today = stats["today"]["sessions"]
            if sessions_today % 4 == 0:
                break_time = config.get("session", {}).get("long_break", 15)
                console.print(f"\n[cyan]Take a {break_time}-minute break. You've earned it.[/cyan]")
            else:
                break_time = config.get("session", {}).get("short_break", 5)
                console.print(f"\n[cyan]Take a {break_time}-minute break. Stand, stretch, hydrate.[/cyan]")

            if Confirm.ask("[cyan]Start break timer?[/cyan]", default=True):
                do_break(break_time)

    else:
        elapsed = result.get("minutes", 0)
        console.print(Panel.fit(
            f"[yellow]Session ended early ({elapsed} min)[/yellow]",
            border_style="yellow"
        ))

        session_data = {
            "task": task,
            "goal": goal,
            "completed": False,
            "minutes_completed": elapsed,
            "reason": result.get("reason", "stopped"),
            "timestamp": datetime.now().isoformat()
        }

        sessions = load_sessions()
        sessions.append(session_data)
        save_sessions(sessions)
        save_stats(stats)


# -----------------------------------------------------------------------------
# Neuroscience Commands
# -----------------------------------------------------------------------------

@cli.command()
@click.option('--quick', '-q', is_flag=True, help='Quick 60-second visual focus only')
def prime(quick: bool):
    """Pre-focus priming protocol to engage attention circuits."""
    config = load_config()
    duration = config.get("neuroscience", {}).get("pre_focus_priming", {}).get("visual_focus_duration", 60)

    console.print(Panel.fit(
        "[bold cyan]PRE-FOCUS PRIMING[/bold cyan]\n"
        "[dim]Engage your attention circuits before deep work[/dim]",
        border_style="cyan"
    ))

    if not quick:
        # Box breathing first
        console.print("\n[bold]Step 1: Box Breathing (2 minutes)[/bold]")
        console.print("[dim]4 counts in → 4 counts hold → 4 counts out → 4 counts hold[/dim]")
        if Confirm.ask("[cyan]Start box breathing?[/cyan]", default=True):
            do_box_breathing(2)

    # Visual focus
    console.print("\n[bold]Step 2: Visual Focus Exercise[/bold]")
    console.print("[dim]Stare at a point 2-4 feet away. This engages your prefrontal cortex.[/dim]")
    console.print()
    input("[cyan]Press ENTER when you've found your focus point...[/cyan]")

    do_visual_focus(duration)

    console.print()
    console.print(Panel.fit(
        "[bold green]PRIMING COMPLETE[/bold green]\n\n"
        "Your attention circuits are engaged.\n"
        "[dim]Type 'focus' to start your session[/dim]",
        border_style="green"
    ))


def do_visual_focus(seconds: int):
    """Run visual focus timer."""
    console.print(f"\n[cyan]Hold visual focus for {seconds} seconds...[/cyan]")
    with Progress(
        TextColumn("[cyan]Visual Focus"),
        BarColumn(bar_width=30),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        task = progress.add_task("", total=seconds)
        for _ in range(seconds):
            time.sleep(1)
            progress.advance(task)
    console.print("[green]Visual focus complete.[/green]")


def do_box_breathing(minutes: int):
    """Guide through box breathing."""
    cycles = minutes * 3  # ~3 cycles per minute
    console.print()
    for i in range(cycles):
        console.print(f"[cyan]Breathe IN... 1... 2... 3... 4...[/cyan]")
        time.sleep(4)
        console.print(f"[yellow]HOLD... 1... 2... 3... 4...[/yellow]")
        time.sleep(4)
        console.print(f"[cyan]Breathe OUT... 1... 2... 3... 4...[/cyan]")
        time.sleep(4)
        console.print(f"[yellow]HOLD... 1... 2... 3... 4...[/yellow]")
        time.sleep(4)
        console.print(f"[dim]Cycle {i+1}/{cycles}[/dim]\n")
    console.print("[green]Box breathing complete.[/green]")


@cli.command()
@click.argument("level", type=int, default=0)
def energy(level: int):
    """Log current energy/alertness level (1-5)."""
    stats = load_stats()
    stats = ensure_today_stats(stats)

    if level == 0:
        console.print(Panel.fit(
            "[bold cyan]ENERGY CHECK[/bold cyan]\n"
            "[dim]Track your alertness throughout the day[/dim]",
            border_style="cyan"
        ))
        console.print("\n[bold]Energy/Alertness Scale:[/bold]")
        console.print("  1 - Foggy, struggling to focus")
        console.print("  2 - Below baseline, need stimulus")
        console.print("  3 - Normal, adequate for routine work")
        console.print("  4 - Good, ready for demanding tasks")
        console.print("  5 - Peak, ideal for hardest challenges")
        level = IntPrompt.ask("\n[cyan]Current level?[/cyan]", default=3)

    factors = Prompt.ask(
        "[cyan]What's affecting your energy? (caffeine, exercise, sleep, meal, etc.)[/cyan]",
        default=""
    )

    reading = {
        "time": datetime.now().strftime("%H:%M"),
        "level": level,
        "factors": factors
    }

    if "energy_readings" not in stats["today"]:
        stats["today"]["energy_readings"] = []
    stats["today"]["energy_readings"].append(reading)
    save_stats(stats)

    # Show today's curve
    readings = stats["today"]["energy_readings"]
    if len(readings) > 1:
        console.print("\n[bold]Today's energy curve:[/bold]")
        for r in readings:
            bar = "█" * r["level"] + "░" * (5 - r["level"])
            console.print(f"  {r['time']} [{bar}] {r['level']}")

    # Suggestion based on level
    if level <= 2:
        console.print("\n[yellow]Low energy detected. Consider:[/yellow]")
        console.print("  - 10-20 min NSDR (type 'focus nsdr')")
        console.print("  - Cold water on face")
        console.print("  - Quick walk outside")
    elif level >= 4:
        console.print("\n[green]High energy - great time for your hardest task![/green]")


@cli.command()
@click.argument("duration", type=int, default=10)
def nsdr(duration: int):
    """Non-Sleep Deep Rest protocol for recovery."""
    console.print(Panel.fit(
        f"[bold cyan]NSDR PROTOCOL - {duration} minutes[/bold cyan]\n\n"
        "Non-Sleep Deep Rest compensates for sleep debt\n"
        "and accelerates learning consolidation.\n\n"
        "[bold]Instructions:[/bold]\n"
        "1. Lie down or recline comfortably\n"
        "2. Close your eyes\n"
        "3. Follow body scan or use guided NSDR\n\n"
        "[dim]Recommended: Search 'Huberman NSDR' on YouTube[/dim]",
        border_style="cyan"
    ))

    if Confirm.ask("\n[cyan]Open Huberman NSDR video?[/cyan]", default=False):
        subprocess.run(["open", "https://www.youtube.com/watch?v=AKGrmY8OSHM"], capture_output=True)

    do_nsdr_timer(duration)


def do_nsdr_timer(duration: int):
    """Run NSDR rest timer."""
    console.print(f"\n[dim]Starting {duration}-minute NSDR timer...[/dim]")
    notify("Focus Mode", f"NSDR: Rest for {duration} minutes")

    total_seconds = duration * 60
    with Progress(
        TextColumn("[cyan]NSDR Rest"),
        BarColumn(bar_width=30),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        task = progress.add_task("", total=total_seconds)
        for _ in range(total_seconds):
            time.sleep(1)
            progress.advance(task)

    notify("Focus Mode", "NSDR complete. You should feel refreshed.")
    say("N S D R complete. You should feel refreshed.")
    console.print("\n[green]NSDR complete. Ready to focus again.[/green]")


# -----------------------------------------------------------------------------
# Behavioral Commands
# -----------------------------------------------------------------------------

@cli.command()
def plan():
    """Weekly planning ritual - set the week's architecture."""
    config = load_config()
    stats = load_stats()
    sessions = load_sessions()

    console.print(Panel.fit(
        "[bold cyan]WEEKLY PLANNING[/bold cyan]\n"
        "[dim]Set your week's architecture[/dim]",
        border_style="cyan"
    ))

    # Review last week
    week_start = date.today() - timedelta(days=date.today().weekday())
    last_week_start = week_start - timedelta(days=7)
    last_week_sessions = [s for s in sessions
                         if str(last_week_start) <= s.get("timestamp", "")[:10] < str(week_start)]

    if last_week_sessions:
        minutes = sum(s.get("duration", s.get("minutes_completed", 0)) for s in last_week_sessions)
        console.print(f"\n[bold]Last week:[/bold] {len(last_week_sessions)} sessions | {format_duration(minutes)}")

    # Check for last week's review insights
    reviews = stats.get("weekly_reviews", [])
    if reviews:
        last_review = reviews[-1]
        if last_review.get("produced_results"):
            console.print(f"\n[dim]Last week's insight: '{last_review.get('produced_results')}'[/dim]")

    # Big rocks for the week
    console.print("\n" + "━" * 50)
    console.print("[bold]BIG ROCKS THIS WEEK[/bold]")
    console.print("[dim]What 3-5 things MUST happen this week?[/dim]")
    console.print("━" * 50)

    big_rocks = []
    for i in range(5):
        rock = Prompt.ask(f"\n[cyan]{i+1}>[/cyan]", default="")
        if not rock or rock.lower() == "done":
            break
        big_rocks.append({"name": rock, "assigned_day": None})

    if not big_rocks:
        console.print("[yellow]No rocks added. Consider what's truly essential.[/yellow]")
        return

    # Assign to days
    console.print("\n[bold]ASSIGN TO DAYS[/bold]")
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    for rock in big_rocks:
        day = Prompt.ask(f"[cyan]{rock['name']} -> Which day?[/cyan]", default="Monday")
        rock["assigned_day"] = day

    # Shutdown time
    console.print()
    shutdown_time = Prompt.ask(
        "[cyan]When does work END each weekday?[/cyan]",
        default=config.get("behavioral", {}).get("shutdown", {}).get("weekday_time", "17:30")
    )

    # Save weekly plan
    plan_data = {
        "week_of": str(week_start),
        "big_rocks": big_rocks,
        "shutdown_time": shutdown_time,
        "created": str(date.today())
    }

    if "weekly_plans" not in stats:
        stats["weekly_plans"] = []
    stats["weekly_plans"].append(plan_data)
    save_stats(stats)

    # Summary
    console.print()
    console.print(Panel.fit(
        f"[bold green]WEEK PLANNED[/bold green]\n\n"
        f"Big rocks: {len(big_rocks)}\n"
        f"Shutdown: {shutdown_time}\n\n"
        "[dim]Type 'gm' each morning to see your plan[/dim]",
        border_style="green"
    ))


@cli.command()
def drift():
    """Quick inter-session check-in."""
    stats = load_stats()
    sessions = load_sessions()

    today_sessions = [s for s in sessions if s.get("timestamp", "")[:10] == str(date.today())]

    if not today_sessions:
        console.print("[dim]No sessions today yet. Start with 'focus'[/dim]")
        return

    last_session = today_sessions[-1]
    last_end = datetime.fromisoformat(last_session.get("timestamp"))
    gap_minutes = int((datetime.now() - last_end).total_seconds() / 60)

    console.print(Panel.fit(
        f"[bold cyan]DRIFT CHECK[/bold cyan]\n\n"
        f"Last session ended: {last_end.strftime('%H:%M')}\n"
        f"Time now: {datetime.now().strftime('%H:%M')}\n"
        f"Gap: {gap_minutes} minutes",
        border_style="cyan"
    ))

    console.print("\n[bold]What did you do in this gap?[/bold]")
    console.print("  1 - Intentional break (rest, walk, etc.)")
    console.print("  2 - Necessary shallow work (emails, admin)")
    console.print("  3 - Drift (social media, browsing, etc.)")

    activity = Prompt.ask("[cyan]Choice[/cyan]", choices=["1", "2", "3"], default="1")

    if activity == "3":
        console.print("\n[dim]No judgment. Awareness is the first step.[/dim]")
        drift_cause = Prompt.ask("[cyan]What pulled you away?[/cyan]", default="")

        # Create new implementation intention
        new_intention = Prompt.ask(
            f"[cyan]When you feel the urge to check {drift_cause}, you will...[/cyan]",
            default="take 3 breaths and return to work"
        )

        # Save to stats
        if "implementation_intentions" not in stats:
            stats["implementation_intentions"] = {}
        stats["implementation_intentions"][drift_cause] = new_intention
        save_stats(stats)

        console.print(f"\n[green]New intention saved: When {drift_cause} → {new_intention}[/green]")

    if Confirm.ask("\n[cyan]Ready to start next session?[/cyan]", default=True):
        import os
        os.system("python3 ~/.warp/focus/focus.py start")


@cli.command()
def shutdown():
    """End-of-day shutdown ritual - complete cognitive closure."""
    config = load_config()
    stats = load_stats()
    stats = ensure_today_stats(stats)

    planned_shutdown = config.get("behavioral", {}).get("shutdown", {}).get("weekday_time", "17:30")
    current_time = datetime.now().strftime("%H:%M")

    # Status check
    if current_time < planned_shutdown:
        status = f"[green]EARLY ({planned_shutdown} planned)[/green]"
    elif current_time == planned_shutdown:
        status = "[green]ON TIME[/green]"
    else:
        status = f"[yellow]LATE ({planned_shutdown} planned)[/yellow]"

    console.print(Panel.fit(
        f"[bold cyan]SHUTDOWN RITUAL[/bold cyan]\n\n"
        f"Current time: {current_time}\n"
        f"Planned shutdown: {planned_shutdown}\n"
        f"Status: {status}",
        border_style="cyan"
    ))

    # Today's stats
    today = stats.get("today", {})
    console.print(f"\n[bold]Today:[/bold] {today.get('sessions', 0)} sessions | {format_duration(today.get('focus_minutes', 0))}")

    # Step 1: Capture open loops
    console.print("\n[bold]Step 1: CAPTURE OPEN LOOPS[/bold]")
    console.print("[dim]Get everything out of your head[/dim]")

    open_loops = Prompt.ask("[cyan]Any tasks nagging at you? (quick brain dump)[/cyan]", default="")
    if open_loops:
        stats["today"]["open_loops"] = open_loops
        console.print("[green]Captured for tomorrow.[/green]")

    # Step 2: Tomorrow's setup
    console.print("\n[bold]Step 2: TOMORROW'S PRIORITY[/bold]")
    tomorrow = Prompt.ask("[cyan]Tomorrow's ONE essential task?[/cyan]", default="")
    stats["today"]["tomorrow_priority"] = tomorrow

    # Step 3: Verbal commitment
    console.print("\n[bold]Step 3: SHUTDOWN COMPLETE[/bold]")
    console.print("[dim]Say out loud: 'Shutdown complete'[/dim]")
    console.print("[dim]This signals your brain to disengage from work.[/dim]")

    input("\n[cyan]Press ENTER after saying 'Shutdown complete' out loud...[/cyan]")

    # Mark shutdown complete
    stats["today"]["shutdown_complete"] = True
    stats["today"]["shutdown_time"] = current_time
    save_stats(stats)

    say("Shutdown complete. Work is done for today.")

    console.print()
    console.print(Panel.fit(
        f"[bold green]SHUTDOWN COMPLETE[/bold green]\n\n"
        f"Sessions today: {today.get('sessions', 0)}\n"
        f"Focus time: {format_duration(today.get('focus_minutes', 0))}\n\n"
        f"[dim]Tomorrow's focus: {tomorrow}[/dim]\n"
        f"[dim]Rest well.[/dim]",
        border_style="green"
    ))


@cli.command()
def journal():
    """Weekly identity reflection - who are you becoming?"""
    stats = load_stats()
    sessions = load_sessions()

    week_start = date.today() - timedelta(days=date.today().weekday())
    week_sessions = get_week_sessions(sessions)

    total_sessions = len(week_sessions)
    total_minutes = sum(s.get("duration", s.get("minutes_completed", 0)) for s in week_sessions)
    completed = len([s for s in week_sessions if s.get("goal_achieved") or s.get("completed", True)])
    completion_rate = int(completed / total_sessions * 100) if total_sessions > 0 else 0

    console.print(Panel.fit(
        f"[bold cyan]IDENTITY JOURNAL[/bold cyan]\n"
        f"Week of: {week_start}",
        border_style="cyan"
    ))

    # Show metrics
    console.print(f"\n[bold]This week's data:[/bold]")
    console.print(f"  - Deep work sessions: {total_sessions}")
    console.print(f"  - Focus time: {format_duration(total_minutes)}")
    console.print(f"  - Commitments kept: {completed}/{total_sessions} ({completion_rate}%)")

    # Identity questions
    console.print("\n" + "━" * 50)
    console.print("[bold]IDENTITY REFLECTION[/bold]")
    console.print("━" * 50)

    q1 = Prompt.ask("\n[cyan]1. What type of person shows up with these numbers?[/cyan]", default="")
    q2 = Prompt.ask("[cyan]2. What could you do this week that you couldn't before?[/cyan]", default="")
    q3 = Prompt.ask("[cyan]3. 'I am someone who...' (identity statement for next week)[/cyan]", default="")
    q4 = Prompt.ask("[cyan]4. One habit to reinforce this identity:[/cyan]", default="")

    # Save
    journal_data = {
        "week": str(week_start),
        "metrics": {
            "sessions": total_sessions,
            "focus_minutes": total_minutes,
            "completion_rate": completion_rate
        },
        "reflection": {
            "person_type": q1,
            "growth_evidence": q2,
            "identity_statement": q3,
            "reinforcing_habit": q4
        },
        "date": str(date.today())
    }

    if "identity_progression" not in stats:
        stats["identity_progression"] = []
    stats["identity_progression"].append(journal_data)
    save_stats(stats)

    # Save to file
    reflection_dir = DATA_DIR / "reflections"
    reflection_dir.mkdir(exist_ok=True)

    journal_file = reflection_dir / f"identity-{date.today()}.md"
    with open(journal_file, "w") as f:
        f.write(f"# Identity Journal: Week of {week_start}\n\n")
        f.write(f"## Metrics\n")
        f.write(f"- Sessions: {total_sessions}\n")
        f.write(f"- Focus time: {format_duration(total_minutes)}\n")
        f.write(f"- Commitment rate: {completion_rate}%\n\n")
        f.write(f"## Reflection\n\n")
        f.write(f"**Type of person:** {q1}\n\n")
        f.write(f"**Growth evidence:** {q2}\n\n")
        f.write(f"**Identity statement:** I am someone who {q3}\n\n")
        f.write(f"**Reinforcing habit:** {q4}\n")

    console.print()
    console.print(Panel.fit(
        f"[bold green]Journal saved![/bold green]\n\n"
        f"[dim]Next week's identity: {q3}[/dim]",
        border_style="green"
    ))


@cli.command()
def insights():
    """Behavioral insights from your data."""
    stats = load_stats()
    sessions = load_sessions()

    console.print(Panel.fit(
        "[bold cyan]BEHAVIORAL INSIGHTS[/bold cyan]\n"
        "[dim]Patterns from your data[/dim]",
        border_style="cyan"
    ))

    # Last 4 weeks
    four_weeks_ago = date.today() - timedelta(weeks=4)
    recent_sessions = [s for s in sessions if s.get("timestamp", "")[:10] >= str(four_weeks_ago)]

    if not recent_sessions:
        console.print("\n[dim]Not enough data yet. Keep tracking![/dim]")
        return

    # Weekly completion trend
    console.print("\n[bold]WEEKLY COMMITMENT RATE[/bold]")
    for week_num in range(4):
        week_start = date.today() - timedelta(weeks=4-week_num, days=date.today().weekday())
        week_end = week_start + timedelta(days=7)
        week_sessions = [s for s in recent_sessions
                        if str(week_start) <= s.get("timestamp", "")[:10] < str(week_end)]
        if week_sessions:
            completed = len([s for s in week_sessions if s.get("goal_achieved") or s.get("completed", True)])
            rate = int(completed / len(week_sessions) * 100)
            bar = "█" * (rate // 10) + "░" * (10 - rate // 10)
            console.print(f"  Week {week_num+1}: [{bar}] {rate}%")

    # Peak hours
    console.print("\n[bold]PEAK FOCUS HOURS[/bold]")
    hour_minutes = {}
    for s in recent_sessions:
        if "T" in s.get("timestamp", ""):
            hour = int(s["timestamp"].split("T")[1][:2])
            duration = s.get("duration", s.get("minutes_completed", 0))
            hour_minutes[hour] = hour_minutes.get(hour, 0) + duration

    if hour_minutes:
        sorted_hours = sorted(hour_minutes.items(), key=lambda x: x[1], reverse=True)
        best_hours = sorted_hours[:3]
        console.print(f"  Your best hours: {', '.join(f'{h}:00-{h+1}:00' for h, _ in best_hours)}")

    # Energy patterns
    if stats.get("today", {}).get("energy_readings"):
        console.print("\n[bold]ENERGY PATTERNS[/bold]")
        readings = stats["today"]["energy_readings"]
        avg_energy = sum(r["level"] for r in readings) / len(readings)
        console.print(f"  Today's average: {avg_energy:.1f}/5")

    # Identity progression
    if stats.get("identity_progression"):
        console.print("\n[bold]IDENTITY TREND[/bold]")
        latest = stats["identity_progression"][-1]
        statement = latest.get("reflection", {}).get("identity_statement", "Not set")
        console.print(f"  Current identity: {statement}")


# -----------------------------------------------------------------------------
# Standard Commands (Enhanced)
# -----------------------------------------------------------------------------

@cli.command()
def gm():
    """Morning ritual - start your day with intention."""
    config = load_config()
    stats = load_stats()
    stats = ensure_today_stats(stats)

    theme = get_todays_theme(config)

    console.print(Panel.fit(
        f"[bold cyan]Good morning![/bold cyan]\n"
        f"[dim]{date.today().strftime('%A, %B %d, %Y')}[/dim]\n\n"
        f"[bold]Today's Theme:[/bold] {theme['name']}\n"
        f"[dim]{theme['description']}[/dim]",
        border_style="cyan"
    ))

    # Circadian optimization
    neuro_config = config.get("neuroscience", {}).get("circadian", {})

    if neuro_config.get("track_wake_time"):
        wake_time = Prompt.ask("\n[cyan]When did you wake up? (HH:MM)[/cyan]",
                              default=datetime.now().strftime("%H:%M"))
        stats["today"]["circadian"]["wake_time"] = wake_time

    if neuro_config.get("prompt_sunlight"):
        sunlight = Confirm.ask("[cyan]Have you gotten 2-10 min of morning sunlight?[/cyan]", default=False)
        stats["today"]["circadian"]["sunlight"] = sunlight
        if not sunlight:
            console.print("[yellow]Tip: Get outside within 30-60 min of waking.[/yellow]")
            console.print("[dim]Morning sunlight sets your cortisol rhythm for all-day focus.[/dim]")

    if neuro_config.get("track_caffeine"):
        caffeine = Confirm.ask("[cyan]Have you had caffeine yet?[/cyan]", default=False)
        stats["today"]["circadian"]["had_caffeine"] = caffeine
        if caffeine and stats["today"]["circadian"].get("wake_time"):
            console.print("[dim]Optimal: delay caffeine 90-120 min after waking.[/dim]")

    # Sleep quality
    sleep = IntPrompt.ask("\n[cyan]Last night's sleep quality? (1-5)[/cyan]", default=3)
    stats["today"]["sleep_quality"] = sleep
    if sleep <= 2:
        console.print("[yellow]Low sleep detected. Consider shorter sessions or NSDR breaks.[/yellow]")

    # Yesterday's summary
    sessions = load_sessions()
    yesterday_date = date.today() - timedelta(days=1)
    yesterday_sessions = [s for s in sessions if s.get("timestamp", "")[:10] == str(yesterday_date)]

    if yesterday_sessions:
        completed = len([s for s in yesterday_sessions if s.get("goal_achieved") or s.get("completed", True)])
        minutes = sum(s.get("duration", s.get("minutes_completed", 0)) for s in yesterday_sessions)
        console.print(f"\n[bold]Yesterday:[/bold] {completed} sessions | {format_duration(minutes)}")

    # Weekly plan check
    weekly_plans = stats.get("weekly_plans", [])
    todays_rocks = []
    if weekly_plans:
        latest_plan = weekly_plans[-1]
        day_name = datetime.now().strftime("%A")
        todays_rocks = [r for r in latest_plan.get("big_rocks", []) if r.get("assigned_day") == day_name]
        if todays_rocks:
            console.print(f"\n[bold]Today's big rock(s):[/bold]")
            for rock in todays_rocks:
                console.print(f"  - {rock['name']}")

    # Essentialism question
    console.print("\n" + "━" * 50)
    console.print("[bold]THE ONE THING[/bold]")
    console.print("[dim]What is the ONE thing that would make everything else easier?[/dim]")
    console.print("━" * 50)

    essential_task = stats["today"].get("essential_task", "")
    if essential_task:
        console.print(f"\n[dim]Yesterday you set: {essential_task}[/dim]")

    default_task = todays_rocks[0]["name"] if todays_rocks else essential_task or ""
    priority = Prompt.ask("\n[cyan]Today's essential task[/cyan]", default=default_task)
    stats["today"]["essential_task"] = priority

    # Habit stacking
    console.print("\n[bold]HABIT STACK[/bold]")
    console.print("[dim]Anchor your first session to something you already do[/dim]")
    existing_habit = Prompt.ask(
        "[cyan]After I [make coffee/arrive at desk/etc.], I will start my first session[/cyan]",
        default="make coffee"
    )
    stats["today"]["habit_anchor"] = existing_habit

    # Time commitment
    first_session = Prompt.ask("[cyan]What time will your first session start?[/cyan]", default="09:00")
    stats["today"]["first_session_time"] = first_session

    # Identity statement
    console.print("\n[bold]IDENTITY[/bold]")
    identity = Prompt.ask("[cyan]Today I am someone who...[/cyan]", default="does deep work")
    stats["today"]["identity_statement"] = identity

    # Energy check
    console.print()
    energy_level = IntPrompt.ask("[cyan]Energy level right now? (1-5)[/cyan]", default=4)
    stats["today"]["energy_readings"].append({
        "time": datetime.now().strftime("%H:%M"),
        "level": energy_level
    })

    save_stats(stats)

    # Summary
    console.print()
    console.print(Panel.fit(
        f"[bold green]Ready for deep work[/bold green]\n\n"
        f"Essential task: {priority}\n"
        f"First session: {first_session} (after {existing_habit})\n"
        f"Identity: I am someone who {identity}\n\n"
        f"[dim]Type 'focus' to begin • 'prime' for pre-focus priming[/dim]",
        border_style="green"
    ))


@cli.command()
def eod():
    """End of day review."""
    stats = load_stats()
    sessions = load_sessions()
    stats = ensure_today_stats(stats)

    today = stats.get("today", {})
    today_sessions = [s for s in sessions if s.get("timestamp", "")[:10] == str(date.today())]

    console.print(Panel.fit(
        f"[bold cyan]END OF DAY REVIEW[/bold cyan]\n"
        f"[dim]{date.today().strftime('%A, %B %d, %Y')}[/dim]",
        border_style="cyan"
    ))

    # Today's results
    completed = today.get("sessions", 0)
    focus_time = today.get("focus_minutes", 0)

    console.print(f"\n[bold]Sessions:[/bold] {completed}")
    console.print(f"[bold]Focus time:[/bold] {format_duration(focus_time)}")

    # Essential task check
    essential_task = today.get("essential_task", "")
    if essential_task:
        console.print(f"\n[bold]Essential task:[/bold] {essential_task}")
        achieved = Confirm.ask("[cyan]Did you make progress on this?[/cyan]", default=True)
        if achieved:
            console.print("[green]Excellent. That's what matters.[/green]")
        else:
            console.print("[yellow]Tomorrow is another opportunity.[/yellow]")

    # Show completed tasks
    if today_sessions:
        console.print("\n[bold]Completed:[/bold]")
        for s in today_sessions:
            if s.get("goal_achieved") or s.get("completed", True):
                console.print(f"  [green]✓[/green] {s.get('task', 'Unknown')}")

    # Reflection
    console.print()
    went_well = Prompt.ask("[cyan]What went well today?[/cyan]", default="")
    tomorrow = Prompt.ask("[cyan]What's tomorrow's priority?[/cyan]", default="")

    # Save reflection
    if went_well or tomorrow:
        reflection_dir = DATA_DIR / "reflections"
        reflection_dir.mkdir(exist_ok=True)

        reflection_file = reflection_dir / f"{date.today()}.md"
        with open(reflection_file, "w") as f:
            f.write(f"# {date.today().strftime('%A, %B %d, %Y')}\n\n")
            f.write(f"## Stats\n")
            f.write(f"- Sessions: {completed}\n")
            f.write(f"- Focus time: {format_duration(focus_time)}\n")
            if essential_task:
                f.write(f"- Essential task: {essential_task}\n")
            f.write(f"\n## Reflection\n")
            f.write(f"**What went well:** {went_well}\n\n")
            f.write(f"**Tomorrow's priority:** {tomorrow}\n")

    stats["today"]["tomorrow_priority"] = tomorrow
    save_stats(stats)

    # Prompt for shutdown if not done
    if not today.get("shutdown_complete"):
        console.print()
        if Confirm.ask("[cyan]Run shutdown ritual for complete cognitive closure?[/cyan]", default=True):
            import os
            os.system("python3 ~/.warp/focus/focus.py shutdown")
            return

    console.print()
    console.print(Panel.fit(
        "[bold green]Good work today.[/bold green]\n\n"
        f"[dim]Rest well. Tomorrow's focus: {tomorrow}[/dim]",
        border_style="green"
    ))


@cli.command()
def status():
    """Show current session status or quick stats."""
    stats = load_stats()
    config = load_config()

    if ACTIVE_SESSION_FILE.exists():
        with open(ACTIVE_SESSION_FILE) as f:
            session = json.load(f)
        console.print(Panel.fit(
            f"[bold yellow]SESSION IN PROGRESS[/bold yellow]\n\n"
            f"Task: {session.get('task', 'Unknown')}\n"
            f"Started: {session.get('start_time', 'Unknown')}\n"
            f"Goal: {session.get('goal', 'Not set')}",
            border_style="yellow"
        ))
        return

    stats = ensure_today_stats(stats)
    today = stats.get("today", {})
    sessions = load_sessions()
    theme = get_todays_theme(config)

    # Week stats
    week_sessions = get_week_sessions(sessions)
    week_minutes = sum(s.get("duration", s.get("minutes_completed", 0)) for s in week_sessions)

    console.print(Panel.fit(
        f"[bold]TODAY - {theme['name']}[/bold]\n"
        f"Sessions: {today.get('sessions', 0)} | Focus: {format_duration(today.get('focus_minutes', 0))}\n\n"
        f"[bold]THIS WEEK[/bold]\n"
        f"Sessions: {len(week_sessions)} | Focus: {format_duration(week_minutes)}\n\n"
        f"[dim]Commands: focus | gm | eod | prime | energy | shutdown[/dim]",
        title="Focus Mode v3",
        border_style="blue"
    ))


@cli.command()
@click.argument("period", type=str, default="today")
def stats(period: str):
    """Show statistics."""
    stats_data = load_stats()
    sessions = load_sessions()
    today = stats_data.get("today", {})

    if period == "today":
        console.print(Panel.fit(
            f"[bold cyan]TODAY[/bold cyan]\n"
            f"[dim]{date.today().strftime('%A, %B %d')}[/dim]",
            border_style="cyan"
        ))

        console.print(f"\nSessions: [bold]{today.get('sessions', 0)}[/bold]")
        console.print(f"Focus time: [bold]{format_duration(today.get('focus_minutes', 0))}[/bold]")

        today_sessions = [s for s in sessions if s.get("timestamp", "").startswith(str(date.today()))]
        if today_sessions:
            completed = len([s for s in today_sessions if s.get("goal_achieved") or s.get("completed", True)])
            console.print(f"Completion rate: [bold]{int(completed/len(today_sessions)*100)}%[/bold]")

            console.print("\n[bold]Sessions:[/bold]")
            for s in today_sessions:
                status_icon = "[green]✓[/green]" if s.get("goal_achieved") or s.get("completed", True) else "[yellow]○[/yellow]"
                time_str = s.get("timestamp", "")[:16].split("T")[1] if "T" in s.get("timestamp", "") else ""
                duration = s.get('duration', s.get('minutes_completed', 0))
                console.print(f"  {status_icon} {time_str} - {s.get('task', 'Unknown')} ({duration} min)")

        # Energy readings
        if today.get("energy_readings"):
            console.print("\n[bold]Energy curve:[/bold]")
            for r in today["energy_readings"]:
                bar = "█" * r["level"] + "░" * (5 - r["level"])
                console.print(f"  {r['time']} [{bar}] {r['level']}")

    elif period == "week":
        console.print(Panel.fit(
            "[bold cyan]THIS WEEK[/bold cyan]",
            border_style="cyan"
        ))

        week_start = date.today() - timedelta(days=date.today().weekday())
        week_sessions = [s for s in sessions if s.get("timestamp", "")[:10] >= str(week_start)]

        total_sessions = len(week_sessions)
        completed_sessions = len([s for s in week_sessions if s.get("goal_achieved") or s.get("completed", True)])
        total_minutes = sum(s.get("duration", s.get("minutes_completed", 0)) for s in week_sessions)
        avg_duration = total_minutes // total_sessions if total_sessions > 0 else 0

        console.print(f"\nSessions: [bold]{total_sessions}[/bold]")
        console.print(f"Focus time: [bold]{format_duration(total_minutes)}[/bold]")
        console.print(f"Avg session: [bold]{avg_duration} min[/bold]")
        console.print(f"Completion rate: [bold]{int(completed_sessions/total_sessions*100) if total_sessions > 0 else 0}%[/bold]")

        console.print("\n[bold]Daily breakdown:[/bold]")
        for i in range(7):
            day = week_start + timedelta(days=i)
            day_sessions = [s for s in week_sessions if s.get("timestamp", "")[:10] == str(day)]
            day_minutes = sum(s.get("duration", s.get("minutes_completed", 0)) for s in day_sessions)
            bar_len = min(20, day_minutes // 10)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            day_name = day.strftime("%a")
            marker = " <- Today" if day == date.today() else ""
            console.print(f"  {day_name} [{bar}] {format_duration(day_minutes)}{marker}")

        # Peak hours
        if week_sessions:
            console.print("\n[bold]Insights:[/bold]")
            hour_counts = {}
            for s in week_sessions:
                if "T" in s.get("timestamp", ""):
                    hour = int(s["timestamp"].split("T")[1][:2])
                    hour_counts[hour] = hour_counts.get(hour, 0) + 1

            if hour_counts:
                peak_hour = max(hour_counts, key=hour_counts.get)
                console.print(f"  Peak focus hour: {peak_hour}:00 - {peak_hour+1}:00")

    else:
        console.print(Panel.fit(
            "[bold cyan]ALL-TIME STATS[/bold cyan]",
            border_style="cyan"
        ))

        console.print(f"\nTotal sessions: [bold]{stats_data.get('total_sessions', 0)}[/bold]")
        console.print(f"Total focus time: [bold]{format_duration(stats_data.get('total_focus_minutes', 0))}[/bold]")


@cli.command()
def review():
    """Weekly Essentialism review - 80/20 analysis."""
    stats_data = load_stats()
    sessions = load_sessions()

    console.print(Panel.fit(
        "[bold cyan]WEEKLY ESSENTIALISM REVIEW[/bold cyan]\n"
        "[dim]Based on Greg McKeown's methodology[/dim]",
        border_style="cyan"
    ))

    week_start = date.today() - timedelta(days=date.today().weekday())
    week_sessions = [s for s in sessions if s.get("timestamp", "")[:10] >= str(week_start)]

    total_sessions = len(week_sessions)
    total_minutes = sum(s.get("duration", s.get("minutes_completed", 0)) for s in week_sessions)

    console.print(f"\n[bold]This week:[/bold] {total_sessions} sessions | {format_duration(total_minutes)}")

    if week_sessions:
        tasks = {}
        for s in week_sessions:
            task = s.get("task", "Unknown")
            tasks[task] = tasks.get(task, 0) + s.get("duration", 0)

        console.print("\n[bold]Time spent:[/bold]")
        for task, minutes in sorted(tasks.items(), key=lambda x: x[1], reverse=True)[:5]:
            console.print(f"  - {task}: {format_duration(minutes)}")

    console.print("\n" + "━" * 50)
    console.print("[bold]THE 80/20 QUESTIONS[/bold]")
    console.print("━" * 50)

    q1 = Prompt.ask("\n[cyan]Which 20% of your work produced 80% of meaningful results?[/cyan]", default="")
    q2 = Prompt.ask("\n[cyan]What should you STOP doing?[/cyan]", default="")
    q3 = Prompt.ask("\n[cyan]What deserves MORE of your time next week?[/cyan]", default="")
    q4 = Prompt.ask("\n[cyan]Next week's ONE essential priority?[/cyan]", default="")

    review_data = {
        "week_start": str(week_start),
        "date": str(date.today()),
        "sessions": total_sessions,
        "focus_minutes": total_minutes,
        "produced_results": q1,
        "stop_doing": q2,
        "more_time": q3,
        "next_priority": q4
    }

    if "weekly_reviews" not in stats_data:
        stats_data["weekly_reviews"] = []
    stats_data["weekly_reviews"].append(review_data)
    save_stats(stats_data)

    reflection_dir = DATA_DIR / "reflections"
    reflection_dir.mkdir(exist_ok=True)

    review_file = reflection_dir / f"week-{week_start}.md"
    with open(review_file, "w") as f:
        f.write(f"# Weekly Review: {week_start} to {date.today()}\n\n")
        f.write(f"## Stats\n- Sessions: {total_sessions}\n- Focus time: {format_duration(total_minutes)}\n\n")
        f.write(f"## 80/20 Analysis\n\n**What produced 80% of results:** {q1}\n\n")
        f.write(f"**Stop doing:** {q2}\n\n**More time on:** {q3}\n\n**Next week's priority:** {q4}\n")

    console.print()
    console.print(Panel.fit(
        f"[bold green]Review saved![/bold green]\n\n[dim]Next week's focus: {q4}[/dim]",
        border_style="green"
    ))


def do_break(duration: int):
    """Run a break timer."""
    console.print()
    console.print(Panel.fit(
        f"[bold cyan]BREAK TIME - {duration} minutes[/bold cyan]\n\n"
        "[dim]Suggestions:[/dim]\n"
        "  - Stand up and stretch\n"
        "  - Look away from screen (20-20-20 rule)\n"
        "  - Hydrate\n"
        "  - Quick walk",
        border_style="cyan"
    ))

    notify("Focus Mode", f"Break time! {duration} minutes to recharge.")

    total_seconds = duration * 60

    with Progress(
        TextColumn("[cyan]Break"),
        BarColumn(bar_width=30),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        task = progress.add_task("", total=total_seconds)
        for _ in range(total_seconds):
            time.sleep(1)
            progress.advance(task)

    notify("Focus Mode", "Break's over! Ready for another session?")
    say("Break complete.")
    console.print("\n[green]Break complete! Type 'focus' to start another session.[/green]")


@cli.command()
@click.argument("duration", type=int, default=5)
def break_(duration: int):
    """Start a break timer."""
    do_break(duration)


# Alias 'break' command
cli.add_command(break_, name="break")


if __name__ == "__main__":
    cli()
