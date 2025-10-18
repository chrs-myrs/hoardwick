#!/usr/bin/env python3
"""
Cleanup utility for Hoardwick.

Built-in operations for common cleanup tasks:
- Docker system pruning
- WSL disk compaction
- Cache clearing (npm, pip, cargo)
- Execution of markdown action plans
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm

console = Console()


def run_command(cmd: List[str], description: str, dry_run: bool = False) -> bool:
    """Run a system command with error handling."""
    if dry_run:
        console.print(f"[yellow]DRY RUN:[/yellow] {description}")
        console.print(f"  Command: {' '.join(cmd)}")
        return True

    console.print(f"[cyan]{description}...[/cyan]")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            console.print(f"[green]✓ {description} complete[/green]")
            if result.stdout:
                console.print(result.stdout)
            return True
        else:
            console.print(f"[red]✗ {description} failed[/red]")
            if result.stderr:
                console.print(f"[red]{result.stderr}[/red]")
            return False
    except FileNotFoundError:
        console.print(f"[red]✗ Command not found: {cmd[0]}[/red]")
        return False
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        return False


@click.group()
def cli():
    """Hoardwick cleanup utilities."""
    pass


@cli.command()
@click.option('--dry-run', is_flag=True, help='Show what would be done')
@click.option('--all', 'prune_all', is_flag=True, help='Remove all unused images, not just dangling')
@click.option('--volumes', is_flag=True, help='Also prune unused volumes')
def docker_prune(dry_run: bool, prune_all: bool, volumes: bool):
    """Clean up Docker images, containers, and optionally volumes."""

    console.print("[bold blue]Docker Cleanup[/bold blue]\n")

    # Check Docker is available
    try:
        result = subprocess.run(['docker', 'system', 'df'], capture_output=True, text=True)
        console.print("[cyan]Current Docker disk usage:[/cyan]")
        console.print(result.stdout)
    except FileNotFoundError:
        console.print("[red]Docker not found. Is Docker installed and running?[/red]")
        return

    # Build prune command
    cmd = ['docker', 'system', 'prune', '-f']
    if prune_all:
        cmd.append('-a')
    if volumes:
        cmd.append('--volumes')

    description = "Pruning Docker system"
    if prune_all:
        description += " (including all unused images)"
    if volumes:
        description += " (including volumes)"

    if not dry_run:
        if not Confirm.ask("\n[yellow]Proceed with Docker cleanup?[/yellow]"):
            console.print("[yellow]Cancelled[/yellow]")
            return

    run_command(cmd, description, dry_run)

    # Show new usage
    if not dry_run:
        result = subprocess.run(['docker', 'system', 'df'], capture_output=True, text=True)
        console.print("\n[cyan]Updated Docker disk usage:[/cyan]")
        console.print(result.stdout)


@cli.command()
@click.option('--dry-run', is_flag=True, help='Show what would be done')
def wsl_compact(dry_run: bool):
    """Compact WSL virtual disk to reclaim space."""

    console.print("[bold blue]WSL Disk Compaction[/bold blue]\n")

    # This requires Windows wsl.exe command
    if not Path('/mnt/c/Windows/System32/wsl.exe').exists():
        console.print("[red]WSL not detected. This command only works in WSL environment.[/red]")
        return

    console.print("[yellow]Note: WSL must be shutdown for compaction[/yellow]")
    console.print("[yellow]This will close all WSL instances![/yellow]\n")

    if dry_run:
        console.print("[yellow]DRY RUN: Would compact WSL disk[/yellow]")
        return

    if not Confirm.ask("[yellow]Shutdown WSL and compact disk?[/yellow]"):
        console.print("[yellow]Cancelled[/yellow]")
        return

    # Shutdown WSL
    console.print("[cyan]Shutting down WSL...[/cyan]")
    subprocess.run(['wsl.exe', '--shutdown'])

    # Instructions for manual compaction (requires running from Windows)
    console.print("\n[yellow]Manual steps required:[/yellow]")
    console.print("1. Open PowerShell as Administrator (from Windows)")
    console.print("2. Run: wsl --shutdown")
    console.print("3. Navigate to: %LOCALAPPDATA%\\Packages\\*Ubuntu*\\LocalState")
    console.print("4. Run: optimize-vhd -Path .\\ext4.vhdx -Mode full")
    console.print("\nAlternatively, use diskpart:")
    console.print("  select vdisk file=\"%LOCALAPPDATA%\\Packages\\*Ubuntu*\\LocalState\\ext4.vhdx\"")
    console.print("  compact vdisk")


@cli.command()
@click.option('--prune-only', is_flag=True, help='Prune unreachable only (keeps used packages)')
@click.option('--dry-run', is_flag=True, help='Show what would be done')
def uv_cache(prune_only: bool, dry_run: bool):
    """Clean UV Python package cache."""

    console.print("[bold blue]UV Cache Cleanup[/bold blue]\n")

    # Check UV is available
    try:
        result = subprocess.run(['uv', 'cache', 'dir'], capture_output=True, text=True)
        cache_dir = result.stdout.strip()
        console.print(f"[cyan]UV cache location:[/cyan] {cache_dir}")

        # Try to get size (may be slow/timeout on large caches)
        console.print("[cyan]Checking cache size...[/cyan]")
        try:
            size_result = subprocess.run(
                ['du', '-sh', cache_dir],
                capture_output=True,
                text=True,
                timeout=30
            )
            if size_result.returncode == 0:
                size = size_result.stdout.split()[0]
                console.print(f"[cyan]Current size:[/cyan] {size}\n")
            else:
                console.print("[yellow]Could not determine size (cache may be very large)[/yellow]\n")
        except subprocess.TimeoutExpired:
            console.print("[yellow]Size check timed out (cache is very large)[/yellow]\n")

    except FileNotFoundError:
        console.print("[red]UV not found. Is UV installed?[/red]")
        console.print("Install with: curl -LsSf https://astral.sh/uv/install.sh | sh")
        return
    except Exception as e:
        console.print(f"[red]Error checking UV cache: {e}[/red]")
        return

    # Build command
    cmd = ['uv', 'cache', 'prune' if prune_only else 'clean']
    operation = "Pruning unreachable packages" if prune_only else "Clearing entire cache"

    if prune_only:
        console.print("[cyan]Prune mode: Only unreachable packages will be removed[/cyan]")
        console.print("[cyan]Active project dependencies will be preserved[/cyan]\n")
    else:
        console.print("[yellow]Clean mode: ALL cached packages will be removed[/yellow]")
        console.print("[yellow]Packages will re-download on next use[/yellow]\n")

    if dry_run:
        console.print(f"[yellow]DRY RUN:[/yellow] {operation}")
        console.print(f"  Command: {' '.join(cmd)}")
        return

    if not Confirm.ask(f"[yellow]Proceed with UV cache {'prune' if prune_only else 'clean'}?[/yellow]"):
        console.print("[yellow]Cancelled[/yellow]")
        return

    # Run cleanup
    console.print(f"[cyan]{operation}...[/cyan]")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            console.print(f"[green]✓ UV cache {'pruned' if prune_only else 'cleaned'}[/green]")
            # UV outputs stats directly
            if result.stderr:
                console.print(result.stderr)
            if result.stdout:
                console.print(result.stdout)
        else:
            console.print(f"[red]✗ Operation failed[/red]")
            if result.stderr:
                console.print(f"[red]{result.stderr}[/red]")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


@cli.command()
@click.option('--type', type=click.Choice(['npm', 'pip', 'cargo', 'all']), default='all')
@click.option('--dry-run', is_flag=True, help='Show what would be done')
def clear_cache(type: str, dry_run: bool):
    """Clear package manager caches."""

    console.print(f"[bold blue]Cache Cleanup: {type}[/bold blue]\n")

    caches = []

    if type in ('npm', 'all'):
        caches.append((['npm', 'cache', 'clean', '--force'], 'npm cache'))

    if type in ('pip', 'all'):
        caches.append((['pip3', 'cache', 'purge'], 'pip cache'))

    if type in ('cargo', 'all'):
        # Cargo doesn't have built-in cache clean, use manual approach
        cargo_cache = Path.home() / '.cargo' / 'registry'
        if cargo_cache.exists():
            if dry_run:
                console.print(f"[yellow]Would remove: {cargo_cache}[/yellow]")
            else:
                if Confirm.ask(f"[yellow]Remove {cargo_cache}?[/yellow]"):
                    import shutil
                    shutil.rmtree(cargo_cache)
                    console.print("[green]✓ Cargo cache cleared[/green]")

    for cmd, name in caches:
        if not dry_run:
            if not Confirm.ask(f"\n[yellow]Clear {name}?[/yellow]"):
                console.print(f"[yellow]Skipped {name}[/yellow]")
                continue

        run_command(cmd, f"Clearing {name}", dry_run)


@cli.command()
@click.argument('patterns', nargs=-1)
@click.option('--root', default='.', help='Root directory to search from')
@click.option('--dry-run', is_flag=True, help='Show what would be found')
def clear_build_artifacts(patterns: tuple[str], root: str, dry_run: bool):
    """Clear build artifacts matching patterns."""

    default_patterns = ['target', 'dist', 'build', '.next', 'out']
    patterns_to_use = patterns if patterns else default_patterns

    console.print(f"[bold blue]Build Artifact Cleanup[/bold blue]\n")
    console.print(f"Root: {root}")
    console.print(f"Patterns: {', '.join(patterns_to_use)}\n")

    root_path = Path(root).resolve()
    found_dirs = []

    for pattern in patterns_to_use:
        console.print(f"[cyan]Searching for: {pattern}[/cyan]")
        for match in root_path.rglob(pattern):
            if match.is_dir() and not match.is_symlink():
                # Check if it's really a build directory (has parent project)
                parent = match.parent
                if any((parent / marker).exists() for marker in
                      ['package.json', 'Cargo.toml', 'go.mod', 'pom.xml']):
                    found_dirs.append(match)
                    console.print(f"  Found: {match}")

    if not found_dirs:
        console.print("[green]No build artifacts found[/green]")
        return

    console.print(f"\n[yellow]Found {len(found_dirs)} build directories[/yellow]")

    if dry_run:
        console.print("[yellow]DRY RUN: No files deleted[/yellow]")
        return

    if not Confirm.ask(f"[yellow]Delete {len(found_dirs)} directories?[/yellow]"):
        console.print("[yellow]Cancelled[/yellow]")
        return

    import shutil
    deleted_count = 0
    for dir_path in found_dirs:
        try:
            shutil.rmtree(dir_path)
            console.print(f"[green]✓ Deleted: {dir_path}[/green]")
            deleted_count += 1
        except Exception as e:
            console.print(f"[red]✗ Failed to delete {dir_path}: {e}[/red]")

    console.print(f"\n[green]Deleted {deleted_count} directories[/green]")


@cli.command()
@click.argument('markdown_file', type=click.Path(exists=True))
@click.option('--section', help='Only execute specific section')
@click.option('--dry-run', is_flag=True, help='Show what would be done')
def execute_plan(markdown_file: str, section: Optional[str], dry_run: bool):
    """Execute cleanup plan from markdown file."""

    console.print(f"[bold blue]Executing Cleanup Plan[/bold blue]\n")
    console.print(f"File: {markdown_file}\n")

    # Read markdown file
    md_path = Path(markdown_file)
    content = md_path.read_text()

    # Parse sections (simple markdown parser)
    current_section = None
    actions = []

    for line in content.split('\n'):
        if line.startswith('##'):
            current_section = line.lstrip('#').strip()
        elif line.strip().startswith('- Action:') or line.strip().startswith('Action:'):
            action_text = line.split('Action:')[1].strip()
            if section is None or current_section == section:
                actions.append((current_section, action_text))

    if not actions:
        console.print("[yellow]No actions found in markdown file[/yellow]")
        return

    console.print(f"[cyan]Found {len(actions)} actions[/cyan]\n")

    table = Table(show_header=True)
    table.add_column("Section")
    table.add_column("Action")

    for sect, action in actions:
        table.add_row(sect or "Unknown", action)

    console.print(table)

    if dry_run:
        console.print("\n[yellow]DRY RUN: No actions executed[/yellow]")
        return

    console.print("\n[yellow]Action execution from markdown is manual.[/yellow]")
    console.print("[yellow]Review the actions above and execute them manually.[/yellow]")
    console.print("[yellow]Future versions will support automated execution.[/yellow]")


if __name__ == '__main__':
    cli()
