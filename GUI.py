import tkinter as tk
from tkinter import filedialog, messagebox
from http_log import HttpLog, HttpLogEntry
from datetime import datetime,timedelta

class LogViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Log Viewer")

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

        tk.Label(filter_frame, text="Od (YYYY-MM-DD):").pack(side=tk.LEFT)
        self.start_date_entry = tk.Entry(filter_frame, width=12)
        self.start_date_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(filter_frame, text="Do (YYYY-MM-DD):").pack(side=tk.LEFT)
        self.end_date_entry = tk.Entry(filter_frame, width=12)
        self.end_date_entry.pack(side=tk.LEFT, padx=5)

        filter_button = tk.Button(filter_frame, text="Filtruj", command=self.filter_dates)
        filter_button.pack(side=tk.LEFT, padx=10)

        list_frame = tk.Frame(self.root)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_list = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.log_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.log_list.bind('<<ListboxSelect>>', self.show_details) # binds selecting element in list to show_details
        scrollbar.config(command=self.log_list.yview)

        self.detail_frame = tk.Frame(self.root)
        self.detail_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.detail_text = tk.Text(self.detail_frame, wrap=tk.WORD, state='disabled')
        self.detail_text.pack(fill=tk.BOTH, expand=True)

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

    def show_details(self, event): # why is the text field editable when the enabling line is at the start of this functionn?
        selection = self.log_list.curselection()
        if not selection:
            return
        index = selection[0]
        log_entry = self.filtered_logs[index]
        details = "\n".join([f"{k}: {v}" for k, v in log_entry.to_dict().items()])
        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete("1.0", tk.END)
        self.detail_text.insert(tk.END, details)
        self.detail_text.config(state=tk.DISABLED)

    def filter_dates(self):
        start_date_txt = self.start_date_entry.get().strip()
        end_date_txt = self.end_date_entry.get().strip()

        try:
            start_date = datetime.strptime(start_date_txt, "%Y-%m-%d") if start_date_txt else None
            end_date = timedelta(hours=23, minutes=59, seconds=59) + datetime.strptime(end_date_txt, "%Y-%m-%d") if end_date_txt else None
        except ValueError:
            tk.messagebox.showerror("Wrong data format", "Use format YYYY-MM-DD")
            return


        filtered = []
        for entry in self.logs:
            if (not start_date or entry.timestamp >= start_date) and (not end_date or entry.timestamp <= end_date):
                filtered.append(entry)

        self.log_list.delete(0, tk.END)
        for entry in filtered:
            self.log_list.insert(tk.END, entry.summary())

        self.filtered_logs = filtered


if __name__ == "__main__":
    root = tk.Tk()
    gui = LogViewer(root)
    root.mainloop()