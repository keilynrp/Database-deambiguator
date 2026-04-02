from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.authority.benchmark import DEFAULT_AUTHOR_NIL_BENCHMARK_PATH, evaluate_author_nil_benchmark, load_author_nil_benchmark


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the offline UKIP author/NIL benchmark.")
    parser.add_argument(
        "--dataset",
        default=str(DEFAULT_AUTHOR_NIL_BENCHMARK_PATH),
        help="Path to the benchmark dataset JSON file.",
    )
    args = parser.parse_args()

    dataset = load_author_nil_benchmark(args.dataset)
    results = evaluate_author_nil_benchmark(dataset)
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
