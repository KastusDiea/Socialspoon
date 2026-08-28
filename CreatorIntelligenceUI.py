import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Any, Callable, Iterable, Optional
import csv


class CreatorIntelligenceUI:
    """
    Tkinter UI for the Creator Intelligence System.

    Expected database input:
      - A list of dicts, e.g.
        [{"Platform": "YouTube", "Creator": "...", "Subscribers": 1234, ...}]
      - Or a list of objects. Object attributes are read by column name
        (spaces are converted to underscores).

    Optional:
      on_api_key_change(api_key): called when the API key is changed.
      filter_callback(rows): called after filters are applied.
    """

    DEFAULT_COLUMNS = [
        "Platform",
        "Creator",
        "Subscribers",
        "Title",
        "Views",
        "Likes",
        "Upload Date",
    ]

    PLATFORMS = ("YouTube", "Instagram", "Tiktok")

    def __init__(
        self,
        parent: Optional[tk.Misc] = None,
        data: Optional[Iterable[Any]] = None,
        on_api_key_change: Optional[Callable[[str], None]] = None,
        filter_callback: Optional[Callable[[list[dict]], None]] = None,
    ):
        self.parent = parent
        self.root = parent or tk.Tk()
        self.on_api_key_change = on_api_key_change
        self.filter_callback = filter_callback

        self.all_rows: list[dict] = []
        self.filtered_rows: list[dict] = []

        self.api_key_var = tk.StringVar()
        self.custom_keyword_var = tk.StringVar()
        self.search_var = tk.StringVar()

        self.platform_vars = {
            platform: tk.BooleanVar(value=True)
            for platform in self.PLATFORMS
        }

        self.sort_column: Optional[str] = None
        self.sort_reverse = False

        self._build_window()
        self._build_ui()

        if data is not None:
            self.set_data(data)

    # ---------------------------------------------------------
    # Window / layout
    # ---------------------------------------------------------

    def _build_window(self):
        if isinstance(self.root, tk.Tk):
            self.root.title("Creator Intelligence System")
            self.root.geometry("1250x700")
            self.root.minsize(900, 550)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

    def _build_ui(self):
        # =========================
        # TOP BAR
        # =========================
        top = ttk.Frame(self.root, padding=(12, 10))
        top.grid(row=0, column=0, sticky="ew")
        top.columnconfigure(0, weight=1)

        title_frame = ttk.Frame(top)
        title_frame.grid(row=0, column=0, sticky="w")

        ttk.Label(
            title_frame,
            text="Creator Intelligence System",
            font=("TkDefaultFont", 16, "bold"),
        ).pack(anchor="w")

        ttk.Label(
            title_frame,
            text="Creator data dashboard",
        ).pack(anchor="w")

        api_frame = ttk.Frame(top)
        api_frame.grid(row=0, column=1, sticky="e", padx=(20, 0))

        ttk.Label(api_frame, text="YouTube API Key:").grid(
            row=0, column=0, padx=(0, 6)
        )

        self.api_entry = ttk.Entry(
            api_frame,
            textvariable=self.api_key_var,
            width=38,
            show="*",
        )
        self.api_entry.grid(row=0, column=1, padx=(0, 6))

        ttk.Button(
            api_frame,
            text="Set Key",
            command=self._set_api_key,
        ).grid(row=0, column=2)

        # =========================
        # FILTER BAR
        # =========================
        filters = ttk.LabelFrame(
            self.root,
            text="Filters",
            padding=(10, 7),
        )
        filters.grid(
            row=1,
            column=0,
            sticky="new",
            padx=12,
            pady=(0, 8),
        )
        filters.columnconfigure(7, weight=1)

        ttk.Label(filters, text="Platforms:").grid(
            row=0, column=0, padx=(0, 8)
        )

        col = 1
        for platform in self.PLATFORMS:
            ttk.Checkbutton(
                filters,
                text=platform,
                variable=self.platform_vars[platform],
                command=self.apply_filters,
            ).grid(row=0, column=col, padx=4)
            col += 1

        ttk.Label(filters, text="Custom keyword:").grid(
            row=0, column=4, padx=(20, 6)
        )

        self.keyword_entry = ttk.Entry(
            filters,
            textvariable=self.custom_keyword_var,
            width=25,
        )
        self.keyword_entry.grid(row=0, column=5, padx=(0, 6))
        self.keyword_entry.bind("<Return>", lambda _: self.apply_filters())

        ttk.Button(
            filters,
            text="Apply",
            command=self.apply_filters,
        ).grid(row=0, column=6, padx=(0, 6))

        ttk.Button(
            filters,
            text="Clear",
            command=self.clear_filters,
        ).grid(row=0, column=7, sticky="w")

        ttk.Label(filters, text="Search table:").grid(
            row=1, column=0, padx=(0, 8), pady=(8, 0)
        )

        self.search_entry = ttk.Entry(
            filters,
            textvariable=self.search_var,
            width=35,
        )
        self.search_entry.grid(
            row=1,
            column=1,
            columnspan=3,
            sticky="w",
            pady=(8, 0),
        )
        self.search_entry.bind("<KeyRelease>", lambda _: self.apply_filters())

        ttk.Label(
            filters,
            text="Tip: click any column heading to sort.",
        ).grid(
            row=1,
            column=4,
            columnspan=3,
            sticky="w",
            padx=(20, 0),
            pady=(8, 0),
        )

        # =========================
        # TABLE
        # =========================
        table_frame = ttk.Frame(self.root, padding=(12, 0, 12, 0))
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        self.table = ttk.Treeview(
            table_frame,
            columns=self.DEFAULT_COLUMNS,
            show="headings",
            selectmode="extended",
        )
        self.table.grid(row=0, column=0, sticky="nsew")

        vertical_scroll = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.table.yview,
        )
        vertical_scroll.grid(row=0, column=1, sticky="ns")

        horizontal_scroll = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.table.xview,
        )
        horizontal_scroll.grid(row=1, column=0, sticky="ew")

        self.table.configure(
            yscrollcommand=vertical_scroll.set,
            xscrollcommand=horizontal_scroll.set,
        )

        for column in self.DEFAULT_COLUMNS:
            self.table.heading(
                column,
                text=column,
                command=lambda c=column: self.sort_by_column(c),
            )

            width = {
                "Platform": 110,
                "Creator": 180,
                "Subscribers": 120,
                "Title": 300,
                "Views": 110,
                "Likes": 110,
                "Upload Date": 130,
            }.get(column, 150)

            self.table.column(
                column,
                width=width,
                minwidth=70,
                anchor="center",
            )

        # =========================
        # BOTTOM BAR
        # =========================
        bottom = ttk.Frame(self.root, padding=12)
        bottom.grid(row=3, column=0, sticky="ew")
        bottom.columnconfigure(0, weight=1)

        self.status_label = ttk.Label(bottom, text="0 rows")
        self.status_label.grid(row=0, column=0, sticky="w")

        ttk.Button(
            bottom,
            text="Export Current Table to CSV",
            command=self.export_csv,
        ).grid(row=0, column=1, padx=(8, 0))

    # ---------------------------------------------------------
    # Data
    # ---------------------------------------------------------

    def set_data(self, data: Iterable[Any]):
        """Replace the table data."""
        self.all_rows = [self._normalize_row(row) for row in data]

        # Automatically include any columns present in the incoming data.
        self._update_columns()

        self.apply_filters()

    def add_data(self, data: Iterable[Any]):
        """Append rows to the current table."""
        self.all_rows.extend(
            self._normalize_row(row) for row in data
        )
        self._update_columns()
        self.apply_filters()

    def _normalize_row(self, row: Any) -> dict:
        if isinstance(row, dict):
            return {
                str(key): self._clean_value(value)
                for key, value in row.items()
            }

        result = {}

        # Convert object attributes to the known display columns.
        for column in self.DEFAULT_COLUMNS:
            attr = column.lower().replace(" ", "_")
            if hasattr(row, attr):
                result[column] = self._clean_value(getattr(row, attr))

        # Also support common variations.
        aliases = {
            "platform": "Platform",
            "creator": "Creator",
            "subscribers": "Subscribers",
            "title": "Title",
            "views": "Views",
            "likes": "Likes",
            "upload_date": "Upload Date",
        }

        for attr, column in aliases.items():
            if column not in result and hasattr(row, attr):
                result[column] = self._clean_value(getattr(row, attr))

        return result

    @staticmethod
    def _clean_value(value: Any) -> Any:
        if value is None:
            return ""
        return value

    def _update_columns(self):
        """Make the Treeview contain every column found in the data."""
        columns = list(self.DEFAULT_COLUMNS)

        for row in self.all_rows:
            for key in row:
                if key not in columns:
                    columns.append(key)

        # Preserve current horizontal table if possible.
        self.table.configure(columns=columns)

        for column in columns:
            self.table.heading(
                column,
                text=column,
                command=lambda c=column: self.sort_by_column(c),
            )

            if column not in self.table.column():
                pass

            width = 150
            if column == "Title":
                width = 300
            elif column == "Creator":
                width = 180
            elif column == "Platform":
                width = 110

            self.table.column(
                column,
                width=width,
                minwidth=70,
                anchor="center",
            )

    # ---------------------------------------------------------
    # Filtering
    # ---------------------------------------------------------

    def apply_filters(self):
        selected_platforms = {
            platform
            for platform, var in self.platform_vars.items()
            if var.get()
        }

        keyword = self.custom_keyword_var.get().strip().lower()
        search = self.search_var.get().strip().lower()

        rows = []

        for row in self.all_rows:
            platform = str(row.get("Platform", "")).strip()

            # If the row has a Platform value, apply platform filters.
            # Rows with no Platform are retained.
            if platform and platform not in selected_platforms:
                continue

            row_text = " ".join(
                str(value).lower()
                for value in row.values()
            )

            if keyword and keyword not in row_text:
                continue

            if search and search not in row_text:
                continue

            rows.append(row)

        self.filtered_rows = rows

        if self.sort_column:
            self.filtered_rows.sort(
                key=lambda row: self._sort_key(
                    row.get(self.sort_column, "")
                ),
                reverse=self.sort_reverse,
            )

        self._refresh_table()

        if self.filter_callback:
            self.filter_callback(self.filtered_rows)

    def clear_filters(self):
        for var in self.platform_vars.values():
            var.set(True)

        self.custom_keyword_var.set("")
        self.search_var.set("")

        self.apply_filters()

    # ---------------------------------------------------------
    # Sorting
    # ---------------------------------------------------------

    def sort_by_column(self, column: str):
        """
        Click once for ascending, again for descending.
        Works with numeric and text columns.
        """
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        self.filtered_rows.sort(
            key=lambda row: self._sort_key(row.get(column, "")),
            reverse=self.sort_reverse,
        )

        self._refresh_table()
        self._update_sort_headings()

    @staticmethod
    def _sort_key(value: Any):
        if value is None:
            return (0, "")

        text = str(value).strip().replace(",", "")

        try:
            return (1, float(text))
        except ValueError:
            return (2, text.lower())

    def _update_sort_headings(self):
        for column in self.table["columns"]:
            label = column

            if column == self.sort_column:
                label += " ▼" if self.sort_reverse else " ▲"

            self.table.heading(
                column,
                text=label,
                command=lambda c=column: self.sort_by_column(c),
            )

    # ---------------------------------------------------------
    # Table
    # ---------------------------------------------------------

    def _refresh_table(self):
        for item in self.table.get_children():
            self.table.delete(item)

        columns = list(self.table["columns"])

        for row in self.filtered_rows:
            values = [
                row.get(column, "")
                for column in columns
            ]

            self.table.insert("", "end", values=values)

        self.status_label.config(
            text=f"{len(self.filtered_rows)} rows "
                 f"(of {len(self.all_rows)})"
        )

    # ---------------------------------------------------------
    # API key
    # ---------------------------------------------------------

    def _set_api_key(self):
        api_key = self.api_key_var.get().strip()

        if not api_key:
            messagebox.showwarning(
                "Missing API Key",
                "Please enter a YouTube API key.",
            )
            return

        if self.on_api_key_change:
            try:
                self.on_api_key_change(api_key)
            except Exception as exc:
                messagebox.showerror(
                    "API Key Error",
                    str(exc),
                )
                return

        messagebox.showinfo(
            "API Key",
            "YouTube API key updated.",
        )

    def get_api_key(self) -> str:
        return self.api_key_var.get().strip()

    # ---------------------------------------------------------
    # CSV export
    # ---------------------------------------------------------

    def export_csv(self):
        if not self.filtered_rows:
            messagebox.showwarning(
                "Nothing to Export",
                "There are no rows in the current table.",
            )
            return

        path = filedialog.asksaveasfilename(
            title="Export Current Table",
            defaultextension=".csv",
            filetypes=[
                ("CSV files", "*.csv"),
                ("All files", "*.*"),
            ],
            initialfile="creator_data.csv",
        )

        if not path:
            return

        columns = list(self.table["columns"])

        try:
            with open(
                path,
                "w",
                newline="",
                encoding="utf-8-sig",
            ) as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=columns,
                    extrasaction="ignore",
                )

                writer.writeheader()

                for row in self.filtered_rows:
                    writer.writerow({
                        column: row.get(column, "")
                        for column in columns
                    })

            messagebox.showinfo(
                "Export Complete",
                f"Exported {len(self.filtered_rows)} rows.",
            )

        except Exception as exc:
            messagebox.showerror(
                "Export Error",
                str(exc),
            )

    # ---------------------------------------------------------
    # Run
    # ---------------------------------------------------------

    def run(self):
        """Start the Tkinter event loop when this class owns the root."""
        if self.parent is None:
            self.root.mainloop()


# ----------------------------------------------------------------
# Example standalone usage
# ----------------------------------------------------------------

if __name__ == "__main__":
    example_data = [
        {
            "Platform": "YouTube",
            "Creator": "Creator One",
            "Subscribers": 125000,
            "Title": "My Latest Video",
            "Views": 52000,
            "Likes": 4300,
            "Upload Date": "2026-08-25",
        },
        {
            "Platform": "Instagram",
            "Creator": "Creator Two",
            "Subscribers": 89000,
            "Title": "Behind the Scenes",
            "Views": 31000,
            "Likes": 5200,
            "Upload Date": "2026-08-24",
        },
        {
            "Platform": "Tiktok",
            "Creator": "Creator Three",
            "Subscribers": 250000,
            "Title": "Quick Creator Tip",
            "Views": 180000,
            "Likes": 19000,
            "Upload Date": "2026-08-23",
        },
    ]

    app = CreatorIntelligenceUI(data=example_data)
    app.run()
