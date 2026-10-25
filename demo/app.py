"""Optional demo entry point; it delegates all behavior to the installed package."""

from drowsyalert.main import main

if __name__ == "__main__":
    raise SystemExit(main())
