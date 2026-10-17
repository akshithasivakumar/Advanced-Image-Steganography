import customtkinter as ctk


class HomePage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent)

        self.configure(fg_color="transparent")

        # Configure Grid
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Advanced Image Steganography",
            font=ctk.CTkFont(size=30, weight="bold")
        )
        self.title_label.grid(
            row=0,
            column=0,
            pady=(40, 10),
            sticky="n"
        )

        # Subtitle
        self.subtitle = ctk.CTkLabel(
            self,
            text="Secure Image Hiding Using LSB Steganography",
            font=ctk.CTkFont(size=18)
        )
        self.subtitle.grid(
            row=1,
            column=0,
            pady=(0, 20),
            sticky="n"
        )

        # Information Frame
        self.info_frame = ctk.CTkFrame(self)

        self.info_frame.grid(
            row=2,
            column=0,
            padx=50,
            pady=10,
            sticky="nsew"
        )

        self.info_frame.grid_columnconfigure(0, weight=1)

        description = (
            "This application provides a secure method for hiding secret "
            "messages inside digital images using Least Significant Bit (LSB) "
            "Steganography.\n\n"
            "The message is encrypted before embedding to improve security. "
            "The encoded image can later be decoded using the correct "
            "decryption key."
        )

        self.description_label = ctk.CTkLabel(
            self.info_frame,
            text=description,
            justify="left",
            wraplength=700,
            font=ctk.CTkFont(size=15)
        )

        self.description_label.pack(
            padx=25,
            pady=(25, 15),
            anchor="w"
        )

        features = (
            "Features\n\n"
            "• Encode secret messages into images\n"
            "• Decode hidden messages\n"
            "• AES (Fernet) encryption support\n"
            "• Email encoded image\n"
            "• Activity logging\n"
            "• Payload capacity estimation\n"
            "• Random LSB support"
        )

        self.features_label = ctk.CTkLabel(
            self.info_frame,
            text=features,
            justify="left",
            font=ctk.CTkFont(size=15)
        )

        self.features_label.pack(
            padx=25,
            pady=(0, 25),
            anchor="w"
        )

        # Footer
        self.footer = ctk.CTkLabel(
            self,
            text="Use the navigation panel on the left to access different modules.",
            font=ctk.CTkFont(size=14)
        )

        self.footer.grid(
            row=3,
            column=0,
            pady=(15, 30)
        )