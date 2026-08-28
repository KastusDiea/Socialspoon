import tkinter as tk
from tkinter import ttk, filedialog
import csv
class CreatorIntelligence:

    def __init__(self, data, api_service=None):
        self.data = data
        self.filtered_data = data
        self.api_service = api_service
        self.root = tk.Tk()
        self.root.title("Creator Intelligence System")
        self.root.geometry("1200x700")
        self.api_key = tk.StringVar()
        self.keyword = tk.StringVar()
        self.youtube = tk.BooleanVar(value=True)
        self.instagram = tk.BooleanVar(value=True)
        self.tiktok = tk.BooleanVar(value=True)
        self.sort_column = None
        self.sort_reverse = False
        self.build_ui()

    def build_ui(self):
        top = tk.Frame(self.root)
        top.pack(fill="x", padx=10, pady=10)
        tk.Label(top, text="Creator Intelligence System", font=("Arial", 18, "bold")).pack(side="left")
        api_frame = tk.Frame(top)
        api_frame.pack(side="right")
        tk.Label(api_frame, text="YouTube API Key:").pack(side="left")
        tk.Entry(api_frame, textvariable=self.api_key, width=30, show="*").pack(side="left", padx=5)
        tk.Button(api_frame, text="Set Key", command=self.set_api_key).pack(side="left")
        filters = tk.Frame(self.root)
        filters.pack(fill="x", padx=10, pady=5)
        tk.Label(filters, text="Platforms:").pack(side="left")
        tk.Checkbutton(filters, text="YouTube", variable=self.youtube, command=self.filter).pack(side="left")
        tk.Checkbutton(filters, text="Instagram", variable=self.instagram, command=self.filter).pack(side="left")
        tk.Checkbutton(filters, text="Tiktok", variable=self.tiktok, command=self.filter).pack(side="left")
        tk.Label(filters, text="Keyword:").pack(side="left", padx=(20, 5))
        tk.Entry(filters, textvariable=self.keyword, width=25).pack(side="left")
        tk.Button(filters, text="Filter", command=self.filter).pack(side="left", padx=5)
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        columns = ["Platform", "Creator", "Subscribers", "Title", "Views", "Likes", "Upload Date"]
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings")
        for column in columns:
            self.table.heading(column, text=column, command=lambda c=column: self.sort(c))
            self.table.column(column, width=150)
        self.table.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        scrollbar.pack(side="right", fill="y")
        self.table.configure(yscrollcommand=scrollbar.set)
        bottom = tk.Frame(self.root)
        bottom.pack(fill="x", padx=10, pady=10)
        self.status = tk.Label(bottom, text="")
        self.status.pack(side="left")
        tk.Button(bottom, text="Export Current Table to CSV", command=self.export_csv).pack(side="right")
        self.display()

    def display(self):
        for item in self.table.get_children():
            self.table.delete(item)
        for row in self.filtered_data:
            values = [
                row.get("Platform", ""),
                row.get("Creator", ""),
                row.get("Subscribers", ""),
                row.get("Title", ""),
                row.get("Views", ""),
                row.get("Likes", ""),
                row.get("Upload Date", "")
            ]
            self.table.insert("", "end", values=values)
        self.status.config(text=f"{len(self.filtered_data)} rows")

    def filter(self):
        keyword = self.keyword.get().lower()
        allowed_platforms = []
        if self.youtube.get():
            allowed_platforms.append("YouTube")
        if self.instagram.get():
            allowed_platforms.append("Instagram")
        if self.tiktok.get():
            allowed_platforms.append("Tiktok")
        self.filtered_data = []
        for row in self.data:
            platform = str(row.get("Platform", ""))
            text = " ".join(str(value) for value in row.values()).lower()
            if platform not in allowed_platforms:
                continue
            if keyword and keyword not in text:
                continue
            self.filtered_data.append(row)
        self.display()

    def sort(self, column):
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        self.filtered_data.sort(
            key=lambda row: str(row.get(column, "")).lower(),
            reverse=self.sort_reverse
        )
        self.display()

    def set_api_key(self):
        key = self.api_key.get().strip()
        if self.api_service:
            self.api_service.set_yt_api_key(key)
        print("YouTube API key updated.")

    def export_csv(self):
        if not self.filtered_data:
            return
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if not filename:
            return
        columns = ["Platform", "Creator", "Subscribers", "Title", "Views", "Likes", "Upload Date"]
        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=columns)
            writer.writeheader()
            writer.writerows(self.filtered_data)

    def run(self):
        self.root.mainloop()
