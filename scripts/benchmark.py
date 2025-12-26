import time
import shutil
import random
import string
import platform
import matplotlib.pyplot as plt
from pathlib import Path
from concurrent.futures import Executor
from unittest.mock import patch
from smart_file_organizer.container import ServiceContainer
from smart_file_organizer.use_cases.scanner import DirectoryScanner
from smart_file_organizer.use_cases.dedupe import DuplicateFinder

# --- Configuration ---
ROOT_DIR = Path("./benchmark_data")
FILE_COUNT = 5000
FILE_SIZE_KB = 50


def get_system_info():
    """Retrieves basic system information for the graph."""
    try:
        info = f"OS: {platform.system()} {platform.release()}"
        info += f"\nMachine: {platform.machine()}"
        info += f"\nProcessor: {platform.processor() or 'Unknown'}"
        info += f"\nPython: {platform.python_version()}"
        return info
    except Exception:
        return "System Info Unavailable"


def generate_dummy_data():
    if ROOT_DIR.exists():
        shutil.rmtree(ROOT_DIR)
    ROOT_DIR.mkdir()

    print(f"Generating {FILE_COUNT} files...")
    content = b"A" * (FILE_SIZE_KB * 1024)

    # Create some duplicates
    for i in range(FILE_COUNT):
        p = ROOT_DIR / f"file_{i}.dat"
        # Make every 10th file a duplicate of the previous one
        if i > 0 and i % 10 == 0:
            shutil.copy(ROOT_DIR / f"file_{i-1}.dat", p)
        else:
            # Add random suffix to ensure uniqueness otherwise
            suffix = "".join(random.choices(string.ascii_letters, k=10)).encode()
            p.write_bytes(content + suffix)


def run_dedupe(parallel: bool) -> float:
    container = ServiceContainer(dry_run=True)
    scanner = DirectoryScanner(container.fs)
    files = list(scanner.scan(ROOT_DIR))

    start = time.time()

    if parallel:
        # Run normally (uses ProcessPoolExecutor)
        finder = DuplicateFinder(container.hasher)
        finder.find_duplicates(files)
    else:
        # Force serial execution by patching ProcessPoolExecutor
        class SerialExecutor(Executor):
            def map(self, fn, *iterables, **kwargs):
                return map(fn, *iterables)

            def shutdown(self, wait=True):
                pass

        with patch(
            "smart_file_organizer.use_cases.dedupe.ProcessPoolExecutor",
            return_value=SerialExecutor(),
        ):
            finder = DuplicateFinder(container.hasher)
            finder.find_duplicates(files)

    return time.time() - start


def plot_results(serial_time, parallel_time):
    labels = ["Serial", "Parallel"]
    times = [serial_time, parallel_time]

    sys_info = get_system_info()

    plt.figure(figsize=(10, 6))
    bars = plt.bar(labels, times, color=["#ff9999", "#66b3ff"])

    plt.ylabel("Time (seconds)")
    plt.title(
        f"Deduplication Performance ({FILE_COUNT} files @ {FILE_SIZE_KB}KB)",
        fontsize=14,
    )

    # Add text labels on top of bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            yval + 0.05,
            f"{yval:.2f}s",
            ha="center",
            va="bottom",
            fontweight="bold",
        )

    # Add system info box
    plt.figtext(
        0.15,
        0.02,
        sys_info,
        fontsize=9,
        bbox={"facecolor": "orange", "alpha": 0.2, "pad": 5},
    )

    # Adjust layout to make room for text
    plt.subplots_adjust(bottom=0.2)

    plt.savefig("benchmark_result.png")
    print("Graph saved to benchmark_result.png")


def main():
    try:
        generate_dummy_data()

        print("Running Serial Benchmark...")
        t_serial = run_dedupe(parallel=False)
        print(f"Serial Time: {t_serial:.2f}s")

        print("Running Parallel Benchmark...")
        t_parallel = run_dedupe(parallel=True)
        print(f"Parallel Time: {t_parallel:.2f}s")

        speedup = t_serial / t_parallel
        print(f"Speedup: {speedup:.2f}x")

        plot_results(t_serial, t_parallel)

    finally:
        if ROOT_DIR.exists():
            shutil.rmtree(ROOT_DIR)


if __name__ == "__main__":
    main()
