import os
from tkinter import filedialog, messagebox

import customtkinter as ctk

from algorithms.lsb_decode import decode_image
from utils.logger import log_decode, log_error


class DecodePage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(fg_color="transparent")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(
            self,
            text="Decode Hidden Message",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.main_frame.grid_columnconfigure(1, weight=1)

        self.image_label = ctk.CTkLabel(self.main_frame, text="Encoded Image:")
        self.image_label.grid(row=0, column=0, padx=15, pady=12, sticky="w")

        self.image_path_var = ctk.StringVar(value="")
        self.image_entry = ctk.CTkEntry(self.main_frame, textvariable=self.image_path_var)
        self.image_entry.grid(row=0, column=1, padx=(0, 10), pady=12, sticky="ew")

        self.browse_button = ctk.CTkButton(
            self.main_frame,
            text="Browse",
            command=self.browse_image,
            width=100
        )
        self.browse_button.grid(row=0, column=2, padx=(0, 15), pady=12)

        self.password_label = ctk.CTkLabel(self.main_frame, text="Password:")
        self.password_label.grid(row=1, column=0, padx=15, pady=12, sticky="w")

        self.password_var = ctk.StringVar(value="")
        self.password_entry = ctk.CTkEntry(self.main_frame, textvariable=self.password_var, show="*")
        self.password_entry.grid(row=1, column=1, padx=(0, 10), pady=12, sticky="ew")

        self.algorithm_label = ctk.CTkLabel(self.main_frame, text="Algorithm:")
        self.algorithm_label.grid(row=2, column=0, padx=15, pady=(12, 5), sticky="nw")

        self.algorithm_var = ctk.StringVar(value="Standard LSB")
        self.algorithm_combo = ctk.CTkOptionMenu(
            self.main_frame,
            values=["Standard LSB", "Random LSB"],
            variable=self.algorithm_var,
            width=200
        )
        self.algorithm_combo.grid(row=2, column=1, padx=(0, 10), pady=(12, 5), sticky="nw")

        self.algorithm_hint = ctk.CTkLabel(
            self.main_frame,
            text="Use the same algorithm that was selected during encoding.",
            font=ctk.CTkFont(size=11, slant="italic"),
            text_color=("gray60", "gray40")
        )
        self.algorithm_hint.grid(row=3, column=0, columnspan=2, padx=15, pady=(0, 8), sticky="w")

        self.decode_button = ctk.CTkButton(
            self.main_frame,
            text="Decode",
            command=self.handle_decode,
            width=120
        )
        self.decode_button.grid(row=4, column=1, padx=(0, 10), pady=(8, 12), sticky="w")

        self.result_label = ctk.CTkLabel(self.main_frame, text="Hidden Message:")
        self.result_label.grid(row=5, column=0, padx=15, pady=(10, 5), sticky="nw")

        self.result_box = ctk.CTkTextbox(self.main_frame)
        self.result_box.grid(row=6, column=0, columnspan=3, padx=15, pady=(5, 12), sticky="nsew")

        self.status_var = ctk.StringVar(value="Ready.")
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            textvariable=self.status_var,
            anchor="w"
        )
        self.status_label.grid(row=7, column=0, columnspan=3, padx=15, pady=(10, 5), sticky="w")

    def browse_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Encoded Image",
            filetypes=[
                ("Common Image formats", "*.png;*.jpg;*.jpeg;*.bmp"),
                ("All image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.tif;*.tiff"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            try:
                from PIL import Image
                with Image.open(file_path) as img:
                    img.convert("RGB")
                self.image_path_var.set(file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Invalid or unsupported image file: {str(e)}")

    def handle_decode(self):
        image_path = self.image_path_var.get().strip()
        password = self.password_var.get().strip()

        if not image_path:
            self.status_var.set("Please select an encoded image.")
            messagebox.showerror("Error", "Please select an encoded image.")
            return

        if not password:
            self.status_var.set("Please enter the password.")
            messagebox.showerror("Error", "Please enter the password.")
            return

        if not os.path.exists(image_path):
            self.status_var.set("Selected image file does not exist.")
            messagebox.showerror("Error", "Selected image file does not exist.")
            return

        self.result_box.delete("1.0", "end")
        self.status_var.set("Decoding...")

        algorithm = self.algorithm_var.get()

        try:
            if algorithm == "Standard LSB":
                from algorithms.lsb_decode import decode_image as decode_func
            else:
                from algorithms.random_lsb import decode_image as decode_func

            decoded_message = decode_func(image_path, password)
            self.result_box.insert("1.0", decoded_message)
            log_decode(algorithm=algorithm)
            self.status_var.set("Decode completed successfully.")
        except Exception as exc:
            self.status_var.set("Decode failed.")
            log_error(f"DECODE failed: {exc}")
            messagebox.showerror(
                "Decode Failed",
                "Decoding failed.\n\n"
                "Possible reasons:\n"
                "• Incorrect password.\n"
                "• Wrong steganography algorithm selected."
            )