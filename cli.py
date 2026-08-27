"""
cli.py
------
Command line interface for the loyalty discount pricing calculator.

Examples:
    python cli.py --T 200 --K 190 --N 5
    python cli.py --T 200 --K 190 --N 5 --method exponential
    python cli.py --T 200 --K 190 --N 6 --method both \
        --csv out.csv --image out.png
"""

import argparse
import sys

from .core import generate_table, rows_to_table, validate_inputs
from .export_utils import save_csv, save_table_image


def print_table(headers, table):
    widths = [max(len(h), *(len(r[i]) for r in table)) if table else len(h)
              for i, h in enumerate(headers)]
    line_sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"

    def fmt_row(cells):
        return "|" + "|".join(f" {c:<{w}} " for c, w in zip(cells, widths)) + "|"

    print(line_sep)
    print(fmt_row(headers))
    print(line_sep)
    for row in table:
        print(fmt_row(row))
    print(line_sep)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Calculate loyalty / hesitation-discount pricing ramps."
    )
    parser.add_argument("--T", type=float, required=True, help="Normal (full) price, e.g. 200")
    parser.add_argument("--K", type=float, required=True, help="Target discounted/loyal price, e.g. 190")
    parser.add_argument("--N", type=int, required=True, help="Number of orders in the ramp, e.g. 5")
    parser.add_argument(
        "--method",
        choices=["normal", "exponential", "both"],
        default="both",
        help="Which ramp formula to use (default: both)",
    )
    parser.add_argument("--csv", metavar="PATH", help="Also save the table as a CSV file")
    parser.add_argument("--image", metavar="PATH", help="Also save the table as a PNG image")
    parser.add_argument("--no-table", action="store_true", help="Don't print the table to the console")

    args = parser.parse_args(argv)

    try:
        warnings = validate_inputs(args.T, args.K, args.N)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    for w in warnings:
        print(f"Warning: {w}", file=sys.stderr)

    rows = generate_table(args.T, args.K, args.N, method=args.method)
    headers, table = rows_to_table(rows, args.method)

    if not args.no_table:
        print_table(headers, table)

    if args.csv:
        save_csv(headers, table, args.csv)
        print(f"CSV saved to: {args.csv}")

    if args.image:
        title = f"Loyalty Pricing (T=${args.T:.2f}, K=${args.K:.2f}, N={args.N})"
        save_table_image(headers, table, args.image, title=title)
        print(f"Image saved to: {args.image}")


if __name__ == "__main__":
    main()
