import argparse
import sys
import logging
from pathlib import Path
from ..container import ServiceContainer
from ..use_cases.scanner import DirectoryScanner
from ..use_cases.dedupe import DuplicateFinder

def setup_logging(verbose: bool):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

def handle_scan(args):
    """Handler for the 'scan' subcommand."""
    dry_run = not args.execute
    container = ServiceContainer(dry_run=dry_run)
    
    root_path = Path(args.root).resolve()
    print(f"--- Smart File Organizer ---")
    print(f"Mode: {'DRY RUN (Safe)' if dry_run else 'EXECUTE (Live)'}")
    print(f"Target: {root_path}\n")

    scanner = DirectoryScanner(container.fs)
    count = 0
    total_size = 0
    
    try:
        for node in scanner.scan(root_path):
            count += 1
            total_size += node.size
            if args.verbose:
                print(f"[FOUND] {node.path.name} ({node.size} bytes)")
            else:
                print(f"\rScanning... Found {count} files", end="", flush=True)
                
        print(f"\n\nScan Complete.")
        print(f"Total Files: {count}")
        print(f"Total Size: {total_size / (1024*1024):.2f} MB")
        
        if scanner.errors:
            print(f"\n[WARNING] Encountered {len(scanner.errors)} permission errors.")
            
    except KeyboardInterrupt:
        print("\nAborted by user.")

    dry_run = not args.execute
    container = ServiceContainer(dry_run=dry_run)
    root_path = Path(args.root).resolve()
    
    scanner = DirectoryScanner(container.fs)
    count = 0
    for node in scanner.scan(root_path):
        count += 1
        print(f"\rScanning... Found {count} files", end="", flush=True)
    print(f"\nTotal Files: {count}")

def handle_dedupe(args):
    """Handler for the 'dedupe' subcommand."""
    container = ServiceContainer(dry_run=True)
    root_path = Path(args.root).resolve()
    
    print(f"--- Duplicate Detector ---")
    print(f"Target: {root_path}")
    print("Step 1: Scanning directory tree...")
    
    scanner = DirectoryScanner(container.fs)
    all_files = list(scanner.scan(root_path))
    print(f"Found {len(all_files)} files. analyzing...")

    finder = DuplicateFinder(container.hasher)
    duplicates = finder.find_duplicates(all_files)

    print(f"\n--- Results ---")
    if not duplicates:
        print("No duplicates found.")
        return

    total_wasted = 0
    for file_hash, group in duplicates.items():
        wasted_size = group[0].size * (len(group) - 1)
        total_wasted += wasted_size
        
        print(f"\n[Hash: {file_hash[:8]}...] Size: {group[0].size} bytes")
        for node in group:
            print(f"  - {node.path}")

    print(f"\nTotal Wasted Space: {total_wasted / (1024*1024):.2f} MB")
    print(f"Duplicate Groups: {len(duplicates)}")

def main():
    parser = argparse.ArgumentParser(description="Smart File Organizer CLI")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable detailed logging")
    parser.add_argument("--execute", action="store_true", help="DISABLE Dry Run mode")
    
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Scan directory and list statistics")
    scan_parser.add_argument("--root", type=str, default=".", help="Root directory to scan")
    scan_parser.set_defaults(func=handle_scan)

    dedupe_parser = subparsers.add_parser("dedupe", help="Find duplicate files")
    dedupe_parser.add_argument("--root", type=str, default=".", help="Root directory to scan")
    dedupe_parser.set_defaults(func=handle_dedupe)

    args = parser.parse_args()
    setup_logging(args.verbose)
    args.func(args)

if __name__ == "__main__":
    main()