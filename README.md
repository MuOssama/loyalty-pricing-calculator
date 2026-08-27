# Loyalty Discount Pricing Calculator

Calculates a gradual "hesitation-proof" discount ramp for loyal clients.

## The problem it solves

You sell a product at a normal price **T** (e.g. $200). A client wants a
loyalty price of **K** (e.g. $190), but you're not sure if they'll actually
keep ordering or just grab the discount once and disappear. Instead of
giving the full discount immediately, you ramp the price down gradually
over **N** orders — order `x` is priced at `P_x`, starting at `T` (order 1)
and ending at `K` (order N).

## Formulas

**Normal / Linear ramp:**
```
P_x = T - ((T - K) * (x - 1)) / (N - 1)
```

**Exponential ramp** (price stays close to T at first, then drops faster
towards the end):
```
P_x = T - (T - K) * (2^(x - 1) - 1) / (2^(N - 1) - 1)
```

Where:
- `T` = normal (full) price
- `K` = target discounted / loyalty price
- `N` = total number of orders in the ramp
- `x` = the order number (1..N)

If `N = 1`, there's only one order, so it's simply priced at `T`.

## Install

```bash
pip install -r requirements.txt
```

- The **CLI** only needs `matplotlib` (for image export) — everything else
  is Python's standard library.
- The **GUI** additionally needs `tkinter`. This ships with most Python
  installs on Windows/macOS. On Debian/Ubuntu Linux, if it's missing:
  ```bash
  sudo apt install python3-tk
  ```

## Usage

### GUI

```bash
python gui.py
# or
python main.py
```

Enter `T`, `K`, `N`, pick a method (normal / exponential / both), click
**Calculate**, then use **Export Table Image (PNG)** or **Export CSV** to
save the result.

### CLI

```bash
python cli.py --T 200 --K 190 --N 6
python cli.py --T 200 --K 190 --N 6 --method exponential
python cli.py --T 200 --K 190 --N 6 --method both --csv table.csv --image table.png
```

Options:

| Flag         | Description                                          |
|--------------|-------------------------------------------------------|
| `--T`        | Normal price (required)                               |
| `--K`        | Target discounted price (required)                    |
| `--N`        | Number of orders in the ramp (required)                |
| `--method`   | `normal`, `exponential`, or `both` (default: `both`)   |
| `--csv PATH` | Save the table as a CSV file                           |
| `--image PATH` | Save the table as a PNG image                       |
| `--no-table` | Suppress printing the table to the console              |

You can also run everything through `main.py`:

```bash
python main.py --cli --T 200 --K 190 --N 6 --image table.png
```

## Files

- `core.py` — pricing math (linear + exponential formulas)
- `export_utils.py` — CSV and PNG table export
- `cli.py` — command-line interface
- `gui.py` — Tkinter desktop GUI
- `main.py` — single launcher for both modes
