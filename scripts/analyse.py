#!/usr/bin/env python3
"""
Storage analyser for Hoardwick.

Analyses scanned storage to identify duplicates, stale files, and storage waste.
"""

import json
import sqlite3
import time
from pathlib import Path
from typing import List, Dict, Any

import click
from rich.console import Console
from rich.table import Table

console = Console()


def format_size(size_bytes: int) -> str:
    """Format size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def get_duplicates(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    """Find duplicate files (same hash), excluding aggregated directories."""
    cursor = conn.cursor()

    cursor.execute("""
        SELECT hash, COUNT(*) as count, SUM(size) as total_size
        FROM files
        WHERE hash IS NOT NULL AND is_aggregate = 0
        GROUP BY hash
        HAVING count > 1
        ORDER BY total_size DESC
    """)

    duplicates = []
    for hash_val, count, total_size in cursor.fetchall():
        # Get all files with this hash
        cursor.execute("SELECT path, size FROM files WHERE hash = ?", (hash_val,))
        files = [{"path": path, "size": size} for path, size in cursor.fetchall()]

        duplicates.append({
            "hash": hash_val,
            "count": count,
            "total_size": total_size,
            "waste": total_size - files[0]["size"],  # Size that could be saved
            "files": files
        })

    return duplicates


def get_stale_files(conn: sqlite3.Connection, stale_days: int) -> List[Dict[str, Any]]:
    """Find files not accessed in specified days, excluding aggregated directories."""
    cursor = conn.cursor()
    cutoff_time = time.time() - (stale_days * 86400)

    cursor.execute("""
        SELECT path, size, accessed
        FROM files
        WHERE accessed < ? AND is_aggregate = 0
        ORDER BY size DESC
    """, (cutoff_time,))

    stale_files = []
    for path, size, accessed in cursor.fetchall():
        days_old = (time.time() - accessed) / 86400
        stale_files.append({
            "path": path,
            "size": size,
            "days_since_access": int(days_old)
        })

    return stale_files


def get_summary(conn: sqlite3.Connection) -> Dict[str, Any]:
    """Get overall storage summary."""
    cursor = conn.cursor()

    # Total files and size (including aggregated)
    cursor.execute("SELECT COUNT(*), SUM(size) FROM files")
    total_files, total_size = cursor.fetchone()

    # Aggregated directories
    cursor.execute("SELECT COUNT(*), SUM(size) FROM files WHERE is_aggregate = 1")
    aggregate_count, aggregate_size = cursor.fetchone()

    # Duplicates
    duplicates = get_duplicates(conn)
    duplicate_count = sum(d["count"] for d in duplicates)
    duplicate_waste = sum(d["waste"] for d in duplicates)

    # File type distribution (by extension, excluding aggregates)
    cursor.execute("""
        SELECT extension, COUNT(*) as count, SUM(size) as total_size
        FROM files
        WHERE is_aggregate = 0 AND extension IS NOT NULL
        GROUP BY extension
        ORDER BY total_size DESC
        LIMIT 10
    """)

    top_extensions = [
        {"extension": ext, "count": count, "size": size}
        for ext, count, size in cursor.fetchall()
    ]

    return {
        "total_files": total_files or 0,
        "total_size": total_size or 0,
        "aggregate_count": aggregate_count or 0,
        "aggregate_size": aggregate_size or 0,
        "duplicate_files": duplicate_count,
        "duplicate_waste": duplicate_waste,
        "top_extensions": top_extensions
    }


def display_duplicates(duplicates: List[Dict[str, Any]], output_format: str):
    """Display duplicate files report."""
    if output_format == "json":
        print(json.dumps(duplicates, indent=2))
        return

    if not duplicates:
        console.print("[green]No duplicates found![/green]")
        return

    console.print(f"\n[bold red]Found {len(duplicates)} duplicate file groups[/bold red]\n")

    total_waste = sum(d["waste"] for d in duplicates)
    console.print(f"[yellow]Potential space savings: {format_size(total_waste)}[/yellow]\n")

    for i, dup in enumerate(duplicates[:10], 1):  # Show top 10
        console.print(f"[bold cyan]Group {i}:[/bold cyan] {dup['count']} copies, {format_size(dup['waste'])} waste")
        for file in dup["files"][:5]:  # Show first 5 files
            console.print(f"  {file['path']}")
        if len(dup["files"]) > 5:
            console.print(f"  ... and {len(dup['files']) - 5} more")
        console.print()


def display_stale(stale_files: List[Dict[str, Any]], output_format: str, stale_days: int):
    """Display stale files report."""
    if output_format == "json":
        print(json.dumps(stale_files, indent=2))
        return

    if not stale_files:
        console.print(f"[green]No files stale (>{stale_days} days)![/green]")
        return

    console.print(f"\n[bold yellow]Found {len(stale_files)} stale files (not accessed in {stale_days}+ days)[/bold yellow]\n")

    total_size = sum(f["size"] for f in stale_files)
    console.print(f"[yellow]Total size: {format_size(total_size)}[/yellow]\n")

    table = Table(show_header=True)
    table.add_column("File", style="cyan")
    table.add_column("Size", justify="right")
    table.add_column("Days", justify="right", style="yellow")

    for file in stale_files[:20]:  # Show top 20
        table.add_row(
            file["path"],
            format_size(file["size"]),
            str(file["days_since_access"])
        )

    console.print(table)

    if len(stale_files) > 20:
        console.print(f"\n... and {len(stale_files) - 20} more")


def display_summary(summary: Dict[str, Any], output_format: str):
    """Display storage summary."""
    if output_format == "json":
        print(json.dumps(summary, indent=2))
        return

    console.print("\n[bold blue]Storage Summary[/bold blue]\n")

    console.print(f"[cyan]Total entries:[/cyan] {summary['total_files']:,}")
    console.print(f"[cyan]Total size:[/cyan] {format_size(summary['total_size'])}")
    console.print(f"[magenta]Aggregated directories:[/magenta] {summary['aggregate_count']:,} ({format_size(summary['aggregate_size'])})")
    console.print(f"[yellow]Duplicate files:[/yellow] {summary['duplicate_files']:,}")
    console.print(f"[red]Duplicate waste:[/red] {format_size(summary['duplicate_waste'])}\n")

    if summary['top_extensions']:
        console.print("[bold]Top file types by size:[/bold]\n")

        table = Table(show_header=True)
        table.add_column("Extension", style="cyan")
        table.add_column("Files", justify="right")
        table.add_column("Total Size", justify="right")

        for ext in summary['top_extensions']:
            table.add_row(
                ext["extension"],
                f"{ext['count']:,}",
                format_size(ext["size"])
            )

        console.print(table)


@click.command()
@click.option('--database', default='./generated/hoardwick.db', help='Database file path')
@click.option('--report', type=click.Choice(['summary', 'duplicates', 'stale']), default='summary', help='Report type')
@click.option('--output', type=click.Choice(['terminal', 'json', 'csv']), default='terminal', help='Output format')
@click.option('--stale-days', default=365, help='Days threshold for stale files')
def main(database: str, report: str, output: str, stale_days: int):
    """Analyse scanned storage for duplicates and waste."""

    db_path = Path(database)

    if not db_path.exists():
        console.print(f"[red]Error: Database not found at {db_path}[/red]")
        console.print("[yellow]Run scan.py first to create the database.[/yellow]")
        return

    conn = sqlite3.connect(db_path)

    if report == 'duplicates':
        duplicates = get_duplicates(conn)
        display_duplicates(duplicates, output)

    elif report == 'stale':
        stale_files = get_stale_files(conn, stale_days)
        display_stale(stale_files, output, stale_days)

    else:  # summary
        summary = get_summary(conn)
        display_summary(summary, output)

    conn.close()


if __name__ == '__main__':
    main()
