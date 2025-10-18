# Hoardwick

**Data management and cleanup system for cross-platform storage**

## Purpose

Analyse storage across WSL, Windows filesystem, and shared drives to identify redundancy, suggest cleanup, and enable intelligent reorganisation.

## Problem

Chris has data scattered across:
- WSL filesystem (`/home/chris/`)
- Windows filesystem (`/mnt/c/Users/Chris/`)
- Shared network drives
- Multiple backup locations

Without visibility into duplication, outdated content, or organisational opportunities, this creates:
- Wasted storage
- Difficulty finding files
- Risk of losing important data
- Confusion about canonical locations

## Solution

Hoardwick provides:
1. Storage scanning and indexing across all locations
2. Duplication detection and analysis
3. Content age and access pattern tracking
4. Cleanup recommendations based on configurable rules
5. Reorganisation suggestions based on usage patterns
6. Safe preview-before-action operations
