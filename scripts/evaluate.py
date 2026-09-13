"""Prepare, verify or run the frozen Phase 7 three-arm evaluation."""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.eval.harness import check, live_evaluate, prepare


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--live", action="store_true")
    args = parser.parse_args()
    result = prepare() if args.prepare else check() if args.check else live_evaluate()
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
