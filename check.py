#!/usr/bin/env python3
"""
Verify a collection of fair-division counterexamples.

Usage:
    python check.py <path-to-counterexamples.py>

The given file must expose a module-level list:
    COUNTEREXAMPLES: Sequence[Counterexample]

Each counterexample is verified and any errors are printed to stderr.
Exits with code 0 if all counterexamples pass, 1 otherwise.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from collections.abc import Sequence
from pathlib import Path

from counterexample import Counterexample


def load_counterexamples(path: Path) -> Sequence[Counterexample]:
    spec = importlib.util.spec_from_file_location("_cex_module", path)
    if spec is None or spec.loader is None:
        print(f"error: cannot load '{path}'", file=sys.stderr)
        sys.exit(1)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    cexs = getattr(module, "COUNTEREXAMPLES", None)
    if cexs is None:
        print(f"error: '{path}' has no module-level COUNTEREXAMPLES", file=sys.stderr)
        sys.exit(1)
    if not isinstance(cexs, list):
        print(f"error: COUNTEREXAMPLES must be a list, got {type(cexs).__name__}",
              file=sys.stderr)
        sys.exit(1)
    return cexs


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify fair-division counterexamples.")
    parser.add_argument("file", type=Path,
                        help="Python file exposing a COUNTEREXAMPLES list")
    args = parser.parse_args()

    cexs = load_counterexamples(args.file)

    failed = 0
    for cex in cexs:
        errors = cex.verify()
        if errors:
            failed += 1
            print(f"FAIL [{cex.id}] ({cex.satisfies} doesn't imply {cex.violates}):",
                  file=sys.stderr)
            for err in errors:
                print(f"  - {err}", file=sys.stderr)

    total = len(cexs)
    passed = total - failed
    print(f"{passed}/{total} counterexamples passed.", file=sys.stderr)
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
