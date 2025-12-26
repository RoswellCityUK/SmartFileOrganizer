import argparse
import sys
import logging
from pathlib import Path
from ..container import ServiceContainer
from ..use_cases.scanner import DirectoryScanner

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

def main():
    parser = argparse.ArgumentParser(description="Smart File Organizer CLI")
    
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable detailed logging")
    parser.add_argument("--execute", action="store_true", help="DISABLE Dry Run mode (Write to disk)")
    
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Scan directory and list statistics")
    scan_parser.add_argument("--root", type=str, default=".", help="Root directory to scan")
    scan_parser.set_defaults(func=handle_scan)

    args = parser.parse_args()
    
    setup_logging(args.verbose)
    args.func(args)

if __name__ == "__main__":
    main()