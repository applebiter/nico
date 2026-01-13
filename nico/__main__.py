"""Entry point for Nico application."""
# Import config first to disable telemetry before any other imports
from nico import config  # noqa: F401

import sys


def main() -> int:
    """Main entry point for the application."""
    print("Nico - Narrative Insight Composition Output")
    print("Version: 0.1.0")
    print("\n[Status: Early development - database models in progress]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
