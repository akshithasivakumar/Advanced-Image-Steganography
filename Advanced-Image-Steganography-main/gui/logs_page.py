import customtkinter as ctk
from tkinter import messagebox

from utils.logger import clear_logs as clear_log_entries, read_logs

COL_TIMESTAMP = 20
COL_OPERATION = 12
COL_STATUS = 12
COL_DETAILS = 55


def format_log_line(line):
    line = line.strip()

    if not line:
        return None

    if line.startswith("Timestamp") or line.startswith("-"):
        return None

    parts = [p.strip() for p in line.split("|")]

    if len(parts) < 3:
        return line

    timestamp = parts[0]
    operation = parts[1]
    status = parts[2]
    details = ""

    if len(parts) >= 4:
        details = " | ".join(parts[3:])

    return (
        f"{timestamp:<{COL_TIMESTAMP}}"
        f"{operation:<{COL_OPERATION}}"
        f"{status:<{COL_STATUS}}"
        f"{details}"
    )


def get_log_header():
    width = (
        COL_TIMESTAMP
        + COL_OPERATION
        + COL_STATUS
        + COL_DETAILS
    )

    separator = "═" * width

    header = (
        f"{'Timestamp':<{COL_TIMESTAMP}}"
        f"{'Operation':<{COL_OPERATION}}"
        f"{'Status':<{COL_STATUS}}"
        f"{'Details'}"
    )

    return f"{separator}\n{header}\n{separator}\n"


class LogsPage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent)

        self.configure(fg_color="transparent")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=20,
            pady=(20, 10)
        )

        top_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            top_frame,
            text="Activity Logs",
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            )
        )

        title.grid(row=0, column=0, sticky="w")

        button_frame = ctk.CTkFrame(
            top_frame,
            fg_color="transparent"
        )

        button_frame.grid(row=0, column=1, sticky="e")

        refresh_btn = ctk.CTkButton(
            button_frame,
            text="Refresh Logs",
            width=130,
            command=self.load_logs
        )

        refresh_btn.pack(side="left", padx=(0, 10))

        clear_btn = ctk.CTkButton(
            button_frame,
            text="Clear Logs",
            width=130,
            fg_color="#c0392b",
            hover_color="#962d22",
            command=self.clear_logs
        )

        clear_btn.pack(side="left")

        self.log_box = ctk.CTkTextbox(
            self,
            wrap="none",
            corner_radius=10
        )

        self.log_box.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=20,
            pady=(0, 20)
        )

        self.log_box.configure(
            font=ctk.CTkFont(
                family="Consolas",
                size=13
            )
        )

        self.load_logs()

    def load_logs(self):

        lines = read_logs()

        formatted = []

        for line in lines:
            entry = format_log_line(line)

            if entry:
                formatted.append(entry)

        formatted.reverse()

        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")

        if formatted:
            self.log_box.insert(
                "end",
                get_log_header()
            )

            self.log_box.insert(
                "end",
                "\n".join(formatted)
            )

        else:
            self.log_box.insert(
                "end",
                "No activity logs found."
            )

        self.log_box.configure(state="disabled")

    def clear_logs(self):

        confirm = messagebox.askyesno(
            "Clear Logs",
            "Delete all activity logs?"
        )

        if not confirm:
            return

        try:
            clear_log_entries()
            self.load_logs()

        except Exception as e:
            messagebox.showerror(
                "Error",
                str(e)
            )