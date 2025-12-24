# app.py
from __future__ import annotations

import inspect
import threading
import tkinter as tk
from datetime import datetime, date
from pathlib import Path
from tkinter import ttk, filedialog, messagebox

DATE_FMT = "%Y-%m-%d"  # input format: 2025-01-01


def parse_date(s: str) -> date:
    return datetime.strptime(s.strip(), DATE_FMT).date()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Financial Export Runner")
        self.geometry("560x260")
        self.resizable(False, False)

        # UI state
        self._running = False
        self._worker: threading.Thread | None = None

        # form vars
        self.start_var = tk.StringVar(value="2025-01-01")
        self.end_var = tk.StringVar(value="2025-12-31")
        self.output_var = tk.StringVar(value=str(Path("out") / "resumen_financiero.xlsx"))
        self.status_var = tk.StringVar(value="Ready.")

        self._build()

    def _build(self):
        root = ttk.Frame(self, padding=16)
        root.pack(fill="both", expand=True)

        # Dates
        ttk.Label(root, text="Start date (YYYY-MM-DD)").grid(row=0, column=0, sticky="w")
        ttk.Label(root, text="End date (YYYY-MM-DD)").grid(row=0, column=1, sticky="w", padx=(12, 0))

        ttk.Entry(root, textvariable=self.start_var, width=24).grid(row=1, column=0, sticky="w", pady=(4, 12))
        ttk.Entry(root, textvariable=self.end_var, width=24).grid(
            row=1, column=1, sticky="w", padx=(12, 0), pady=(4, 12)
        )

        # Output
        ttk.Label(root, text="Output file (.xlsx)").grid(row=2, column=0, sticky="w")
        ttk.Entry(root, textvariable=self.output_var, width=52).grid(
            row=3, column=0, columnspan=2, sticky="we", pady=(4, 6)
        )
        ttk.Button(root, text="Choose…", command=self.choose_output).grid(row=3, column=2, sticky="w", padx=(10, 0))

        # Actions
        self.run_btn = ttk.Button(root, text="Run", command=self.on_run)
        self.run_btn.grid(row=4, column=0, sticky="w", pady=(10, 0))

        ttk.Button(root, text="Quit", command=self.destroy).grid(row=4, column=1, sticky="w", padx=(12, 0), pady=(10, 0))

        # Status
        ttk.Separator(root).grid(row=5, column=0, columnspan=3, sticky="we", pady=(14, 10))
        ttk.Label(root, textvariable=self.status_var).grid(row=6, column=0, columnspan=3, sticky="w")

        root.columnconfigure(0, weight=1)
        root.columnconfigure(1, weight=1)

    def choose_output(self):
        path = filedialog.asksaveasfilename(
            title="Save output as",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=Path(self.output_var.get()).name if self.output_var.get() else "resumen_financiero.xlsx",
        )
        if path:
            self.output_var.set(path)

    def set_running(self, running: bool):
        self._running = running
        self.run_btn.config(state=("disabled" if running else "normal"))

    def on_run(self):
        if self._running:
            return

        # Validate inputs
        try:
            start = parse_date(self.start_var.get())
            end = parse_date(self.end_var.get())
        except ValueError:
            messagebox.showerror("Invalid date", f"Use format {DATE_FMT} (example: 2025-01-01).")
            return

        if start > end:
            messagebox.showerror("Invalid range", "Start date must be before or equal to end date.")
            return

        output_path_str = self.output_var.get().strip()
        if not output_path_str:
            messagebox.showerror("Missing output", "Choose an output file first.")
            return

        output_path = Path(output_path_str)

        # Run in background thread
        self.set_running(True)
        self.status_var.set("Running…")
        self._worker = threading.Thread(
            target=self._run_background, args=(start, end, output_path), daemon=True
        )
        self._worker.start()

    def _run_background(self, start: date, end: date, output_path: Path):
        try:
            self._call_backend(start, end, output_path)
        except Exception as e:
            self.after(0, self._on_failure, e)
        else:
            self.after(0, self._on_success, output_path)

    def _call_backend(self, start: date, end: date, output_path: Path):
        """
        Calls your backend.

        Supports BOTH controller styles:
          A) recommended: run_controller(start, end, output_path)
          B) old style:   run_controller()  (hardcoded dates/output inside controller)
        If you haven't updated controller.py yet, it will still run (style B),
        but the UI-selected values won't be used.
        """
        import controller  # local import so UI loads even if backend errors early

        if not hasattr(controller, "run_controller"):
            raise RuntimeError("controller.py must expose a function named run_controller().")

        fn = controller.run_controller
        sig = inspect.signature(fn)

        if len(sig.parameters) == 0:
            # Old controller signature: run_controller()
            fn()
            return

        if len(sig.parameters) == 3:
            # New signature: run_controller(start, end, output_path)
            fn(start, end, output_path)
            return

        raise RuntimeError(
            "Unsupported run_controller signature. Expected run_controller() or run_controller(start, end, output_path)."
        )

    def _on_success(self, output_path: Path):
        self.set_running(False)
        self.status_var.set("Done ✅")
        messagebox.showinfo("Success", f"Finished.\n\nSaved to:\n{output_path}")

    def _on_failure(self, err: Exception):
        self.set_running(False)
        self.status_var.set("Error ❌")
        messagebox.showerror("Error", str(err))


def main():
    App().mainloop()


if __name__ == "__main__":
    main()
