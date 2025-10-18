#!/usr/bin/env python3
"""
Storage scanner for Hoard

wick - Production version.

Features:
- Resumable scanning with checkpoints
- Aggregate patterns (node_modules, .git treated as units)
- Symlink loop detection
- Directory statistics computation
- Lazy hashing (only for duplicates)
"""

import hashlib
import os
import sqlite3
import time
from pathlib import Path
from typing import List, Optional, Set, Tuple
from datetime import datetime

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn

console = Console()

# Aggregate-only patterns (treat as single unit, don't index individual files)
AGGREGATE_PATTERNS = {
    'node_modules': 'npm packages',
    '.git/objects': 'git objects',
    '__pycache__': 'python cache',
    '.next': 'nextjs cache',
    'target': 'rust build',
    'dist': 'build output',
    '.venv': 'python virtualenv',
    'venv': 'python virtualenv',
    'Cache': 'browser cache',
    'cache2': 'browser cache',
    '.cache': 'cache directory',
    '.cargo/registry': 'cargo packages',
    '.npm': 'npm cache',
    '.pyenv': 'python environments',
}

# Skip entirely (don't even aggregate)
SKIP_PATTERNS = {
    '.Trash',
    'System Volume Information',
    '$RECYCLE.BIN',
    '.DS_Store',
}


def init_database(db_path: Path) -> sqlite3.Connection:
    """Initialize database with enhanced schema."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Main files table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT UNIQUE NOT NULL,
            size INTEGER NOT NULL,
            hash TEXT,
            modified INTEGER NOT NULL,
            accessed INTEGER NOT NULL,
            parent_dir TEXT NOT NULL,
            depth INTEGER NOT NULL,
            extension TEXT,
            file_type TEXT,
            is_aggregate BOOLEAN DEFAULT 0,
            aggregate_type TEXT,
            scan_id INTEGER NOT NULL
        )
    """)

    # Indices
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hash ON files(hash) WHERE hash IS NOT NULL")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_parent ON files(parent_dir)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_size ON files(size DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scan ON files(scan_id)")

    # Directory statistics
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS directory_stats (
            path TEXT PRIMARY KEY,
            file_count INTEGER,
            total_size INTEGER,
            descendant_count INTEGER,
            oldest_access INTEGER,
            pattern TEXT,
            scan_id INTEGER NOT NULL
        )
    """)

    # Scan metadata
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            root_path TEXT NOT NULL,
            label TEXT,
            started INTEGER NOT NULL,
            completed INTEGER,
            files_found INTEGER,
            total_size INTEGER,
            status TEXT DEFAULT 'running'
        )
    """)

    # Scan progress (resumable)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_progress (
            root_path TEXT PRIMARY KEY,
            last_path TEXT,
            files_scanned INTEGER,
            status TEXT,
            started INTEGER,
            updated INTEGER,
            visited_inodes TEXT
        )
    """)

    # Scan areas (for chunked scanning)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_areas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id INTEGER NOT NULL,
            path TEXT NOT NULL,
            display_name TEXT,
            priority INTEGER DEFAULT 2,
            status TEXT DEFAULT 'pending',
            estimated_size INTEGER,
            estimated_files INTEGER,
            actual_files INTEGER,
            actual_size INTEGER,
            started INTEGER,
            completed INTEGER,
            UNIQUE(scan_id, path)
        )
    """)

    conn.commit()
    return conn


def compute_hash(file_path: Path, max_size_mb: int = 100) -> Optional[str]:
    """
    Compute SHA256 hash of file contents.
    Only hash files under max_size_mb to avoid slowdowns.
    """
    try:
        stat = file_path.stat()
        if stat.st_size > max_size_mb * 1024 * 1024:
            return None  # Skip hashing very large files

        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()
    except (PermissionError, OSError) as e:
        return None


def is_aggregate_pattern(path: Path) -> Optional[str]:
    """Check if path matches aggregate pattern. Returns pattern type if match."""
    path_str = str(path)
    for pattern, agg_type in AGGREGATE_PATTERNS.items():
        if pattern in path_str:
            return agg_type
    return None


def should_skip(path: Path) -> bool:
    """Check if path should be skipped entirely."""
    path_str = str(path)
    return any(pattern in path_str for pattern in SKIP_PATTERNS)


def discover_scan_areas(root: Path, max_depth: int = 2) -> List[Tuple[Path, str, int]]:
    """
    Discover logical scan areas within root directory.

    Returns list of (path, display_name, priority) tuples.

    Priority levels:
    - 1 (high): User directories (Documents, projects, etc.)
    - 2 (normal): Config and application data
    - 3 (low): Caches, build artifacts, temp data
    """
    areas = []

    # Priority keywords for classification
    high_priority = {'projects', 'documents', 'desktop', 'downloads', 'pictures', 'music', 'videos'}
    low_priority = {'cache', 'tmp', 'temp', '.npm', '.cargo', '.pyenv', 'build', 'dist', 'target', 'node_modules'}

    try:
        # Get top-level directories
        for item in root.iterdir():
            if not item.is_dir() or item.is_symlink():
                continue

            if should_skip(item):
                continue

            # Check if this should be aggregated entirely
            if is_aggregate_pattern(item):
                # Treat entire aggregate as one area (low priority)
                display_name = f"{item.name}/ (cache/build)"
                areas.append((item, display_name, 3))
                continue

            # Determine priority
            name_lower = item.name.lower()
            priority = 2  # default
            if any(kw in name_lower for kw in high_priority):
                priority = 1
            elif any(kw in name_lower for kw in low_priority):
                priority = 3

            # Check if we should split this into sub-areas (for large directories)
            # For now, treat depth-1 directories as areas
            # Future: could recursively split projects/* into per-project areas
            display_name = f"{item.name}/"
            areas.append((item, display_name, priority))

            # Special case: break down 'projects' into per-project areas
            if name_lower == 'projects' and max_depth >= 2:
                try:
                    for project in item.iterdir():
                        if project.is_dir() and not project.is_symlink() and not should_skip(project):
                            proj_display = f"projects/{project.name}/"
                            areas.append((project, proj_display, 1))
                except (PermissionError, OSError):
                    pass

    except (PermissionError, OSError):
        # If can't read root, treat entire root as one area
        areas.append((root, str(root), 2))

    # Sort by priority then name
    areas.sort(key=lambda x: (x[2], x[1]))

    return areas


class ResumableScanner:
    """Scanner with checkpoint support and loop detection."""

    def __init__(self, conn: sqlite3.Connection, scan_id: int, checkpoint_every: int = 1000):
        self.conn = conn
        self.scan_id = scan_id
        self.checkpoint_every = checkpoint_every
        self.visited_inodes: Set[int] = set()
        self.files_scanned = 0
        self.files_skipped = 0
        self.aggregates_found = 0
        self.dir_stats = {}

    def load_checkpoint(self, root: Path) -> Optional[str]:
        """Load last checkpoint for resuming."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT last_path, files_scanned, visited_inodes
            FROM scan_progress
            WHERE root_path = ? AND status = 'running'
        """, (str(root),))

        row = cursor.fetchone()
        if row:
            last_path, files_scanned, visited_inodes_str = row
            self.files_scanned = files_scanned
            if visited_inodes_str:
                self.visited_inodes = set(map(int, visited_inodes_str.split(',')))
            console.print(f"[yellow]Resuming from: {last_path}[/yellow]")
            return last_path
        return None

    def save_checkpoint(self, root: Path, current_path: Path):
        """Save current progress."""
        cursor = self.conn.cursor()
        visited_str = ','.join(map(str, list(self.visited_inodes)[:1000]))  # Limit size

        cursor.execute("""
            INSERT OR REPLACE INTO scan_progress
            (root_path, last_path, files_scanned, status, started, updated, visited_inodes)
            VALUES (?, ?, ?, 'running', ?, ?, ?)
        """, (str(root), str(current_path), self.files_scanned,
              int(time.time()), int(time.time()), visited_str))

        self.conn.commit()

    def mark_complete(self, root: Path):
        """Mark scan as complete."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE scan_progress
            SET status = 'complete', updated = ?
            WHERE root_path = ?
        """, (int(time.time()), str(root)))
        self.conn.commit()

    def check_symlink_loop(self, path: Path) -> bool:
        """Detect symlink loops using inodes."""
        try:
            stat = path.stat(follow_symlinks=False)
            inode = stat.st_ino

            if inode in self.visited_inodes:
                console.print(f"[yellow]Symlink loop detected: {path}[/yellow]")
                return True

            self.visited_inodes.add(inode)
            return False
        except (OSError, AttributeError):
            return False

    def get_depth(self, path: Path, root: Path) -> int:
        """Calculate directory depth from root."""
        try:
            return len(path.relative_to(root).parts)
        except ValueError:
            return 0

    def aggregate_directory(self, dir_path: Path, agg_type: str) -> Tuple[int, int]:
        """
        Aggregate a directory (treat as single unit).
        Returns: (total_size, file_count)
        """
        total_size = 0
        file_count = 0

        try:
            for entry in dir_path.rglob('*'):
                if entry.is_file():
                    try:
                        total_size += entry.stat().st_size
                        file_count += 1
                    except (OSError, PermissionError):
                        pass
        except (OSError, PermissionError):
            pass

        return total_size, file_count

    def save_file(self, path: Path, root: Path, stat_info: os.stat_result,
                  file_hash: Optional[str] = None, is_aggregate: bool = False,
                  agg_type: Optional[str] = None):
        """Save file metadata to database."""
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO files
            (path, size, hash, modified, accessed, parent_dir, depth, extension,
             file_type, is_aggregate, aggregate_type, scan_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(path),
            stat_info.st_size,
            file_hash,
            int(stat_info.st_mtime),
            int(stat_info.st_atime),
            str(path.parent),
            self.get_depth(path, root),
            path.suffix.lower() if not is_aggregate else None,
            'aggregate' if is_aggregate else 'file',
            is_aggregate,
            agg_type,
            self.scan_id
        ))

    def compute_dir_stats(self, dir_path: Path):
        """Compute and save directory statistics."""
        cursor = self.conn.cursor()

        # Query child files
        cursor.execute("""
            SELECT COUNT(*), SUM(size), MIN(accessed)
            FROM files
            WHERE parent_dir = ? AND scan_id = ?
        """, (str(dir_path), self.scan_id))

        row = cursor.fetchone()
        if row and row[0]:
            file_count, total_size, oldest_access = row

            # Detect pattern
            dir_name = dir_path.name
            pattern = None
            for pat in AGGREGATE_PATTERNS.keys():
                if pat in dir_name:
                    pattern = pat
                    break

            cursor.execute("""
                INSERT OR REPLACE INTO directory_stats
                (path, file_count, total_size, descendant_count, oldest_access, pattern, scan_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (str(dir_path), file_count, total_size or 0, file_count,
                  oldest_access, pattern, self.scan_id))

    def scan(self, root: Path, exclude_patterns: List[str], resume: bool = True, hash_files: bool = False) -> Tuple[int, int, int]:
        """
        Scan directory with all production features.

        Args:
            root: Root directory to scan
            exclude_patterns: Patterns to exclude
            resume: Whether to resume from checkpoint
            hash_files: Whether to compute file hashes (slower, for duplicate detection)

        Returns: (files_scanned, files_skipped, aggregates_found)
        """
        # Load checkpoint if resuming
        resume_from = self.load_checkpoint(root) if resume else None
        should_skip_until_resume = resume_from is not None

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress:

            task = progress.add_task(f"Scanning {root}...", total=None)

            for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
                current_dir = Path(dirpath)

                # Check if we should skip until resume point
                if should_skip_until_resume:
                    if str(current_dir) == resume_from or current_dir.is_relative_to(Path(resume_from)):
                        should_skip_until_resume = False
                    else:
                        continue

                # Skip patterns
                if should_skip(current_dir):
                    dirnames.clear()
                    continue

                # Check for symlink loops
                if self.check_symlink_loop(current_dir):
                    dirnames.clear()
                    continue

                # Check if this directory should be aggregated
                agg_type = is_aggregate_pattern(current_dir)
                if agg_type:
                    # Aggregate this entire directory
                    total_size, file_count = self.aggregate_directory(current_dir, agg_type)

                    try:
                        stat_info = current_dir.stat()
                        self.save_file(current_dir, root, stat_info,
                                     is_aggregate=True, agg_type=agg_type)

                        # Update size in database
                        cursor = self.conn.cursor()
                        cursor.execute("UPDATE files SET size = ? WHERE path = ?",
                                     (total_size, str(current_dir)))

                        self.aggregates_found += 1
                        progress.update(task, description=
                            f"Aggregated {agg_type}: {current_dir.name} ({total_size / 1024 / 1024:.1f} MB, {file_count} files)")
                    except (OSError, PermissionError):
                        pass

                    # Don't descend into aggregated directories
                    dirnames.clear()
                    continue

                # Filter subdirectories
                dirnames[:] = [
                    d for d in dirnames
                    if not should_skip(current_dir / d)
                    and not any(pat in d for pat in exclude_patterns)
                ]

                # Process files
                for filename in filenames:
                    file_path = current_dir / filename

                    # Skip patterns
                    if should_skip(file_path):
                        self.files_skipped += 1
                        continue

                    # Skip symlinks
                    if file_path.is_symlink():
                        self.files_skipped += 1
                        continue

                    try:
                        stat_info = file_path.stat()

                        # Optional hashing (only if --hash-files flag set)
                        # By default, skip hashing for speed - hash later only for size-duplicates
                        file_hash = None
                        if hash_files and stat_info.st_size < 100 * 1024 * 1024:  # < 100MB
                            file_hash = compute_hash(file_path)

                        self.save_file(file_path, root, stat_info, file_hash)

                        self.files_scanned += 1

                        # Checkpoint
                        if self.files_scanned % self.checkpoint_every == 0:
                            self.save_checkpoint(root, file_path)
                            progress.update(task, description=
                                f"Scanned {self.files_scanned} files, {self.aggregates_found} aggregates: {file_path.name}")

                    except (PermissionError, OSError) as e:
                        self.files_skipped += 1

                # Compute directory stats
                self.compute_dir_stats(current_dir)
                self.conn.commit()

        self.mark_complete(root)
        return self.files_scanned, self.files_skipped, self.aggregates_found


@click.command()
@click.argument('paths', nargs=-1, type=click.Path(exists=True), required=True)
@click.option('--database', default='./generated/hoardwick.db', help='Database file path')
@click.option('--label', help='Label for this scan')
@click.option('--exclude', multiple=True, help='Additional exclusion patterns')
@click.option('--no-resume', is_flag=True, help='Start fresh (ignore checkpoints)')
@click.option('--checkpoint-every', default=1000, help='Checkpoint frequency (files)')
@click.option('--hash-files', is_flag=True, help='Compute file hashes during scan (slower)')
def main(paths: tuple[str], database: str, label: Optional[str],
         exclude: tuple[str], no_resume: bool, checkpoint_every: int, hash_files: bool):
    """Scan storage locations with resumable, production-ready scanner."""

    console.print("[bold blue]Hoardwick Storage Scanner v2[/bold blue]\n")

    # Initialize database
    db_path = Path(database)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = init_database(db_path)

    total_scanned = 0
    total_skipped = 0
    total_aggregates = 0

    for path_str in paths:
        root = Path(path_str).resolve()
        console.print(f"[cyan]Scanning:[/cyan] {root}\n")

        # Discover scan areas
        console.print("[cyan]Discovering scan areas...[/cyan]")
        areas = discover_scan_areas(root)
        console.print(f"[green]Found {len(areas)} areas to scan[/green]\n")

        # Show areas
        for area_path, display_name, priority in areas[:10]:  # Show first 10
            priority_label = {1: "high", 2: "normal", 3: "low"}[priority]
            console.print(f"  {display_name:40s} [{priority_label}]")
        if len(areas) > 10:
            console.print(f"  ... and {len(areas) - 10} more")
        console.print()

        # Create scan record
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO scans (root_path, label, started)
            VALUES (?, ?, ?)
        """, (str(root), label, int(time.time())))
        scan_id = cursor.lastrowid
        conn.commit()

        # Record scan areas
        for area_path, display_name, priority in areas:
            cursor.execute("""
                INSERT INTO scan_areas (scan_id, path, display_name, priority, status)
                VALUES (?, ?, ?, ?, 'pending')
            """, (scan_id, str(area_path), display_name, priority))
        conn.commit()

        # Scan with production features
        scanner = ResumableScanner(conn, scan_id, checkpoint_every)
        scanned, skipped, aggregates = scanner.scan(
            root,
            list(exclude),
            resume=not no_resume,
            hash_files=hash_files
        )

        total_scanned += scanned
        total_skipped += skipped
        total_aggregates += aggregates

        # Update scan record
        cursor.execute("""
            UPDATE scans
            SET completed = ?, files_found = ?,
                total_size = (SELECT SUM(size) FROM files WHERE scan_id = ?),
                status = 'complete'
            WHERE id = ?
        """, (int(time.time()), scanned, scan_id, scan_id))
        conn.commit()

    conn.close()

    # Summary
    console.print(f"\n[bold green]Scan Complete[/bold green]")
    console.print(f"Files indexed: {total_scanned:,}")
    console.print(f"Aggregated directories: {total_aggregates:,}")
    console.print(f"Skipped: {total_skipped:,}")
    console.print(f"Database: {db_path}")


if __name__ == '__main__':
    main()
