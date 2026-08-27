"""
export_utils.py
----------------
Helpers to export a pricing table to CSV and to a rendered PNG image.
"""

import csv
from typing import List

import matplotlib
matplotlib.use("Agg")  # safe for headless/CLI use; GUI overrides backend itself if needed
import matplotlib.pyplot as plt


def save_csv(headers: List[str], table: List[List[str]], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(table)


def save_table_image(
    headers: List[str],
    table: List[List[str]],
    path: str,
    title: str = "Loyalty Discount Pricing Table",
) -> None:
    """Render the table as a styled PNG image."""
    n_rows = len(table)
    n_cols = len(headers)

    fig_width = max(6, n_cols * 1.9)
    fig_height = max(2, 0.55 * (n_rows + 2))

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.axis("off")
    # Escape "$" so matplotlib doesn't interpret it as LaTeX math-mode
    safe_title = title.replace("$", "\\$")
    ax.set_title(safe_title, fontsize=14, fontweight="bold", pad=16)

    mpl_table = ax.table(
        cellText=table,
        colLabels=headers,
        loc="center",
        cellLoc="center",
    )
    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(10)
    mpl_table.scale(1, 1.5)
    mpl_table.auto_set_column_width(col=list(range(n_cols)))

    header_color = "#2c3e50"
    row_color_even = "#f2f2f2"
    row_color_odd = "#ffffff"

    for (row, col), cell in mpl_table.get_celld().items():
        cell.set_edgecolor("#cccccc")
        if row == 0:
            cell.set_facecolor(header_color)
            cell.set_text_props(color="white", fontweight="bold")
        else:
            cell.set_facecolor(row_color_even if row % 2 == 0 else row_color_odd)

    plt.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
