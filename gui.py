"""
gui.py
------
Desktop GUI (Tkinter, standard library only) for the loyalty discount
pricing calculator.

Run with:
    python gui.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from .core import generate_table, rows_to_table, validate_inputs
from .export_utils import save_csv, save_table_image


class LoyaltyPricingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Loyalty Discount Pricing Calculator")
        self.geometry("980x560")
        self.minsize(820, 460)
        self.configure(bg="#f5f6f8")

        self._current_headers = []
        self._current_table = []
        self._current_rows = []
        self._current_title = "Loyalty Discount Pricing Table"

        self._build_style()
        self._build_input_bar()
        self._build_views()
        self._build_status_bar()

    # ------------------------------------------------------------------ UI
    def _build_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", rowheight=26, font=("Segoe UI", 10))
        style.configure("TLabel", background="#f5f6f8", font=("Segoe UI", 10))
        style.configure("Header.TLabel", background="#f5f6f8", font=("Segoe UI", 15, "bold"))
        style.configure("TButton", font=("Segoe UI", 10))

    def _build_input_bar(self):
        header = ttk.Label(self, text="Loyalty / Hesitation Discount Pricing", style="Header.TLabel")
        header.pack(anchor="w", padx=16, pady=(14, 4))

        subtitle = ttk.Label(
            self,
            text="Ramp a client's price from a normal price T down to a target loyalty price K over N orders.",
        )
        subtitle.pack(anchor="w", padx=16, pady=(0, 10))

        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=16, pady=4)

        self.t_var = tk.StringVar(value="200")
        self.k_var = tk.StringVar(value="190")
        self.n_var = tk.StringVar(value="6")
        self.method_var = tk.StringVar(value="both")

        self._labeled_entry(bar, "Normal Price (T):", self.t_var, 0)
        self._labeled_entry(bar, "Target Price (K):", self.k_var, 1)
        self._labeled_entry(bar, "Number of Orders (N):", self.n_var, 2)

        ttk.Label(bar, text="Method:").grid(row=0, column=6, sticky="w", padx=(16, 4))
        method_box = ttk.Combobox(
            bar,
            textvariable=self.method_var,
            values=["normal", "exponential", "both"],
            state="readonly",
            width=13,
        )
        method_box.grid(row=0, column=7, sticky="w")

        calc_btn = ttk.Button(bar, text="Calculate", command=self.calculate)
        calc_btn.grid(row=0, column=8, sticky="w", padx=(16, 0))

        export_bar = ttk.Frame(self)
        export_bar.pack(fill="x", padx=16, pady=(2, 8))

        ttk.Button(export_bar, text="Export Table Image (PNG)", command=self.export_image).pack(
            side="left"
        )
        ttk.Button(export_bar, text="Export Chart Image (PNG)", command=self.export_chart).pack(
            side="left", padx=(8, 0)
        )
        ttk.Button(export_bar, text="Export CSV", command=self.export_csv).pack(
            side="left", padx=(8, 0)
        )

    def _labeled_entry(self, parent, label, var, col_start):
        ttk.Label(parent, text=label).grid(row=0, column=col_start * 2, sticky="w", padx=(0 if col_start == 0 else 16, 4))
        entry = ttk.Entry(parent, textvariable=var, width=10)
        entry.grid(row=0, column=col_start * 2 + 1, sticky="w")
        return entry

    def _build_views(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        self.table_frame = ttk.Frame(self.notebook)
        self.chart_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.table_frame, text="Data Table")
        self.notebook.add(self.chart_frame, text="Pricing Chart")

        # Table
        self.tree = ttk.Treeview(self.table_frame, show="headings")
        vsb = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        self.table_frame.rowconfigure(0, weight=1)
        self.table_frame.columnconfigure(0, weight=1)

        self.tree.tag_configure("odd", background="#ffffff")
        self.tree.tag_configure("even", background="#f2f2f2")

        # Chart
        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def _build_status_bar(self):
        self.status_var = tk.StringVar(value="Enter values and click Calculate.")
        status = ttk.Label(self, textvariable=self.status_var, anchor="w")
        status.pack(fill="x", padx=16, pady=(0, 10))

    # --------------------------------------------------------------- logic
    def _parse_inputs(self):
        try:
            T = float(self.t_var.get())
            K = float(self.k_var.get())
            N = int(float(self.n_var.get()))
        except ValueError:
            raise ValueError("T and K must be numbers, and N must be a whole number.")
        return T, K, N

    def calculate(self):
        try:
            T, K, N = self._parse_inputs()
            warnings = validate_inputs(T, K, N)
        except ValueError as e:
            messagebox.showerror("Invalid input", str(e))
            return

        method = self.method_var.get()
        self._current_rows = generate_table(T, K, N, method=method)
        headers, table = rows_to_table(self._current_rows, method)

        self._current_headers = headers
        self._current_table = table
        self._current_title = f"Loyalty Pricing (T=${T:.2f}, K=${K:.2f}, N={N})"

        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = headers
        for h in headers:
            self.tree.heading(h, text=h)
            self.tree.column(h, anchor="center", width=max(90, int(760 / len(headers))))

        for i, row in enumerate(table):
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.insert("", "end", values=row, tags=(tag,))

        # Update chart
        self.ax.clear()
        
        chart_rows = [r for r in self._current_rows if isinstance(r.order, int)]
        orders = [r.order for r in chart_rows]
        if method in ("normal", "both"):
            n_prices = [r.normal_price for r in chart_rows]
            self.ax.plot(orders, n_prices, marker='o', label="Normal", color="blue")
        if method in ("exponential", "both"):
            e_prices = [r.exponential_price for r in chart_rows]
            self.ax.plot(orders, e_prices, marker='s', label="Exponential", color="orange")
        
        self.ax.axhline(T, color="red", linestyle="--", alpha=0.5, label="Normal Price (T)")
        self.ax.axhline(K, color="green", linestyle="--", alpha=0.5, label="Target Price (K)")

        self.ax.set_title(self._current_title)
        self.ax.set_xlabel("Order Number")
        self.ax.set_ylabel("Price ($)")
        self.ax.set_xticks(orders)
        self.ax.grid(True, linestyle=":", alpha=0.6)
        self.ax.legend()
        self.fig.tight_layout()
        self.canvas.draw()

        if warnings:
            self.status_var.set("Calculated with warning(s): " + " | ".join(warnings))
        else:
            self.status_var.set(f"Calculated {N} order(s) using method: {method}.")

    def _ensure_calculated(self):
        if not self._current_table:
            messagebox.showwarning("Nothing to export", "Click Calculate first.")
            return False
        return True

    def export_image(self):
        if not self._ensure_calculated():
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG image", "*.png")],
            title="Save table as image",
        )
        if not path:
            return
        save_table_image(self._current_headers, self._current_table, path, title=self._current_title)
        self.status_var.set(f"Image saved to: {path}")

    def export_chart(self):
        if not self._ensure_calculated():
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG image", "*.png")],
            title="Save chart as image",
        )
        if not path:
            return
        self.fig.savefig(path, dpi=200, bbox_inches="tight")
        self.status_var.set(f"Chart saved to: {path}")

    def export_csv(self):
        if not self._ensure_calculated():
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV file", "*.csv")],
            title="Save table as CSV",
        )
        if not path:
            return
        save_csv(self._current_headers, self._current_table, path)
        self.status_var.set(f"CSV saved to: {path}")


def main():
    app = LoyaltyPricingApp()
    app.mainloop()


if __name__ == "__main__":
    main()
