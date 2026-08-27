"""
main.py
-------
Single entry point:

    python main.py            -> launches the GUI
    python main.py --cli ...  -> runs the CLI (forwards remaining args to cli.py)

Examples:
    python main.py
    python main.py --cli --T 200 --K 190 --N 6
    python main.py --cli --T 200 --K 190 --N 6 --method exponential --image out.png
"""

import sys


def main():
    if "--cli" in sys.argv:
        from . import cli
        args = [a for a in sys.argv[1:] if a != "--cli"]
        cli.main(args)
    else:
        from . import gui
        gui.main()


if __name__ == "__main__":
    main()
