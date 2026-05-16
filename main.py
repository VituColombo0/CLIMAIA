#!/usr/bin/env python3
"""
CLIMAIA – Climate AI Analysis
Entry point for the desktop application.

Usage:
    python main.py
"""

import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main_app import CLIMAIAApp


def main():
    app = CLIMAIAApp()
    app.mainloop()


if __name__ == "__main__":
    main()
