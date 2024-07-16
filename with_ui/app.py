import os.path
from tkinter import filedialog

import customtkinter as ctk

from decrypter.decrypter import decrypt_pack

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    MAX_CHAR_329 = 12

    def __init__(self):
        super().__init__()

        self.title("Pack Decrypter")
        self.geometry("475x630")

        self.pack_path = ctk.StringVar()
        self.key_path = ctk.StringVar()
        self.save_path = ctk.StringVar()
        self.progress = ctk.DoubleVar()

        self.button_font = ctk.CTkFont(size=40, weight="bold", family="inter")

        self.title_label = ctk.CTkLabel(self, text="Pack Decrypter",
                                        font=ctk.CTkFont(size=48, weight="bold", family="inter"), text_color="#3870FF")
        self.title_label.pack(pady=(25, 25))

        self.browse_pack_button = ctk.CTkButton(self, text="Pack", command=self.browse_pack, fg_color="#2950B5",
                                                width=329, height=57, corner_radius=11, font=self.button_font,
                                                hover_color="#254AA9")
        self.browse_pack_button.pack(pady=(25, 20))

        self.browse_key_button = ctk.CTkButton(self, text="Key", command=self.browse_key, fg_color="#2950B5", width=329,
                                               height=57, corner_radius=11, font=self.button_font,
                                               hover_color="#254AA9")
        self.browse_key_button.pack(pady=(25, 20))

        self.browse_save_button = ctk.CTkButton(self, text="Save", command=self.browse_save, fg_color="#2950B5",
                                                width=329, height=57, corner_radius=11, font=self.button_font,
                                                hover_color="#254AA9")
        self.browse_save_button.pack(pady=(25, 20))

        self.decrypt_button = ctk.CTkButton(self, text="Decrypt", fg_color="#383838", width=329, height=108,
                                            corner_radius=11, font=self.button_font, hover_color="#383838",
                                            state="disabled", command=self.submit)
        self.decrypt_button.pack(pady=(25, 10))

        self.progress_bar = ctk.CTkProgressBar(self, mode="determinate", variable=self.progress, height=21, width=329,
                                               progress_color="#29B561")

        self.status_label = ctk.CTkLabel(self, text="Success !", text_color="#29B561", font=ctk.CTkFont(size=35))

        self.clear_button = ctk.CTkButton(self, text="Clear", font=self.button_font, height=80, width=329,
                                          corner_radius=11,
                                          fg_color="#FF6262", hover_color="#C14A4A", command=self.clear)

    def update(self):
        if self.pack_path.get() != "" and self.key_path.get() != "" and self.save_path.get() != "":
            self.decrypt_button.configure(fg_color="#29B561", hover_color="#239A53", state="normal")
            print("update")
        super().update()

    def browse_pack(self):
        file_path = filedialog.askopenfilename(filetypes=[(".zip", "*.zip"), (".mcpack", "*.mcpack")])
        if file_path:
            self.pack_path.set(file_path)
            name = os.path.basename(file_path)
            name_len = len(name)
            size = 40
            if name_len > self.MAX_CHAR_329:
                ext = name.split(os.path.extsep)[len(name.split(os.path.extsep)) - 1]
                name = name[:12] + "..." + ext
                size = 25
            self.browse_pack_button.configure(font=ctk.CTkFont(size=size, family="inter", weight="bold"), text=name)

    def browse_key(self):
        file_path = filedialog.askopenfilename(filetypes=[(".key", "*.key"), (".txt", "*.txt")])
        if file_path:
            self.key_path.set(file_path)
            self.update()
            name = os.path.basename(file_path)
            name_len = len(name)
            print(name_len)
            size = 40
            if name_len > self.MAX_CHAR_329:
                ext = name.split(os.path.extsep)[len(name.split(os.path.extsep)) - 1]
                name = name[:12] + "..." + ext
                size = 25
            self.browse_key_button.configure(font=ctk.CTkFont(size=size, family="inter", weight="bold"), text=name)

    def browse_save(self):
        file_path = filedialog.askdirectory()
        if file_path:
            self.save_path.set(file_path)
            self.update()
            name = os.path.basename(file_path)
            name_len = len(name)
            size = 40
            if name_len > self.MAX_CHAR_329:
                name = name[:12] + "..."
                size = 25
            self.browse_save_button.configure(font=ctk.CTkFont(size=size, family="inter", weight="bold"), text=name)

    def reset_paths(self):
        self.pack_path.set("")
        self.key_path.set("")
        self.save_path.set("")

    def submit(self):
        self.decrypt_button.destroy()
        self.progress_bar.pack(pady=(50, 10))

        with open(self.key_path.get(), "rb") as key_file:
            key = key_file.read()
            key_file.close()

        name = os.path.basename(self.pack_path.get())
        try:
            decrypted_data = decrypt_pack(key, self.pack_path.get(), self.progress, self.progress_bar)
        except Exception:
            self.status_label.configure(text="Failure !", text_color="#FF6262")
            self.progress_bar.configure(progress_color="#FF6262")
            self.status_label.pack(pady=(35, 10))
            self.do_end()
            return
        with open(os.path.join(self.save_path.get(), f"{name}_decrypted.zip"), "wb+") as save_file:
            save_file.write(decrypted_data)
            save_file.close()
        self.reset_paths()
        self.status_label.pack(pady=(35, 10))
        self.do_end()

    def clear(self):
        self.destroy()
        app_2 = App()
        app_2.mainloop()

    def do_end(self):
        self.reset_paths()
        self.update()
        self.status_label.after(3500)
        self.progress_bar.destroy()
        self.status_label.destroy()
        self.clear_button.pack(pady=(50, 10))


if __name__ == "__main__":
    app = App()
    app.mainloop()
