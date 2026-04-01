import hashlib
import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, scrolledtext


# ---------------- LOG CLASS ---------------- #
class LogEntry:
    def __init__(self, timestamp, event_type, description, prev_hash):
        self.timestamp = timestamp
        self.event_type = event_type
        self.description = description
        self.prev_hash = prev_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        data = f"{self.timestamp}{self.event_type}{self.description}{self.prev_hash}"
        return hashlib.sha256(data.encode()).hexdigest()

    def to_dict(self):
        return self.__dict__


# ---------------- GUI CLASS ---------------- #
class TamperLogGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tamper-Evident Logging System")
        self.root.geometry("700x500")

        self.logs = []

        # Title
        tk.Label(root, text="Tamper-Evident Logging System",
                 font=("Arial", 16, "bold")).pack(pady=10)

        # Input Frame
        frame = tk.Frame(root)
        frame.pack(pady=10)

        tk.Label(frame, text="Event Type:").grid(row=0, column=0, padx=5, pady=5)
        self.event_entry = tk.Entry(frame, width=40)
        self.event_entry.grid(row=0, column=1, padx=5)

        tk.Label(frame, text="Description:").grid(row=1, column=0, padx=5, pady=5)
        self.desc_entry = tk.Entry(frame, width=40)
        self.desc_entry.grid(row=1, column=1, padx=5)

        # Buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add Log", width=15, command=self.add_log).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Verify Logs", width=15, command=self.verify_logs).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Save Logs", width=15, command=self.save_logs).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Load Logs", width=15, command=self.load_logs).grid(row=0, column=3, padx=5)

        tk.Button(btn_frame, text="Clear Screen", width=15,
                  command=lambda: self.output.delete(1.0, tk.END)).grid(row=1, column=1, pady=5)

        # Output Box
        self.output = scrolledtext.ScrolledText(root, width=80, height=15)
        self.output.pack(pady=10)

    # ---------------- FUNCTIONS ---------------- #

    def add_log(self):
        event = self.event_entry.get()
        desc = self.desc_entry.get()

        if not event or not desc:
            messagebox.showwarning("Warning", "All fields required!")
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prev_hash = self.logs[-1].hash if self.logs else "0"

        log = LogEntry(timestamp, event, desc, prev_hash)
        self.logs.append(log)

        self.output.insert(tk.END, f"Added: {event} | Hash: {log.hash[:12]}...\n")

    def verify_logs(self):
        if not self.logs:
            messagebox.showinfo("Info", "No logs to verify")
            return

        for i in range(len(self.logs)):
            current = self.logs[i]

            # Check hash integrity
            if current.hash != current.calculate_hash():
                messagebox.showerror("ALERT", f"Tampering detected at log {i}")
                return

            # Check chain linkage
            if i > 0:
                prev = self.logs[i - 1]
                if current.prev_hash != prev.hash:
                    messagebox.showerror("ALERT", f"Chain broken at log {i}")
                    return

        messagebox.showinfo("Success", "Logs are secure")

    def save_logs(self):
        try:
            file_path = os.path.join(os.path.dirname(__file__), "logs.json")

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump([log.to_dict() for log in self.logs], f, indent=4)

            self.output.insert(tk.END, f"Saved at: {file_path}\n")
            messagebox.showinfo("Success", "Logs saved successfully!")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_logs(self):
        try:
            file_path = os.path.join(os.path.dirname(__file__), "logs.json")

            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.logs = []

            for entry in data:
                log = LogEntry(
                    entry["timestamp"],
                    entry["event_type"],
                    entry["description"],
                    entry["prev_hash"]
                )
                log.hash = entry["hash"]
                self.logs.append(log)

            self.output.insert(tk.END, "Logs loaded successfully\n")
            self.verify_logs()

        except FileNotFoundError:
            messagebox.showerror("Error", "No logs.json found in folder")


# ---------------- RUN APP ---------------- #
if __name__ == "__main__":
    root = tk.Tk()
    app = TamperLogGUI(root)
    root.mainloop()