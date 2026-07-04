from __future__ import annotations

import argparse
import sys
import unittest


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Shadowcaster test suite.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show individual test names.")
    args = parser.parse_args()

    loader = unittest.defaultTestLoader
    suite = loader.discover("shadowcaster/tests", top_level_dir=".")
    verbosity = 2 if args.verbose else 1
    result = unittest.TextTestRunner(verbosity=verbosity).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
