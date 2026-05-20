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
import json
from collections.abc import Mapping, Sequence
from pathlib import Path

from conditions import Conditions, verify_conditions
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


def match_cex(cex_spec: dict[str, object], cex: Counterexample) -> list[str]:
    satisfies, violates = cex_spec['satisfies'], cex_spec['butNot']
    conditions: Conditions =  cex_spec['under']  # type: ignore
    errors = []
    if satisfies != cex.satisfies:
        errors.append(f"cex {cex.id}: mismatched 'satisfies': {satisfies} ≠ {cex.satisfies}")
    if violates != cex.violates:
        errors.append(f"cex {cex.id}: mismatched 'violates': {violates} ≠ {cex.violates}")
    if errors:
        return errors
    else:
        return verify_conditions(cex.instance, conditions)


def match_json_file(fpath: Path, cexs_dict: Mapping[str, Counterexample]) -> int:
    with open(fpath) as fp:
        cexs_spec_list = json.load(fp)['counterexamples']
    cexs_spec_ids = set()
    n_ignored, n_not_found, n_failed, n_matched = 0, 0, 0, 0
    for cex_spec in cexs_spec_list:
        if 'id' not in cex_spec:
            n_ignored += 1
        elif cex_spec['id'] in cexs_spec_ids:
            raise Exception(f"duplicate id {cex_spec['id']} in JSON file")
        else:
            idStr = cex_spec['id']
            cexs_spec_ids.add(idStr)
            cex = cexs_dict.get(idStr)
            if cex is None:
                print(f'id {idStr} in JSON file is missing from Python file', file=sys.stderr)
                n_not_found += 1
            else:
                match_errors = match_cex(cex_spec, cex)
                if match_errors:
                    for error in match_errors:
                        print(error, file=sys.stderr)
                    n_failed += 1
                else:
                    n_matched += 1
    print('JSON status:', n_matched, 'matched,', n_ignored, 'ignored,',
        n_not_found, 'not found,', n_failed, 'failed.', file=sys.stderr)
    return int(n_failed + n_not_found > 0)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify fair-division counterexamples.")
    parser.add_argument("file", type=Path,
        help="Python file exposing a COUNTEREXAMPLES list")
    parser.add_argument('--no-verify', action='store_false', dest='verify', default=True,
        help='Do not check correctness of counterexamples.')
    parser.add_argument("--cpigjs-json", type=Path,
        help="JSON file containing a spec of counterexamples. Will be cross-checked with the python file.")
    args = parser.parse_args()

    # check for duplicate ids in args.file
    cexs_list = load_counterexamples(args.file)
    cexs_dict = {}
    for cex in cexs_list:
        if cex.id in cexs_dict:
            raise Exception(f'duplicate id {cex.id}')
        else:
            cexs_dict[cex.id] = cex

    # match with args.cpigjs_json
    exit_status = 0
    if args.cpigjs_json:
        exit_status = match_json_file(args.cpigjs_json, cexs_dict)

    # verify counterexamples
    failed = 0
    for cex in cexs_list:
        if args.verify:
            errors = cex.verify()
            if errors:
                failed += 1
                print(f"FAIL [{cex.id}] ({cex.satisfies} doesn't imply {cex.violates}):",
                      file=sys.stderr)
                for err in errors:
                    print(f"  - {err}", file=sys.stderr)

    # report cexs verification results
    if args.verify:
        total = len(cexs_list)
        passed = total - failed
        print(f"{passed}/{total} counterexamples passed.", file=sys.stderr)
    if failed > 0:
        exit_status = 1
    sys.exit(exit_status)


if __name__ == "__main__":
    main()
