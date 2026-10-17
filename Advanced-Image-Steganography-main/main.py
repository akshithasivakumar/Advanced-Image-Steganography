import customtkinter as ctk

from gui.home import HomePage
from gui.encode_page import EncodePage
from gui.decode_page import DecodePage
from gui.logs_page import LogsPage


ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Advanced Image Steganography")
        self.geometry("1200x700")
        self.minsize(1000, 650)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ---------------- Sidebar ---------------- #

        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        self.title_label = ctk.CTkLabel(
            self.sidebar,
            text="Advanced Image\nSteganography",
            font=("Arial", 22, "bold"),
            justify="center"
        )
        self.title_label.pack(pady=(30, 40))

        self.home_button = ctk.CTkButton(
            self.sidebar,
            text="Home",
            command=self.show_home
        )
        self.home_button.pack(fill="x", padx=20, pady=8)

        self.encode_button = ctk.CTkButton(
            self.sidebar,
            text="Encode",
            command=self.show_encode
        )
        self.encode_button.pack(fill="x", padx=20, pady=8)

        self.decode_button = ctk.CTkButton(
            self.sidebar,
            text="Decode",
            command=self.show_decode
        )
        self.decode_button.pack(fill="x", padx=20, pady=8)

        self.logs_button = ctk.CTkButton(
            self.sidebar,
            text="Logs",
            command=self.show_logs
        )
        self.logs_button.pack(fill="x", padx=20, pady=8)

        self.exit_button = ctk.CTkButton(
            self.sidebar,
            text="Exit",
            fg_color="firebrick",
            hover_color="darkred",
            command=self.destroy
        )
        self.exit_button.pack(side="bottom", fill="x", padx=20, pady=20)

        # ---------------- Main Content ---------------- #

        self.content_frame = ctk.CTkFrame(self, corner_radius=0)
        self.content_frame.grid(row=0, column=1, sticky="nsew")

        self.current_page = None
        self.show_home()

    def clear_page(self):
        page = self.current_page
        self.current_page = None

        if page is not None and page.winfo_exists():
            page.destroy()

    def show_home(self):
        self.clear_page()
        self.current_page = HomePage(self.content_frame)
        self.current_page.pack(fill="both", expand=True)

    def show_encode(self):
        self.clear_page()
        self.current_page = EncodePage(self.content_frame)
        self.current_page.pack(fill="both", expand=True)

    def show_decode(self):
        self.clear_page()
        self.current_page = DecodePage(self.content_frame)
        self.current_page.pack(fill="both", expand=True)

    def show_logs(self):
        self.clear_page()
        self.current_page = LogsPage(self.content_frame)
        self.current_page.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = App()
    app.mainloop()