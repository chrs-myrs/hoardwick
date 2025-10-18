#!/usr/bin/env python3
"""
Preference and usage tracking for Hoardwick.

Learns from user cleanup decisions and project usage patterns.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import click
from rich.console import Console
from rich.table import Table

console = Console()


class PreferenceManager:
    """Manages user preferences and usage patterns."""

    def __init__(self, prefs_file: Path):
        self.prefs_file = prefs_file
        self.preferences = self._load()

    def _load(self) -> Dict:
        """Load preferences from file."""
        if self.prefs_file.exists():
            return json.loads(self.prefs_file.read_text())
        return self._default_preferences()

    def _default_preferences(self) -> Dict:
        """Create default preferences."""
        return {
            "version": "1.0",
            "created": datetime.now().strftime("%Y-%m-%d"),
            "user_preferences": {
                "stale_project_threshold_days": 365,
                "active_project_threshold_days": 90
            },
            "cleanup_rules": {
                "safe_to_remove": [],
                "always_keep": [],
                "project_activity_thresholds": {
                    "active": "modified within 90 days",
                    "semi_active": "modified within 365 days",
                    "stale": "not modified in >365 days"
                }
            },
            "known_active_projects": [],
            "cleanup_decisions": {},
            "notes": "Auto-generated preferences file"
        }

    def save(self):
        """Save preferences to file."""
        self.prefs_file.write_text(json.dumps(self.preferences, indent=2))
        console.print(f"[green]Saved preferences to {self.prefs_file}[/green]")

    def record_cleanup(self, action: str, reason: str, size_gb: float):
        """Record a cleanup decision."""
        date = datetime.now().strftime("%Y-%m-%d")
        if date not in self.preferences["cleanup_decisions"]:
            self.preferences["cleanup_decisions"][date] = []

        self.preferences["cleanup_decisions"][date].append({
            "action": action,
            "reason": reason,
            "size_saved_gb": size_gb,
            "timestamp": datetime.now().isoformat()
        })
        self.save()

    def add_active_project(self, project: str):
        """Mark a project as active."""
        if project not in self.preferences["known_active_projects"]:
            self.preferences["known_active_projects"].append(project)
            self.save()

    def remove_active_project(self, project: str):
        """Remove project from active list."""
        if project in self.preferences["known_active_projects"]:
            self.preferences["known_active_projects"].remove(project)
            self.save()

    def is_active_project(self, project: str) -> bool:
        """Check if project is marked as active."""
        return project in self.preferences["known_active_projects"]


class ProjectAnalyser:
    """Analyses project usage from scan data."""

    def __init__(self, db_path: Path, prefs: PreferenceManager):
        self.db_path = db_path
        self.prefs = prefs

    def classify_projects(self, scan_id: int = None) -> Dict[str, List[Dict]]:
        """
        Classify projects by activity level.

        Returns:
            {
                "active": [...],
                "semi_active": [...],
                "stale": [...]
            }
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get most recent scan if not specified
        if scan_id is None:
            cursor.execute("SELECT MAX(id) FROM scans WHERE status = 'complete'")
            scan_id = cursor.fetchone()[0]

        # Get project activity
        cursor.execute("""
            SELECT
                REPLACE(REPLACE(path, '/home/chris/projects/', ''),
                    SUBSTR(REPLACE(path, '/home/chris/projects/', ''),
                        INSTR(REPLACE(path, '/home/chris/projects/', ''), '/')+1),
                    '') as project,
                COUNT(*) as files,
                SUM(size) as size_bytes,
                MAX(modified) as last_modified
            FROM files
            WHERE scan_id = ?
                AND path LIKE '/home/chris/projects/%'
            GROUP BY project
            ORDER BY MAX(modified) DESC
        """, (scan_id,))

        rows = cursor.fetchall()
        conn.close()

        # Classify by thresholds
        now = datetime.now().timestamp()
        active_threshold = now - (90 * 24 * 60 * 60)
        stale_threshold = now - (365 * 24 * 60 * 60)

        classified = {
            "active": [],
            "semi_active": [],
            "stale": []
        }

        for project, files, size, last_mod in rows:
            project_info = {
                "name": project,
                "files": files,
                "size_mb": size / 1024 / 1024,
                "last_modified": last_mod,
                "days_old": int((now - last_mod) / 86400),
                "in_preferences": self.prefs.is_active_project(project)
            }

            if last_mod > active_threshold or project_info["in_preferences"]:
                classified["active"].append(project_info)
            elif last_mod > stale_threshold:
                classified["semi_active"].append(project_info)
            else:
                classified["stale"].append(project_info)

        return classified


@click.group()
def cli():
    """Hoardwick preference and usage tracking."""
    pass


@cli.command()
@click.option('--database', default='./generated/hoardwick.db', help='Database path')
@click.option('--prefs', default='./.hoardwick-preferences.json', help='Preferences file')
def classify(database: str, prefs: str):
    """Classify projects by activity level."""

    prefs_mgr = PreferenceManager(Path(prefs))
    analyser = ProjectAnalyser(Path(database), prefs_mgr)

    console.print("[bold blue]Project Classification[/bold blue]\n")

    classified = analyser.classify_projects()

    # Show active projects
    console.print("[bold green]Active Projects[/bold green] (< 90 days)")
    table = Table(show_header=True)
    table.add_column("Project")
    table.add_column("Files", justify="right")
    table.add_column("Size", justify="right")
    table.add_column("Days Old", justify="right")
    table.add_column("Status")

    for proj in classified["active"][:20]:
        status = "✓ In prefs" if proj["in_preferences"] else ""
        table.add_row(
            proj["name"],
            f"{proj['files']:,}",
            f"{proj['size_mb']:.1f} MB",
            str(proj['days_old']),
            status
        )

    console.print(table)
    console.print()

    # Show stale projects
    if classified["stale"]:
        console.print("[bold yellow]Stale Projects[/bold yellow] (> 365 days)")
        stale_table = Table(show_header=True)
        stale_table.add_column("Project")
        stale_table.add_column("Size", justify="right")
        stale_table.add_column("Days Old", justify="right")

        for proj in classified["stale"][:20]:
            stale_table.add_row(
                proj["name"],
                f"{proj['size_mb']:.1f} MB",
                str(proj['days_old'])
            )

        console.print(stale_table)

    # Summary
    console.print(f"\n[cyan]Summary:[/cyan]")
    console.print(f"  Active: {len(classified['active'])} projects")
    console.print(f"  Semi-active: {len(classified['semi_active'])} projects")
    console.print(f"  Stale: {len(classified['stale'])} projects")


@cli.command()
@click.argument('project')
@click.option('--prefs', default='./.hoardwick-preferences.json', help='Preferences file')
def mark_active(project: str, prefs: str):
    """Mark a project as actively used."""

    prefs_mgr = PreferenceManager(Path(prefs))
    prefs_mgr.add_active_project(project)
    console.print(f"[green]Marked {project} as active[/green]")


@cli.command()
@click.argument('project')
@click.option('--prefs', default='./.hoardwick-preferences.json', help='Preferences file')
def mark_inactive(project: str, prefs: str):
    """Remove project from active list."""

    prefs_mgr = PreferenceManager(Path(prefs))
    prefs_mgr.remove_active_project(project)
    console.print(f"[yellow]Removed {project} from active list[/yellow]")


@cli.command()
@click.argument('action')
@click.argument('reason')
@click.argument('size_gb', type=float)
@click.option('--prefs', default='./.hoardwick-preferences.json', help='Preferences file')
def record(action: str, reason: str, size_gb: float, prefs: str):
    """Record a cleanup decision."""

    prefs_mgr = PreferenceManager(Path(prefs))
    prefs_mgr.record_cleanup(action, reason, size_gb)
    console.print(f"[green]Recorded cleanup: {action}[/green]")


@cli.command()
@click.option('--prefs', default='./.hoardwick-preferences.json', help='Preferences file')
def show(prefs: str):
    """Show current preferences and history."""

    prefs_mgr = PreferenceManager(Path(prefs))

    console.print("[bold blue]Hoardwick Preferences[/bold blue]\n")

    # Active projects
    console.print("[cyan]Active Projects:[/cyan]")
    for proj in prefs_mgr.preferences["known_active_projects"]:
        console.print(f"  • {proj}")
    console.print()

    # Cleanup history
    console.print("[cyan]Cleanup History:[/cyan]")
    for date, actions in prefs_mgr.preferences.get("cleanup_decisions", {}).items():
        console.print(f"\n[yellow]{date}[/yellow]")
        if isinstance(actions, list):
            for action in actions:
                console.print(f"  • {action.get('action', 'N/A')}: {action.get('size_saved_gb', 0):.1f} GB")
                console.print(f"    Reason: {action.get('reason', 'N/A')}")
        else:
            console.print(f"  • {actions.get('action', actions.get('decision', 'N/A'))}: {actions.get('size_saved_gb', 0):.1f} GB")

    # Thresholds
    console.print(f"\n[cyan]Thresholds:[/cyan]")
    console.print(f"  Active: < {prefs_mgr.preferences['user_preferences']['active_project_threshold_days']} days")
    console.print(f"  Stale: > {prefs_mgr.preferences['user_preferences']['stale_project_threshold_days']} days")


if __name__ == '__main__':
    cli()
