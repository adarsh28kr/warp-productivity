#!/usr/bin/env python3
"""
Focus Mode v2: Expert-Reviewed Productivity System
Based on Cal Newport, Nir Eyal, and executive coaching methodologies.

Philosophy: Minimalist deep work system with flexible sessions and Essentialism layer.
No gamification - just clean tracking and evidence-based practices.
"""

import json
import subprocess
import sys
import time
from datetime import datetime, date, timedelta
from pathlib import Path

import click
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.prompt import Prompt, IntPrompt, Confirm

# Initialize Rich console
console = Console()

# Paths
FOCUS_DIR = Path.home() / ".warp" / "focus"
CONFIG_FILE = FOCUS_DIR / "config.yaml"
DATA_DIR = FOCUS_DIR / "data"
SESSIONS_FILE = DATA_DIR / "sessions.json"
STATS_FILE = DATA_DIR / "stats.json"
ACTIVE_SESSION_FILE = DATA_DIR / ".active_session.json"


def load_config() -> dict:
    """Load configuration from YAML file."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return yaml.safe_load(f)
    return {
        "session": {"suggested_duration": 90, "short_break": 5, "long_break": 15},
        "notifications": {"enabled": True, "sound": "Glass", "voice": True}
    }


def load_stats() -> dict:
    """Load stats from JSON file."""
    if STATS_FILE.exists():
        with open(STATS_FILE) as f:
            return json.load(f)
    return {
        "total_sessions": 0,
        "total_focus_minutes": 0,
        "today": {
            "date": str(date.today()),
            "sessions": 0,
            "focus_minutes": 0,
            "essential_task": None,
            "energy_readings": []
        },
        "weekly_reviews": []
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


def display_session_ui(task: str, duration_minutes: int, goal: str, intention: str):
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
    """Focus Mode v2: Deep Work System (Expert-Reviewed)"""
    if ctx.invoked_subcommand is None:
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

    # Reset today's stats if new day
    if stats.get("today", {}).get("date") != str(date.today()):
        stats["today"] = {
            "date": str(date.today()),
            "sessions": 0,
            "focus_minutes": 0,
            "essential_task": stats.get("today", {}).get("tomorrow_priority"),
            "energy_readings": []
        }

    session_num = stats["today"]["sessions"] + 1

    console.print(Panel.fit(
        "[bold cyan]DEEP WORK SESSION[/bold cyan]",
        border_style="cyan"
    ))

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

    # Implementation intention (strongest evidence-based feature)
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
        "intention": intention,
        "is_essential": is_essential
    }
    with open(ACTIVE_SESSION_FILE, "w") as f:
        json.dump(active_session, f)

    notify("Focus Mode", f"Starting {duration}-minute deep work session")

    result = display_session_ui(task, duration, goal, intention)

    # Remove active session file
    if ACTIVE_SESSION_FILE.exists():
        ACTIVE_SESSION_FILE.unlink()

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

        resume_note = Prompt.ask(
            "[cyan]Note for next session[/cyan]",
            default=""
        )

        # Save session data
        session_data = {
            "task": task,
            "goal": goal,
            "goal_achieved": goal_achieved,
            "distractions": result.get("distractions", 0),
            "duration": duration,
            "is_essential": is_essential,
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

        # Show simple stats
        console.print()
        console.print(f"[bold]Today:[/bold] {stats['today']['sessions']} sessions | {format_duration(stats['today']['focus_minutes'])}")

        # Get week stats
        week_start = date.today() - timedelta(days=date.today().weekday())
        week_sessions = [s for s in sessions if s.get("timestamp", "")[:10] >= str(week_start)]
        week_minutes = sum(s.get("duration", 0) for s in week_sessions)
        console.print(f"[bold]This week:[/bold] {len(week_sessions)} sessions | {format_duration(week_minutes)}")

        # Suggest break
        console.print()
        sessions_today = stats["today"]["sessions"]
        if sessions_today % 4 == 0:
            break_time = config.get("session", {}).get("long_break", 15)
            console.print(f"[cyan]Take a {break_time}-minute break. You've earned it.[/cyan]")
        else:
            break_time = config.get("session", {}).get("short_break", 5)
            console.print(f"[cyan]Take a {break_time}-minute break. Stand, stretch, hydrate.[/cyan]")

        if Confirm.ask("\n[cyan]Start break timer?[/cyan]", default=True):
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


@cli.command()
def status():
    """Show current session status or quick stats."""
    stats = load_stats()

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

    today = stats.get("today", {})
    sessions = load_sessions()

    # Week stats
    week_start = date.today() - timedelta(days=date.today().weekday())
    week_sessions = [s for s in sessions if s.get("timestamp", "")[:10] >= str(week_start)]
    week_minutes = sum(s.get("duration", s.get("minutes_completed", 0)) for s in week_sessions)

    console.print(Panel.fit(
        f"[bold]TODAY[/bold]\n"
        f"Sessions: {today.get('sessions', 0)} | Focus: {format_duration(today.get('focus_minutes', 0))}\n\n"
        f"[bold]THIS WEEK[/bold]\n"
        f"Sessions: {len(week_sessions)} | Focus: {format_duration(week_minutes)}\n\n"
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
    today = stats_data.get("today", {})

    if period == "today":
        console.print(Panel.fit(
            f"[bold cyan]TODAY[/bold cyan]\n"
            f"[dim]{date.today().strftime('%A, %B %d')}[/dim]",
            border_style="cyan"
        ))

        console.print(f"\nSessions: [bold]{today.get('sessions', 0)}[/bold]")
        console.print(f"Focus time: [bold]{format_duration(today.get('focus_minutes', 0))}[/bold]")

        # Today's sessions
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
            console.print(f"  {day_name} [{bar}] {format_duration(day_minutes)}{marker}")

        # Insights
        if week_sessions:
            console.print("\n[bold]Insights:[/bold]")

            # Find peak hours
            hour_counts = {}
            for s in week_sessions:
                if "T" in s.get("timestamp", ""):
                    hour = int(s["timestamp"].split("T")[1][:2])
                    hour_counts[hour] = hour_counts.get(hour, 0) + 1

            if hour_counts:
                peak_hour = max(hour_counts, key=hour_counts.get)
                console.print(f"  Peak focus hour: {peak_hour}:00 - {peak_hour+1}:00")

            # Find most productive day
            day_counts = {}
            for s in week_sessions:
                day = s.get("timestamp", "")[:10]
                day_counts[day] = day_counts.get(day, 0) + s.get("duration", 0)

            if day_counts:
                best_day = max(day_counts, key=day_counts.get)
                best_day_name = datetime.strptime(best_day, "%Y-%m-%d").strftime("%A")
                console.print(f"  Most productive: {best_day_name}")

    else:
        # All-time stats
        console.print(Panel.fit(
            "[bold cyan]ALL-TIME STATS[/bold cyan]",
            border_style="cyan"
        ))

        console.print(f"\nTotal sessions: [bold]{stats_data.get('total_sessions', 0)}[/bold]")
        console.print(f"Total focus time: [bold]{format_duration(stats_data.get('total_focus_minutes', 0))}[/bold]")

        if stats_data.get('total_sessions', 0) > 0:
            avg = stats_data.get('total_focus_minutes', 0) // stats_data.get('total_sessions', 1)
            console.print(f"Avg session length: [bold]{avg} min[/bold]")


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

    # This week's stats
    week_start = date.today() - timedelta(days=date.today().weekday())
    week_sessions = [s for s in sessions if s.get("timestamp", "")[:10] >= str(week_start)]

    total_sessions = len(week_sessions)
    total_minutes = sum(s.get("duration", s.get("minutes_completed", 0)) for s in week_sessions)

    console.print(f"\n[bold]This week:[/bold] {total_sessions} sessions | {format_duration(total_minutes)}")

    # Show what you worked on
    if week_sessions:
        tasks = {}
        for s in week_sessions:
            task = s.get("task", "Unknown")
            tasks[task] = tasks.get(task, 0) + s.get("duration", 0)

        console.print("\n[bold]Time spent:[/bold]")
        for task, minutes in sorted(tasks.items(), key=lambda x: x[1], reverse=True)[:5]:
            console.print(f"  - {task}: {format_duration(minutes)}")

    # 80/20 Questions
    console.print("\n" + "━" * 50)
    console.print("[bold]THE 80/20 QUESTIONS[/bold]")
    console.print("━" * 50)

    q1 = Prompt.ask("\n[cyan]Which 20% of your work produced 80% of meaningful results?[/cyan]", default="")

    q2 = Prompt.ask("\n[cyan]What should you STOP doing?[/cyan]", default="")

    q3 = Prompt.ask("\n[cyan]What deserves MORE of your time next week?[/cyan]", default="")

    q4 = Prompt.ask("\n[cyan]Next week's ONE essential priority?[/cyan]", default="")

    # Save review
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

    # Save to reflections file
    reflection_dir = DATA_DIR / "reflections"
    reflection_dir.mkdir(exist_ok=True)

    review_file = reflection_dir / f"week-{week_start}.md"
    with open(review_file, "w") as f:
        f.write(f"# Weekly Review: {week_start} to {date.today()}\n\n")
        f.write(f"## Stats\n")
        f.write(f"- Sessions: {total_sessions}\n")
        f.write(f"- Focus time: {format_duration(total_minutes)}\n\n")
        f.write(f"## 80/20 Analysis\n\n")
        f.write(f"**What produced 80% of results:** {q1}\n\n")
        f.write(f"**Stop doing:** {q2}\n\n")
        f.write(f"**More time on:** {q3}\n\n")
        f.write(f"**Next week's priority:** {q4}\n")

    console.print()
    console.print(Panel.fit(
        f"[bold green]Review saved![/bold green]\n\n"
        f"[dim]Next week's focus: {q4}[/dim]",
        border_style="green"
    ))


@cli.command()
def gm():
    """Morning ritual - start your day with intention."""
    stats_data = load_stats()

    # Reset today's stats if new day
    if stats_data.get("today", {}).get("date") != str(date.today()):
        yesterday = stats_data.get("today", {})
        stats_data["today"] = {
            "date": str(date.today()),
            "sessions": 0,
            "focus_minutes": 0,
            "essential_task": yesterday.get("tomorrow_priority"),
            "energy_readings": []
        }

    console.print(Panel.fit(
        f"[bold cyan]Good morning![/bold cyan]\n"
        f"[dim]{date.today().strftime('%A, %B %d, %Y')}[/dim]",
        border_style="cyan"
    ))

    # Yesterday's summary
    sessions = load_sessions()
    yesterday_date = date.today() - timedelta(days=1)
    yesterday_sessions = [s for s in sessions if s.get("timestamp", "")[:10] == str(yesterday_date)]

    if yesterday_sessions:
        completed = len([s for s in yesterday_sessions if s.get("goal_achieved") or s.get("completed", True)])
        minutes = sum(s.get("duration", s.get("minutes_completed", 0)) for s in yesterday_sessions)
        console.print(f"\n[bold]Yesterday:[/bold] {completed} sessions | {format_duration(minutes)}")

    # Essentialism question (McKeown)
    console.print("\n" + "━" * 50)
    console.print("[bold]THE ONE THING[/bold]")
    console.print("[dim]What is the ONE thing that would make everything else easier?[/dim]")
    console.print("━" * 50)

    essential_task = stats_data["today"].get("essential_task", "")
    if essential_task:
        console.print(f"\n[dim]Yesterday you set: {essential_task}[/dim]")

    priority = Prompt.ask("\n[cyan]Today's essential task[/cyan]", default=essential_task or "")
    stats_data["today"]["essential_task"] = priority

    # Is it truly essential?
    if priority:
        console.print(f"\n[dim]'{priority}'[/dim]")
        is_truly_essential = Confirm.ask("[cyan]Is this truly essential, or merely good?[/cyan]", default=True)
        if not is_truly_essential:
            priority = Prompt.ask("[cyan]What's actually essential?[/cyan]", default="")
            stats_data["today"]["essential_task"] = priority

    # Energy check
    console.print()
    energy = IntPrompt.ask("[cyan]Energy level right now? (1-5)[/cyan]", default=4)
    stats_data["today"]["energy_readings"].append({
        "time": datetime.now().strftime("%H:%M"),
        "level": energy
    })

    save_stats(stats_data)

    console.print()
    console.print(Panel.fit(
        f"[bold green]Ready for deep work[/bold green]\n\n"
        f"Essential task: {priority}\n\n"
        f"[dim]Type 'focus' to begin[/dim]",
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

    # Save tomorrow's priority
    stats_data["today"]["tomorrow_priority"] = tomorrow
    save_stats(stats_data)

    console.print()
    console.print(Panel.fit(
        "[bold green]Good work today.[/bold green]\n\n"
        f"[dim]Rest well. Tomorrow's focus: {tomorrow}[/dim]",
        border_style="green"
    ))


# Alias 'break' command
cli.add_command(break_, name="break")


if __name__ == "__main__":
    cli()
