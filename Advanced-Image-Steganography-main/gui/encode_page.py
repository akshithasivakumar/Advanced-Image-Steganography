import os
import threading
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from utils.capacity import can_embed
from utils.email import send_mail
from utils.file_manager import (
    ensure_directories,
    generate_output_filename,
    validate_file_path,
)
from utils.logger import log_encode, log_error


class EncodePage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(fg_color="transparent")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.current_key = None
        self.output_path = None

        self.title_label = ctk.CTkLabel(
            self,
            text="Encode Secret Message",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.main_frame.grid_columnconfigure(1, weight=1)

        self.cover_label = ctk.CTkLabel(self.main_frame, text="Cover Image:")
        self.cover_label.grid(row=0, column=0, padx=15, pady=12, sticky="w")

        self.cover_path_var = ctk.StringVar(value="")
        self.cover_entry = ctk.CTkEntry(self.main_frame, textvariable=self.cover_path_var)
        self.cover_entry.grid(row=0, column=1, padx=(0, 10), pady=12, sticky="ew")

        self.browse_cover_button = ctk.CTkButton(
            self.main_frame,
            text="Browse",
            command=self.browse_cover_image,
            width=100
        )
        self.browse_cover_button.grid(row=0, column=2, padx=(0, 15), pady=12)

        self.output_label = ctk.CTkLabel(self.main_frame, text="Output Image:")
        self.output_label.grid(row=1, column=0, padx=15, pady=12, sticky="w")

        self.output_path_var = ctk.StringVar(value="")
        self.output_entry = ctk.CTkEntry(self.main_frame, textvariable=self.output_path_var)
        self.output_entry.grid(row=1, column=1, padx=(0, 10), pady=12, sticky="ew")

        self.browse_output_button = ctk.CTkButton(
            self.main_frame,
            text="Select",
            command=self.browse_output_image,
            width=100
        )
        self.browse_output_button.grid(row=1, column=2, padx=(0, 15), pady=12)

        self.message_label = ctk.CTkLabel(self.main_frame, text="Secret Message:")
        self.message_label.grid(row=2, column=0, padx=15, pady=(12, 5), sticky="nw")

        self.message_box = ctk.CTkTextbox(self.main_frame, height=120)
        self.message_box.grid(row=2, column=1, padx=(0, 10), pady=(12, 8), sticky="nsew")

        self.email_label = ctk.CTkLabel(self.main_frame, text="Receiver Email:")
        self.email_label.grid(row=3, column=0, padx=15, pady=12, sticky="w")

        self.email_var = ctk.StringVar(value="")
        self.email_entry = ctk.CTkEntry(self.main_frame, textvariable=self.email_var)
        self.email_entry.grid(row=3, column=1, padx=(0, 10), pady=12, sticky="ew")

        self.password_label = ctk.CTkLabel(self.main_frame, text="Password:")
        self.password_label.grid(row=4, column=0, padx=15, pady=12, sticky="w")

        self.password_var = ctk.StringVar(value="")
        self.password_entry = ctk.CTkEntry(self.main_frame, textvariable=self.password_var, show="*")
        self.password_entry.grid(row=4, column=1, padx=(0, 10), pady=12, sticky="ew")

        self.algorithm_label = ctk.CTkLabel(self.main_frame, text="Algorithm:")
        self.algorithm_label.grid(row=5, column=0, padx=15, pady=(12, 5), sticky="nw")

        self.algorithm_var = ctk.StringVar(value="Standard LSB")
        self.algorithm_combo = ctk.CTkOptionMenu(
            self.main_frame,
            values=["Standard LSB", "Random LSB"],
            variable=self.algorithm_var,
            width=200
        )
        self.algorithm_combo.grid(row=5, column=1, padx=(0, 10), pady=(12, 5), sticky="nw")

        self.algorithm_hint = ctk.CTkLabel(
            self.main_frame,
            text="Use the same algorithm that was selected during encoding.",
            font=ctk.CTkFont(size=11, slant="italic"),
            text_color=("gray60", "gray40")
        )
        self.algorithm_hint.grid(row=6, column=0, columnspan=2, padx=15, pady=(0, 8), sticky="w")

        self.button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.button_frame.grid(row=7, column=1, padx=(0, 10), pady=(8, 12), sticky="w")

        self.encode_button = ctk.CTkButton(
            self.button_frame,
            text="Encode",
            command=self.handle_encode,
            width=120
        )
        self.encode_button.pack(side="left", padx=(0, 10))

        self.send_button = ctk.CTkButton(
            self.button_frame,
            text="Send Email",
            command=self.handle_send_email,
            width=120
        )
        self.send_button.pack(side="left")

        self.status_var = ctk.StringVar(value="Ready.")
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            textvariable=self.status_var,
            anchor="w"
        )
        self.status_label.grid(row=8, column=0, columnspan=3, padx=15, pady=(12, 5), sticky="w")

    def browse_cover_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Cover Image",
            filetypes=[
                ("Common Image formats", "*.png;*.jpg;*.jpeg;*.bmp"),
                ("All image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.tif;*.tiff"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            # Validate that the selected file is readable as an image
            try:
                from PIL import Image
                with Image.open(file_path) as img:
                    img.convert("RGB")  # Test conversion
                self.cover_path_var.set(file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Invalid or unsupported image file: {str(e)}")

    def _get_default_output_path(self):
        project_root = Path(__file__).resolve().parent.parent
        output_dir = project_root / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        current_value = self.output_path_var.get().strip()
        existing_suffix = Path(current_value).suffix if current_value else ""
        extension = existing_suffix or ".png"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"IMG_{timestamp}{extension}"
        return output_dir / default_name

    def browse_output_image(self):
        ensure_directories()

        cover_path = self.cover_path_var.get().strip()
        if cover_path:
            default_output_path = Path(generate_output_filename(cover_path))
        else:
            default_output_path = self._get_default_output_path()

        file_path = filedialog.asksaveasfilename(
            title="Save Encoded Image As",
            initialdir=str(default_output_path.parent),
            initialfile=default_output_path.name,
            defaultextension=default_output_path.suffix or ".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if file_path:
            self.output_path_var.set(file_path)
            self.output_path = file_path

    def handle_encode(self):
        ensure_directories()

        cover_path = self.cover_path_var.get().strip()
        output_path = self.output_path_var.get().strip()
        message = self.message_box.get("1.0", "end").strip()
        password = self.password_var.get().strip()

        if not cover_path:
            self.status_var.set("Please select a cover image.")
            messagebox.showerror("Error", "Please select a cover image.")
            return

        if not validate_file_path(cover_path):
            self.status_var.set("Selected cover image path is invalid.")
            messagebox.showerror("Error", "Selected cover image path is invalid.")
            return

        if not output_path:
            output_path = generate_output_filename(cover_path)
            self.output_path_var.set(output_path)
            self.output_path = output_path

        output_path_obj = Path(output_path)
        if output_path_obj.exists():
            self.status_var.set("Output file already exists. Choose a different filename.")
            messagebox.showerror("Error", "Output file already exists. Choose a different filename.")
            return

        if not message:
            self.status_var.set("Please enter a secret message.")
            messagebox.showerror("Error", "Please enter a secret message.")
            return

        if not password:
            self.status_var.set("Please enter a password.")
            messagebox.showerror("Error", "Please enter a password.")
            return

        if not can_embed(cover_path, message):
            self.status_var.set("Message is too large to fit in the selected image.")
            messagebox.showerror("Error", "Message is too large to fit in the selected image.")
            return

        try:
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            self.status_var.set("Permission denied: Cannot write to output directory.")
            messagebox.showerror("Error", "Permission denied: Cannot write to output directory.")
            return
        except OSError as e:
            self.status_var.set(f"Failed to create output directory: {e}")
            messagebox.showerror("Error", f"Failed to create output directory: {e}")
            return

        try:
            if not can_embed(cover_path, message):
                self.status_var.set("Message is too large to fit in the selected image.")
                messagebox.showerror("Error", "Message is too large to fit in the selected image.")
                return

            algorithm = self.algorithm_var.get()
            if algorithm == "Standard LSB":
                from algorithms.lsb_encode import encode_image as encode_func
            else:  # Random LSB
                from algorithms.random_lsb import encode_image as encode_func

            encode_func(cover_path, str(output_path_obj), message, password)
            self.current_key = password.encode("utf-8")
            self.status_var.set("Encoding completed successfully.")
            log_encode(algorithm=algorithm)
            messagebox.showinfo("Success", "Image encoded successfully.")
        except Exception as exc:
            self.current_key = None
            self.status_var.set(f"Encoding failed: {exc}")
            log_error(f"ENCODE failed: {exc}")
            messagebox.showerror("Error", str(exc))

    def handle_send_email(self):
        receiver_email = self.email_var.get().strip()
        if not self.current_key:
            self.status_var.set("Encode an image first before sending email.")
            messagebox.showerror("Error", "Encode an image first before sending email.")
            return

        if not receiver_email:
            self.status_var.set("Please enter a receiver email address.")
            messagebox.showerror("Error", "Please enter a receiver email address.")
            return

        if not self.output_path:
            self.status_var.set("Please select an output image path.")
            messagebox.showerror("Error", "Please select an output image path.")
            return

        if not os.path.exists(self.output_path):
            self.status_var.set("Encoded image file does not exist.")
            messagebox.showerror("Error", "Encoded image file does not exist.")
            return

        confirm = messagebox.askyesno(
            "Confirm Email Send",
            f"Send encoded image to:\n\n  {receiver_email}\n\n"
            f"Click Yes to proceed, No to cancel."
        )
        if not confirm:
            self.status_var.set("Email send cancelled.")
            return

        try:
            loading_window = ctk.CTkToplevel(self)
            loading_window.title("Sending Email")
            loading_window.geometry("260x100")
            loading_window.transient(self.winfo_toplevel())
            ctk.CTkLabel(loading_window, text="Sending encoded image...").pack(expand=True, pady=20)

            thread = threading.Thread(
                target=send_mail,
                args=(receiver_email, self.output_path, self.current_key, loading_window),
                daemon=True
            )
            thread.start()
        except Exception as exc:
            self.status_var.set(f"Email sending failed: {exc}")
            if self.winfo_exists():
                messagebox.showerror("Error", str(exc))