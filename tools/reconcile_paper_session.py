"""Reconcile a saved paper-observer session without modifying its records."""

import argparse
import json
import sys

from app.paper_reconcile import human_summary, reconcile_session


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("session_dir", help="directory containing observer_health.json and paper_journal.jsonl")
    args = parser.parse_args(argv)

    result = reconcile_session(args.session_dir)
    print(json.dumps(result, sort_keys=True, indent=2))
    print(human_summary(result), file=sys.stderr)
    return 0 if result["integrity_ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
