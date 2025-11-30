#!/usr/bin/env python3
"""
Focus Mode: Evidence-Based Productivity System
A terminal-based focus tool built on behavioral science research.
"""

import json
import os
import random
import subprocess
import sys
import time
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Optional

import click
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.table import Table
from rich.text import Text
from rich import box

# Initialize Rich console
console = Console()

# Paths
FOCUS_DIR = Path.home() / ".warp" / "focus"
CONFIG_FILE = FOCUS_DIR / "config.yaml"
DATA_DIR = FOCUS_DIR / "data"
SESSIONS_FILE = DATA_DIR / "sessions.json"
STATS_FILE = DATA_DIR / "stats.json"
QUOTES_FILE = FOCUS_DIR / "quotes.txt"
ACTIVE_SESSION_FILE = DATA_DIR / ".active_session.json"


def load_config() -> dict:
    """Load configuration from YAML file."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return yaml.safe_load(f)
    return {
        "session": {"default_duration": 20, "short_break": 5, "long_break": 15, "sessions_before_long_break": 4},
        "notifications": {"enabled": True, "sound": "Glass", "voice": True},
        "gamification": {"base_xp": 50, "goal_bonus": 15, "no_distraction_bonus": 20,
                         "first_session_bonus": 25, "streak_multiplier": 0.1, "critical_hit_chance": 0.10},
        "streaks": {"sessions_per_day": 3, "freeze_earn_days": 7, "weekend_pause": False},
        "goals": {"daily_sessions": 4, "daily_focus_minutes": 80}
    }


def load_stats() -> dict:
    """Load stats from JSON file."""
    if STATS_FILE.exists():
        with open(STATS_FILE) as f:
            return json.load(f)
    return {
        "xp": 0,
        "level": 1,
        "total_sessions": 0,
        "total_focus_minutes": 0,
        "streaks": {
            "daily": 0,
            "daily_best": 0,
            "weekly": 0,
            "weekly_best": 0,
            "current_run": 0,
            "current_run_best": 0,
            "freezes_available": 0,
            "last_session_date": None
        },
        "today": {
            "date": str(date.today()),
            "sessions": 0,
            "focus_minutes": 0,
            "xp_earned": 0,
            "goal": None,
            "energy_readings": []
        }
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


def get_random_quote() -> str:
    """Get a random motivational quote."""
    if QUOTES_FILE.exists():
        with open(QUOTES_FILE) as f:
            quotes = [line.strip() for line in f if line.strip()]
        return random.choice(quotes) if quotes else "Stay focused!"
    return "Stay focused!"


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


def get_level_info(xp: int) -> tuple[int, str, int, int]:
    """Get level, title, XP for current level, XP needed for next level."""
    level = 1
    remaining_xp = xp
    titles = {
        (1, 5): "Apprentice",
        (6, 10): "Focused",
        (11, 15): "Deep Worker",
        (16, 20): "Flow Master",
        (21, 100): "Productivity Legend"
    }

    thresholds = [(5, 100), (5, 250), (5, 400), (5, 600)]

    for count, xp_per_level in thresholds:
        for _ in range(count):
            if remaining_xp >= xp_per_level:
                remaining_xp -= xp_per_level
                level += 1
            else:
                # Found current level
                for (low, high), title in titles.items():
                    if low <= level <= high:
                        return level, title, remaining_xp, xp_per_level
                return level, "Legend", remaining_xp, 800

    # Level 21+
    while remaining_xp >= 800:
        remaining_xp -= 800
        level += 1

    return level, "Productivity Legend", remaining_xp, 800


def calculate_xp(session: dict, stats: dict, config: dict) -> tuple[int, list[str]]:
    """Calculate XP earned for a session."""
    gam = config.get("gamification", {})
    base = gam.get("base_xp", 50)
    bonuses = []
    total = base

    # Goal achieved bonus
    if session.get("goal_achieved") in ["y", "yes", True]:
        bonus = gam.get("goal_bonus", 15)
        total += bonus
        bonuses.append(f"+{bonus} goal achieved")
    elif session.get("goal_achieved") == "partial":
        bonus = gam.get("goal_bonus", 15) // 2
        total += bonus
        bonuses.append(f"+{bonus} partial goal")

    # No distractions bonus
    if session.get("distractions", 0) == 0:
        bonus = gam.get("no_distraction_bonus", 20)
        total += bonus
        bonuses.append(f"+{bonus} no distractions")

    # First session of day bonus
    today_stats = stats.get("today", {})
    if today_stats.get("date") != str(date.today()) or today_stats.get("sessions", 0) == 0:
        bonus = gam.get("first_session_bonus", 25)
        total += bonus
        bonuses.append(f"+{bonus} first session")

    # Streak multiplier
    streak_days = stats.get("streaks", {}).get("daily", 0)
    if streak_days > 0:
        multiplier = min(2.0, 1.0 + (streak_days * gam.get("streak_multiplier", 0.1)))
        if multiplier > 1.0:
            streak_bonus = int(total * (multiplier - 1))
            total += streak_bonus
            bonuses.append(f"+{streak_bonus} streak x{multiplier:.1f}")

    # Critical hit (random bonus)
    if random.random() < gam.get("critical_hit_chance", 0.10):
        crit_bonus = total  # Double the XP
        total += crit_bonus
        bonuses.append(f"+{crit_bonus} CRITICAL HIT!")

    return total, bonuses


def update_streaks(stats: dict, completed: bool = True):
    """Update streak information after a session."""
    streaks = stats.get("streaks", {})
    today = str(date.today())
    last_date = streaks.get("last_session_date")

    if completed:
        # Update current run
        streaks["current_run"] = streaks.get("current_run", 0) + 1
        streaks["current_run_best"] = max(streaks.get("current_run_best", 0), streaks["current_run"])

        # Check daily streak
        today_sessions = stats.get("today", {}).get("sessions", 0)
        sessions_needed = load_config().get("streaks", {}).get("sessions_per_day", 3)

        if today_sessions >= sessions_needed:
            if last_date:
                last = datetime.strptime(last_date, "%Y-%m-%d").date()
                diff = (date.today() - last).days
                if diff == 1:
                    streaks["daily"] = streaks.get("daily", 0) + 1
                elif diff > 1:
                    # Check for freeze
                    if streaks.get("freezes_available", 0) > 0 and diff == 2:
                        streaks["freezes_available"] -= 1
                        streaks["daily"] = streaks.get("daily", 0) + 1
                    else:
                        streaks["daily"] = 1
            else:
                streaks["daily"] = 1

            streaks["daily_best"] = max(streaks.get("daily_best", 0), streaks["daily"])

            # Earn freeze days
            if streaks["daily"] > 0 and streaks["daily"] % 7 == 0:
                streaks["freezes_available"] = streaks.get("freezes_available", 0) + 1

        streaks["last_session_date"] = today
    else:
        # Session aborted
        streaks["current_run"] = 0

    stats["streaks"] = streaks


def display_session_ui(task: str, duration_minutes: int, goal: str, intention: str):
    """Display the focus session UI with progress bar."""
    total_seconds = duration_minutes * 60
    start_time = time.time()
    quote = get_random_quote()
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

            task_id = progress.add_task(f"[cyan]Focusing on: {task}", total=total_seconds)

            while not progress.finished:
                if paused:
                    console.print("\n[yellow]PAUSED[/yellow] - Press Enter to resume, 's' to stop")
                    try:
                        import select
                        if select.select([sys.stdin], [], [], 0.5)[0]:
                            key = sys.stdin.read(1)
                            if key == 's':
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

                # Display session info
                console.print(f"\n  [dim]Goal: {goal}[/dim]", end="\r")

                # Check for keyboard input (non-blocking)
                try:
                    import select
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        key = sys.stdin.read(1)
                        if key == 'p':
                            paused = True
                            pause_start = time.time()
                        elif key == 's':
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


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Focus Mode: Evidence-Based Productivity System"""
    if ctx.invoked_subcommand is None:
        # Default behavior: start a session or show status
        if ACTIVE_SESSION_FILE.exists():
            ctx.invoke(status)
        else:
            ctx.invoke(start)


@cli.command()
@click.argument("duration", type=int, default=0)
@click.argument("task", type=str, default="")
def start(duration: int, task: str):
    """Start a focus session."""
    config = load_config()
    stats = load_stats()

    if duration == 0:
        duration = config.get("session", {}).get("default_duration", 20)

    # Reset today's stats if new day
    if stats.get("today", {}).get("date") != str(date.today()):
        stats["today"] = {
            "date": str(date.today()),
            "sessions": 0,
            "focus_minutes": 0,
            "xp_earned": 0,
            "goal": stats.get("today", {}).get("tomorrow_priority"),
            "energy_readings": []
        }

    # Session count for today
    session_num = stats["today"]["sessions"] + 1

    # Display session start
    console.print(Panel.fit(
        "[bold cyan]FOCUS SESSION STARTING[/bold cyan]",
        border_style="cyan"
    ))
    console.print()

    # Get task if not provided
    if not task:
        task = Prompt.ask("[cyan]What are you working on?[/cyan]", default="Deep work")

    console.print(f"\n[bold]Task:[/bold] {task}")
    console.print(f"[bold]Duration:[/bold] {duration} minutes")
    console.print(f"[bold]Session:[/bold] #{session_num} today")
    console.print()

    # Goal clarification (Flow trigger)
    goal = Prompt.ask("[cyan]What specific outcome marks this session complete?[/cyan]")

    # Implementation intention
    distraction = Prompt.ask("[cyan]What might distract you?[/cyan]", default="notifications")
    response = Prompt.ask(f"[cyan]When you want to check {distraction}, you will:[/cyan]", default="note it and continue")
    intention = f"When I want to check {distraction}, I will {response}"

    console.print()
    console.print(Panel.fit(
        f"[bold green]SESSION ACTIVE[/bold green]\n\n"
        f"[dim]Goal: {goal}[/dim]\n"
        f"[dim]Intention: {intention}[/dim]\n\n"
        f"[dim][p] pause  [s] stop  [d] log distraction[/dim]",
        border_style="green"
    ))

    # Store active session
    active_session = {
        "start_time": datetime.now().isoformat(),
        "task": task,
        "duration": duration,
        "goal": goal,
        "intention": intention
    }
    with open(ACTIVE_SESSION_FILE, "w") as f:
        json.dump(active_session, f)

    # Run the session
    notify("Focus Mode", f"Starting {duration}-minute session: {task}")

    result = display_session_ui(task, duration, goal, intention)

    # Remove active session file
    if ACTIVE_SESSION_FILE.exists():
        ACTIVE_SESSION_FILE.unlink()

    # Session end
    console.clear()

    if result["completed"]:
        notify("Focus Mode", "Session complete! Great work!", sound=True)
        say("Focus session complete. Great work!")

        console.print(Panel.fit(
            "[bold green]SESSION COMPLETE![/bold green]",
            border_style="green"
        ))

        # Quick reflection
        console.print()
        goal_achieved = Prompt.ask(
            "[cyan]Did you achieve your goal?[/cyan]",
            choices=["y", "n", "partial"],
            default="y"
        )

        productivity = IntPrompt.ask(
            "[cyan]Productivity rating (1-5)[/cyan]",
            default=4
        )

        resume_note = Prompt.ask(
            "[cyan]Note for when you resume this work[/cyan]",
            default=""
        )

        # Calculate XP
        session_data = {
            "task": task,
            "goal": goal,
            "goal_achieved": goal_achieved,
            "productivity": productivity,
            "distractions": result.get("distractions", 0),
            "duration": duration,
            "resume_note": resume_note,
            "timestamp": datetime.now().isoformat()
        }

        xp_earned, bonuses = calculate_xp(session_data, stats, config)

        # Update stats
        stats["xp"] += xp_earned
        stats["total_sessions"] += 1
        stats["total_focus_minutes"] += duration
        stats["today"]["sessions"] += 1
        stats["today"]["focus_minutes"] += duration
        stats["today"]["xp_earned"] += xp_earned

        # Update streaks
        update_streaks(stats, completed=True)

        # Get level info
        level, title, level_xp, next_level_xp = get_level_info(stats["xp"])
        stats["level"] = level

        # Save session
        sessions = load_sessions()
        sessions.append(session_data)
        save_sessions(sessions)
        save_stats(stats)

        # Display XP earned
        console.print()
        console.print(f"[bold green]+{xp_earned} XP[/bold green]")
        for bonus in bonuses:
            console.print(f"  [dim]{bonus}[/dim]")

        console.print()
        console.print(f"[bold]Level {level} {title}[/bold] | {stats['xp']} XP total")

        # Progress bar to next level
        progress_pct = int((level_xp / next_level_xp) * 20)
        bar = "█" * progress_pct + "░" * (20 - progress_pct)
        console.print(f"[{bar}] {level_xp}/{next_level_xp} to next level")

        # Streak info
        streaks = stats.get("streaks", {})
        console.print(f"\n[dim]Streak: {streaks.get('daily', 0)} days | Run: {streaks.get('current_run', 0)} sessions[/dim]")

        # Suggest break
        console.print()
        sessions_today = stats["today"]["sessions"]
        if sessions_today % 4 == 0:
            break_time = config.get("session", {}).get("long_break", 15)
            console.print(f"[yellow]Time for a longer break! ({break_time} min suggested)[/yellow]")
        else:
            break_time = config.get("session", {}).get("short_break", 5)
            console.print(f"[cyan]Take a {break_time}-minute break. Stand, stretch, hydrate.[/cyan]")

        if Confirm.ask("\n[cyan]Start break timer?[/cyan]", default=True):
            do_break(break_time)

    else:
        console.print(Panel.fit(
            f"[yellow]Session ended early ({result.get('minutes', 0)} min)[/yellow]",
            border_style="yellow"
        ))

        # Still log partial session
        session_data = {
            "task": task,
            "goal": goal,
            "completed": False,
            "minutes_completed": result.get("minutes", 0),
            "reason": result.get("reason", "stopped"),
            "timestamp": datetime.now().isoformat()
        }

        sessions = load_sessions()
        sessions.append(session_data)
        save_sessions(sessions)

        # Update streaks (broken run)
        update_streaks(stats, completed=False)
        save_stats(stats)


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
    say("Break complete. Ready to focus again?")
    console.print("\n[green]Break complete! Type 'focus' to start another session.[/green]")


@cli.command()
@click.argument("duration", type=int, default=5)
def break_(duration: int):
    """Start a break timer."""
    do_break(duration)


@cli.command()
def status():
    """Show current session status or stats."""
    stats = load_stats()

    # Check for active session
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

    # Show quick stats
    level, title, level_xp, next_level_xp = get_level_info(stats.get("xp", 0))
    streaks = stats.get("streaks", {})
    today = stats.get("today", {})

    console.print(Panel.fit(
        f"[bold]Level {level} {title}[/bold] | {stats.get('xp', 0)} XP\n\n"
        f"Today: {today.get('sessions', 0)} sessions | {today.get('focus_minutes', 0)} min\n"
        f"Streak: {streaks.get('daily', 0)} days | Run: {streaks.get('current_run', 0)}\n\n"
        f"[dim]Type 'focus' to start a session[/dim]",
        title="Focus Mode",
        border_style="blue"
    ))


@cli.command()
@click.argument("period", type=str, default="today")
def stats(period: str):
    """Show statistics."""
    stats_data = load_stats()
    sessions = load_sessions()

    level, title, level_xp, next_level_xp = get_level_info(stats_data.get("xp", 0))
    streaks = stats_data.get("streaks", {})
    today = stats_data.get("today", {})

    if period == "today":
        console.print(Panel.fit(
            f"[bold cyan]TODAY'S FOCUS[/bold cyan]\n"
            f"[dim]{date.today().strftime('%A, %B %d')}[/dim]",
            border_style="cyan"
        ))

        console.print(f"\nSessions: [bold]{today.get('sessions', 0)}[/bold]")
        console.print(f"Focus time: [bold]{today.get('focus_minutes', 0)} min[/bold]")
        console.print(f"XP earned: [bold]+{today.get('xp_earned', 0)}[/bold]")

        # Today's sessions
        today_sessions = [s for s in sessions if s.get("timestamp", "").startswith(str(date.today()))]
        if today_sessions:
            console.print("\n[bold]Sessions:[/bold]")
            for s in today_sessions:
                status = "[green]✓[/green]" if s.get("completed", s.get("goal_achieved")) else "[yellow]○[/yellow]"
                time_str = s.get("timestamp", "")[:16].split("T")[1] if "T" in s.get("timestamp", "") else ""
                console.print(f"  {status} {time_str} - {s.get('task', 'Unknown')} ({s.get('duration', s.get('minutes_completed', 0))} min)")

    elif period == "week":
        console.print(Panel.fit(
            "[bold cyan]THIS WEEK'S FOCUS[/bold cyan]",
            border_style="cyan"
        ))

        # Calculate weekly stats
        week_start = date.today() - timedelta(days=date.today().weekday())
        week_sessions = [s for s in sessions if s.get("timestamp", "")[:10] >= str(week_start)]

        total_sessions = len([s for s in week_sessions if s.get("completed", s.get("goal_achieved"))])
        total_minutes = sum(s.get("duration", s.get("minutes_completed", 0)) for s in week_sessions)

        console.print(f"\nSessions: [bold]{total_sessions}[/bold]")
        console.print(f"Focus time: [bold]{total_minutes // 60}h {total_minutes % 60}m[/bold]")

        # Daily breakdown
        console.print("\n[bold]Daily breakdown:[/bold]")
        for i in range(7):
            day = week_start + timedelta(days=i)
            day_sessions = [s for s in week_sessions if s.get("timestamp", "")[:10] == str(day)]
            day_minutes = sum(s.get("duration", s.get("minutes_completed", 0)) for s in day_sessions)
            bar_len = min(20, day_minutes // 10)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            day_name = day.strftime("%a")
            marker = " <- Today" if day == date.today() else ""
            console.print(f"  {day_name} [{bar}] {day_minutes} min{marker}")

    else:
        # All-time stats
        console.print(Panel.fit(
            "[bold cyan]ALL-TIME STATS[/bold cyan]",
            border_style="cyan"
        ))

        console.print(f"\n[bold]Level {level} {title}[/bold]")
        console.print(f"Total XP: {stats_data.get('xp', 0)}")
        console.print(f"Total sessions: {stats_data.get('total_sessions', 0)}")
        console.print(f"Total focus time: {stats_data.get('total_focus_minutes', 0) // 60}h {stats_data.get('total_focus_minutes', 0) % 60}m")

    # Always show streaks
    console.print(f"\n[bold]Streaks:[/bold]")
    console.print(f"  Daily: {streaks.get('daily', 0)} days (best: {streaks.get('daily_best', 0)})")
    console.print(f"  Run: {streaks.get('current_run', 0)} sessions (best: {streaks.get('current_run_best', 0)})")
    console.print(f"  Freezes: {streaks.get('freezes_available', 0)} available")


@cli.command()
def streak():
    """Show streak information."""
    stats_data = load_stats()
    streaks = stats_data.get("streaks", {})

    console.print(Panel.fit(
        "[bold cyan]YOUR STREAKS[/bold cyan]",
        border_style="cyan"
    ))

    # Daily streak visualization
    daily = streaks.get("daily", 0)
    daily_bar = "█" * min(daily, 10) + "░" * max(0, 10 - daily)
    console.print(f"\n[bold]Daily Streak:[/bold] {daily} days")
    console.print(f"  [{daily_bar}] Best: {streaks.get('daily_best', 0)} days")

    # Current run
    run = streaks.get("current_run", 0)
    run_bar = "█" * min(run, 10) + "░" * max(0, 10 - run)
    console.print(f"\n[bold]Current Run:[/bold] {run} sessions")
    console.print(f"  [{run_bar}] Best: {streaks.get('current_run_best', 0)} sessions")

    # Freezes
    freezes = streaks.get("freezes_available", 0)
    console.print(f"\n[bold]Freeze Days:[/bold] {freezes} available")
    console.print(f"  [dim]Earn 1 freeze for every 7 consecutive days[/dim]")

    # Next milestone
    next_freeze_in = 7 - (daily % 7) if daily > 0 else 7
    console.print(f"\n[dim]Next freeze in: {next_freeze_in} days[/dim]")


@cli.command()
def gm():
    """Morning ritual - start your day with intention."""
    stats_data = load_stats()
    config = load_config()

    # Check if new day, reset today stats
    if stats_data.get("today", {}).get("date") != str(date.today()):
        yesterday = stats_data.get("today", {})
        stats_data["today"] = {
            "date": str(date.today()),
            "sessions": 0,
            "focus_minutes": 0,
            "xp_earned": 0,
            "goal": yesterday.get("tomorrow_priority"),
            "energy_readings": []
        }

    console.print(Panel.fit(
        f"[bold cyan]Good morning![/bold cyan]\n"
        f"[dim]{date.today().strftime('%A, %B %d, %Y')}[/dim]",
        border_style="cyan"
    ))

    # Yesterday's summary
    yesterday_date = date.today() - timedelta(days=1)
    sessions = load_sessions()
    yesterday_sessions = [s for s in sessions if s.get("timestamp", "")[:10] == str(yesterday_date)]

    if yesterday_sessions:
        completed = len([s for s in yesterday_sessions if s.get("completed", s.get("goal_achieved"))])
        minutes = sum(s.get("duration", s.get("minutes_completed", 0)) for s in yesterday_sessions)
        console.print(f"\n[bold]Yesterday:[/bold] {completed} sessions | {minutes} min focused")

    # Current streak
    streaks = stats_data.get("streaks", {})
    console.print(f"[bold]Streak:[/bold] {streaks.get('daily', 0)} days")

    # Level
    level, title, _, _ = get_level_info(stats_data.get("xp", 0))
    console.print(f"[bold]Level:[/bold] {level} {title}")

    # Energy check
    console.print()
    energy = IntPrompt.ask("[cyan]Energy level right now? (1-5)[/cyan]", default=4)
    stats_data["today"]["energy_readings"].append({
        "time": datetime.now().strftime("%H:%M"),
        "level": energy
    })

    # Focus level for today
    console.print("\n[bold]Focus level today:[/bold]")
    console.print("  [1] Light (2 sessions)")
    console.print("  [2] Normal (4 sessions)")
    console.print("  [3] Deep (6 sessions)")

    focus_level = IntPrompt.ask("[cyan]Choose[/cyan]", default=2)
    session_goals = {1: 2, 2: 4, 3: 6}
    stats_data["today"]["session_goal"] = session_goals.get(focus_level, 4)

    # Priority
    yesterday_priority = stats_data["today"].get("goal", "")
    if yesterday_priority:
        console.print(f"\n[dim]Yesterday you set: {yesterday_priority}[/dim]")

    priority = Prompt.ask("[cyan]What's your #1 priority today?[/cyan]", default=yesterday_priority or "")
    stats_data["today"]["goal"] = priority

    save_stats(stats_data)

    console.print()
    console.print(Panel.fit(
        f"[bold green]Ready to go![/bold green]\n\n"
        f"Goal: {session_goals.get(focus_level, 4)} focused sessions\n"
        f"Priority: {priority}\n\n"
        f"[dim]Type 'focus' to begin your first session[/dim]",
        border_style="green"
    ))


@cli.command()
def eod():
    """End of day review."""
    stats_data = load_stats()
    sessions = load_sessions()

    today = stats_data.get("today", {})
    today_sessions = [s for s in sessions if s.get("timestamp", "")[:10] == str(date.today())]

    console.print(Panel.fit(
        f"[bold cyan]END OF DAY REVIEW[/bold cyan]\n"
        f"[dim]{date.today().strftime('%A, %B %d, %Y')}[/dim]",
        border_style="cyan"
    ))

    # Today's results
    session_goal = today.get("session_goal", 4)
    completed = today.get("sessions", 0)
    completion_pct = int((completed / session_goal) * 100) if session_goal > 0 else 0

    console.print(f"\n[bold]Sessions:[/bold] {completed}/{session_goal} ({completion_pct}%)")
    console.print(f"[bold]Focus time:[/bold] {today.get('focus_minutes', 0)} min")
    console.print(f"[bold]XP earned:[/bold] +{today.get('xp_earned', 0)}")

    # Streak update
    streaks = stats_data.get("streaks", {})
    if completed >= 3:
        console.print(f"\n[green]Streak extended to {streaks.get('daily', 0)} days![/green]")
    else:
        console.print(f"\n[yellow]Need {3 - completed} more sessions to maintain streak[/yellow]")

    # Show completed tasks
    if today_sessions:
        console.print("\n[bold]Completed:[/bold]")
        for s in today_sessions:
            if s.get("completed", s.get("goal_achieved")):
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
            f.write(f"- Sessions: {completed}/{session_goal}\n")
            f.write(f"- Focus time: {today.get('focus_minutes', 0)} min\n")
            f.write(f"- XP: +{today.get('xp_earned', 0)}\n\n")
            f.write(f"## Reflection\n")
            f.write(f"**What went well:** {went_well}\n\n")
            f.write(f"**Tomorrow's priority:** {tomorrow}\n")

    # Save tomorrow's priority
    stats_data["today"]["tomorrow_priority"] = tomorrow
    save_stats(stats_data)

    console.print()
    console.print(Panel.fit(
        "[bold green]Great work today![/bold green]\n\n"
        f"[dim]Reflection saved. Rest well![/dim]",
        border_style="green"
    ))


# Alias 'break' command (break is a reserved word)
cli.add_command(break_, name="break")


if __name__ == "__main__":
    cli()
