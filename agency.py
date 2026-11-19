#!/usr/bin/env python3
"""
CLI entry point for the Research Agency Lab.
Prefer the web app:  streamlit run app.py
"""

import sys
from lab.core import run_research


def main():
    print("\n🔬 Research Agency Lab (CLI)")
    print("For the full controllable UI run:  streamlit run app.py\n")

    if len(sys.argv) > 1:
        request = " ".join(sys.argv[1:])
    else:
        request = input("Research question / project:\n> ").strip()
        if not request:
            print("No request. Exiting.")
            return

    print("\nLaunching hierarchical research lab...\n")
    result = run_research(request, verbose=True)

    print("\n" + "=" * 70)
    print("✅ FINAL RESEARCH OUTPUT")
    print("=" * 70)
    print(result)


if __name__ == "__main__":
    main()
