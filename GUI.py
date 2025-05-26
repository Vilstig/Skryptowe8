import tkinter as tk
from tkinter import filedialog, messagebox

from tkcalendar import Calendar

from http_log import HttpLog, HttpLogEntry
from datetime import datetime, timedelta


class LogViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Log Viewer")

        self.current_index = -1

        self.logs = []
        self.filtered_logs = []

        self.create_widgets()

    def create_widgets(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)

        self.file_entry = tk.Entry(top_frame)
        self.file_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

        browse_button = tk.Button(top_frame, text="Browse", command=self.browse_file)
        browse_button.pack(side=tk.LEFT, padx=5)

        load_button = tk.Button(top_frame, text="Load", command=self.load_file_from_entry)
        load_button.pack(side=tk.LEFT, padx=5)

        filter_frame = tk.Frame(self.root)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        # --- Start date ---
        tk.Label(filter_frame, text="Od (YYYY-MM-DD):").pack(side=tk.LEFT)
        self.start_date_var = tk.StringVar()
        self.start_date_entry = tk.Entry(filter_frame, textvariable=self.start_date_var, width=12, state='readonly')
        self.start_date_entry.pack(side=tk.LEFT, padx=5)
        start_date_button = tk.Button(filter_frame, text="📅", command=self.open_start_date_picker)
        start_date_button.pack(side=tk.LEFT)

        # --- End date ---
        tk.Label(filter_frame, text="Do (YYYY-MM-DD):").pack(side=tk.LEFT)
        self.end_date_var = tk.StringVar()
        self.end_date_entry = tk.Entry(filter_frame, textvariable=self.end_date_var, width=12, state='readonly')
        self.end_date_entry.pack(side=tk.LEFT, padx=5)
        end_date_button = tk.Button(filter_frame, text="📅", command=self.open_end_date_picker)
        end_date_button.pack(side=tk.LEFT)

        filter_button = tk.Button(filter_frame, text="Filtruj", command=self.filter_dates)
        filter_button.pack(side=tk.LEFT, padx=10)
        # Nawigacja logów
        nav_frame = tk.Frame(self.root)
        nav_frame.pack(fill=tk.X, padx=10, pady=5)

        prev_button = tk.Button(nav_frame, text="Previous", command=self.show_previous)
        prev_button.pack(side=tk.LEFT, padx=5)

        next_button = tk.Button(nav_frame, text="Next", command=self.show_next)
        next_button.pack(side=tk.LEFT, padx=5)

        self.prev_button = prev_button
        self.next_button = next_button
        list_frame = tk.Frame(self.root)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_list = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.log_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.log_list.bind('<<ListboxSelect>>', self.show_details)  # binds selecting element in list to show_details
        scrollbar.config(command=self.log_list.yview)

        self.detail_frame = tk.Frame(self.root)
        self.detail_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.detail_text = tk.Text(self.detail_frame, wrap=tk.WORD, state='disabled')
        self.detail_text.pack(fill=tk.BOTH, expand=True)

    def open_start_date_picker(self):
        self.open_date_picker(self.start_date_var)

    def open_end_date_picker(self):
        self.open_date_picker(self.end_date_var)

    def open_date_picker(self, target_var):
        def on_date_select():
            selected_date = cal.selection_get()
            target_var.set(selected_date.strftime("%Y-%m-%d"))
            top.destroy()

        top = tk.Toplevel(self.root)
        top.grab_set()
        top.title("Wybierz datę")
        cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack(padx=10, pady=10)

        ok_button = tk.Button(top, text="OK", command=on_date_select)
        ok_button.pack(pady=(0, 10))

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Log files", "*.log"), ("All files", "*.*")])
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)
            self.load_file(file_path)

    def load_file_from_entry(self):
        file_path = self.file_entry.get().strip()
        if not file_path:
            messagebox.showwarning("No path", "Please input the file path.")
            return
        self.load_file(file_path)

    def load_file(self, file_path):
        try:
            log = HttpLog(file_path)
            self.logs = log.entries
            self.filtered_logs = log.entries
            self.log_list.delete(0, tk.END)

            for entry in self.filtered_logs:
                self.log_list.insert(tk.END, entry.summary())

        except Exception as e:
            messagebox.showerror("Error", f"Can't load file:\n{e}")

    def show_details(self, event=None):
        selection = self.log_list.curselection()
        if not selection:
            return
        index = selection[0]
        self.current_index = index
        log_entry = self.filtered_logs[index]
        details = "\n".join([f"{k}: {v}" for k, v in log_entry.to_dict().items()])
        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete("1.0", tk.END)
        self.detail_text.insert(tk.END, details)
        self.detail_text.config(state=tk.DISABLED)
        self.update_nav_buttons()

    def filter_dates(self):

        start_date = self.start_date_var.get().strip()
        end_date = self.end_date_var.get().strip()

        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
            end_date = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
            if end_date:
                end_date = datetime.combine(end_date, datetime.max.time())
            if start_date:
                start_date = datetime.combine(start_date, datetime.min.time())
        except ValueError:
            tk.messagebox.showerror("Wrong date format", "Use format YYYY-MM-DD")
            return

        filtered = []
        for entry in self.logs:
            if (not start_date or entry.timestamp >= start_date) and (not end_date or entry.timestamp <= end_date):
                filtered.append(entry)

        self.log_list.delete(0, tk.END)
        for entry in filtered:
            self.log_list.insert(tk.END, entry.summary())

        self.filtered_logs = filtered


    def update_nav_buttons(self):
        self.prev_button.config(state=tk.NORMAL if self.current_index > 0 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if self.current_index < len(self.filtered_logs) - 1 else tk.DISABLED)


    def show_previous(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.log_list.selection_clear(0, tk.END)
            self.log_listA.selection_set(self.current_index)
            self.log_list.activate(self.current_index)
            self.show_details()


    def show_next(self):
        if self.current_index < len(self.filtered_logs) - 1:
            self.current_index += 1
            self.log_list.selection_clear(0, tk.END)
            self.log_list.selection_set(self.current_index)
            self.log_list.activate(self.current_index)
            self.show_details()


if __name__ == "__main__":
    root = tk.Tk()
    gui = LogViewer(root)
    root.mainloop()
