# gui.py
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import webbrowser
import platform
import categories.image_stego as image_stego
import categories.audio_stego as audio_stego
import categories.text_stego as text_stego
import categories.video_stego as video_stego

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Change these if your shortcuts are in different paths
DEEGGER_LNK_PATH = video_stego.DEEGGER_LNK_PATH
class AdvancedStegoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Steganography Suite")
        window_width = 1000
        window_height = 720
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - window_width)//2
        y = (screen_h - window_height)//2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(900, 600)

        # Internal state
        self.category_methods = {
            "Image": ["LSB", "Parity", "BitPlane"],
            "Audio": ["LSB", "Parity", "Phase", "Echo"],
            "Text": ["ZW", "Parity", "Whitespace"],
            "Video": ["DeEgger Hide", "DeEgger Extract"],
        }
        self.current_file = None
        self.output_dir = os.path.join(os.getcwd(), "Output")
        os.makedirs(self.output_dir, exist_ok=True)

        self.build_ui()

    def build_ui(self):
        # Root layout: Top header, control row, center area
        header = ctk.CTkFrame(self.root, fg_color="#0F1720")
        header.pack(fill="x", padx=12, pady=8)
        ctk.CTkLabel(header, text="Steganography Suite", font=("Roboto", 20, "bold")).pack(side="left", padx=12)
        ctk.CTkButton(header, text="Open Output Folder", command=self.open_output_folder, width=160).pack(side="right", padx=12)

        # Controls frame
        controls = ctk.CTkFrame(self.root)
        controls.pack(fill="x", padx=12, pady=6)

        # Category
        ctk.CTkLabel(controls, text="Category:", anchor="w").grid(row=0, column=0, padx=8, pady=10, sticky="w")
        self.category_var = tk.StringVar(value="Image")
        self.category_menu = ctk.CTkOptionMenu(controls, values=list(self.category_methods.keys()),
                                                variable=self.category_var, command=self.on_category_change, width=160)
        self.category_menu.grid(row=0, column=1, padx=8, pady=10, sticky="w")

        # Method
        ctk.CTkLabel(controls, text="Method:", anchor="w").grid(row=0, column=2, padx=8, pady=10, sticky="w")
        self.method_var = tk.StringVar(value=self.category_methods["Image"][0])
        self.method_menu = ctk.CTkOptionMenu(controls, values=self.category_methods["Image"], variable=self.method_var, command=self.on_method_change, width=160)
        self.method_menu.grid(row=0, column=3, padx=8, pady=10, sticky="w")

        # File selector
        self.file_label = ctk.CTkLabel(controls, text="No file selected", width=40)
        self.file_label.grid(row=1, column=0, columnspan=2, padx=8, pady=(0,12), sticky="w")
        self.select_btn = ctk.CTkButton(controls, text="Select File", command=self.select_file)
        self.select_btn.grid(row=1, column=3, padx=8, pady=(0,12), sticky="e")

        # Message entry
        main_area = ctk.CTkFrame(self.root)
        main_area.pack(fill="both", expand=True, padx=12, pady=8)

        left = ctk.CTkFrame(main_area)
        left.pack(side="left", fill="both", expand=True, padx=(0,6), pady=6)

        right = ctk.CTkFrame(main_area, width=320)
        right.pack(side="right", fill="y", padx=(6,0), pady=6)

        # Shared message field (large)
        ctk.CTkLabel(left, text="Message (hide/extract)", anchor="w").pack(anchor="w", padx=8, pady=(8,4))
        self.msg_text = ctk.CTkTextbox(left, width=600, height=220, corner_radius=8, fg_color="#0B1220")
        self.msg_text.pack(fill="x", padx=8, pady=(0,12))

        # Per-method parameters area (dynamically shown)
        ctk.CTkLabel(left, text="Method Parameters", anchor="w").pack(anchor="w", padx=8, pady=(4,4))
        self.params_frame = ctk.CTkFrame(left, fg_color="#071018")
        self.params_frame.pack(fill="x", padx=8, pady=(0,12))

        # Default parameter widgets (hidden/shown dynamically)
        # Bit plane (integer)
        self.plane_var = tk.IntVar(value=1)
        self.plane_widget = None

        # Echo delay
        self.echo_delay_var = tk.IntVar(value=120)
        self.echo_widget = None

        # Buttons: Hide / Extract
        btns = ctk.CTkFrame(left)
        btns.pack(fill="x", padx=8, pady=(0,12))
        self.hide_btn = ctk.CTkButton(btns, text="Hide", fg_color="#28A745", hover_color="#3CC45F", command=self.on_hide)
        self.hide_btn.pack(side="left", padx=8, pady=6)
        self.extract_btn = ctk.CTkButton(btns, text="Extract", fg_color="#FFC107", hover_color="#FFDB58", text_color="#111", command=self.on_extract)
        self.extract_btn.pack(side="left", padx=8, pady=6)

        # Right panel: Info & Tools
        ctk.CTkLabel(right, text="Info & Tools", anchor="w").pack(anchor="w", padx=8, pady=(8,4))
        self.info_box = ctk.CTkTextbox(right, height=320, width=300, state="disabled")
        self.info_box.pack(padx=8, pady=(0,12))

        ctk.CTkButton(right, text="Open DeEgger", command=self.open_deegger).pack(fill="x", padx=8, pady=6)
        ctk.CTkButton(right, text="Reset", command=self.reset).pack(fill="x", padx=8, pady=6)

        # Initialize parameter widgets for initial method
        self.on_category_change(self.category_var.get())
        self.on_method_change(self.method_var.get())

    # ----------------- UI Helpers -----------------
    def on_category_change(self, cat):
        methods = self.category_methods.get(cat, [])
        self.method_menu.configure(values=methods)
        if methods:
            self.method_var.set(methods[0])
        # Update file select button label and clear current_file
        if cat == "Image":
            self.select_btn.configure(text="Select Image")
            self.file_label.configure(text="No image selected")
            self.current_file = None
        elif cat == "Audio":
            self.select_btn.configure(text="Select Audio (WAV)")
            self.file_label.configure(text="No audio selected")
            self.current_file = None
        elif cat == "Text":
            self.select_btn.configure(text="Select Text File")
            self.file_label.configure(text="No text file selected")
            self.current_file = None
        elif cat == "Video":
            self.select_btn.configure(text="Select Video")
            self.file_label.configure(text="No video selected")
            self.current_file = None
        # refresh params
        self.on_method_change(self.method_var.get())

    def on_method_change(self, method):
        # Clear params frame
        for w in self.params_frame.winfo_children():
            w.destroy()
        # Show parameters depending on method
        if method == "BitPlane":
            ctk.CTkLabel(self.params_frame, text="Bit Plane (0-7):").pack(side="left", padx=8, pady=8)
            self.plane_widget = ctk.CTkEntry(self.params_frame, width=80, textvariable=self.plane_var)
            self.plane_widget.pack(side="left", padx=8, pady=8)
        elif method == "Echo":
            ctk.CTkLabel(self.params_frame, text="Echo Delay (samples):").pack(side="left", padx=8, pady=8)
            self.echo_widget = ctk.CTkEntry(self.params_frame, width=120, textvariable=self.echo_delay_var)
            self.echo_widget.pack(side="left", padx=8, pady=8)
        else:
            # no params
            ctk.CTkLabel(self.params_frame, text="(No parameters for this method)").pack(anchor="w", padx=8, pady=8)

    def select_file(self):
        cat = self.category_var.get()
        if cat == "Image":
            path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg")])
        elif cat == "Audio":
            path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        elif cat == "Text":
            path = filedialog.askopenfilename(filetypes=[("Text", "*.txt")])
        elif cat == "Video":
            path = filedialog.askopenfilename(filetypes=[("Videos", "*.mp4 *.avi *.mov")])
        else:
            path = filedialog.askopenfilename()
        if path:
            self.current_file = path
            self.file_label.configure(text=os.path.basename(path))
            self.log(f"Selected: {path}")

    def get_message_text(self):
        return self.msg_text.get("0.0", "end-1c")

    def log(self, text, clear=False):
        self.info_box.configure(state="normal")
        if clear:
            self.info_box.delete("0.0", "end")
        self.info_box.insert("end", text + "\n")
        self.info_box.see("end")
        self.info_box.configure(state="disabled")

    def open_output_folder(self):
        path = self.output_dir
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        if platform.system() == "Windows":
            os.startfile(path)
        else:
            webbrowser.open(path)

    def open_deegger(self):
        try:
            if os.path.exists(DEEGGER_LNK_PATH):
                os.startfile(DEEGGER_LNK_PATH)
                self.log("Opened DeEgger (shortcut).")
            else:
                raise FileNotFoundError("DeEgger shortcut not found; update DEEGGER_LNK_PATH in code.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def reset(self):
        self.current_file = None
        self.file_label.configure(text="No file selected")
        self.msg_text.delete("0.0", "end")
        self.log("State reset", clear=True)

    # ----------------- Operations -----------------
    def on_hide(self):
        cat = self.category_var.get()
        method = self.method_var.get()
        msg = self.get_message_text()
        if cat != "Video" and (not self.current_file or not os.path.exists(self.current_file)):
            messagebox.showerror("Error", "Please select a file first")
            return
        if not msg:
            messagebox.showerror("Error", "Please enter a message to hide")
            return

        try:
            out_name = None
            if cat == "Image":
                out_name = os.path.join(self.output_dir, "output_image.png")
                if method == "LSB":
                    image_stego.hide_lsb_image(self.current_file, msg, out_name)
                elif method == "Parity":
                    image_stego.hide_parity_image(self.current_file, msg, out_name)
                elif method == "BitPlane":
                    plane = max(0, min(7, int(self.plane_var.get()))) if self.plane_widget else 1
                    image_stego.hide_bitplane_image(self.current_file, msg, out_name, plane=plane)

            elif cat == "Audio":
                out_name = os.path.join(self.output_dir, "output_audio.wav")
                if method == "LSB":
                    audio_stego.hide_audio_lsb(self.current_file, msg, out_name)
                elif method == "Parity":
                    audio_stego.hide_audio_parity(self.current_file, msg, out_name)
                elif method == "Phase":
                    audio_stego.hide_audio_phase(self.current_file, msg, out_name)
                elif method == "Echo":
                    delay = int(self.echo_delay_var.get()) if self.echo_widget else 120
                    audio_stego.hide_audio_echo(self.current_file, msg, out_name, delay_samples=delay)

            elif cat == "Text":
                out_name = os.path.join(self.output_dir, "output_text.txt")
                with open(self.current_file, "r", encoding="utf-8") as f:
                    cover = f.read()
                if method == "ZW":
                    hidden = text_stego.hide_zw(cover, msg)
                elif method == "Parity":
                    hidden = text_stego.hide_parity_text(cover, msg)
                else:
                    hidden = text_stego.hide_whitespace(cover, msg)
                with open(out_name, "w", encoding="utf-8") as f:
                    f.write(hidden)

            elif cat == "Video":
                # Video uses DeEgger which is manual; we open DeEgger and create the message file
                info = video_stego.hide_video_deegger(self.current_file, msg, lnk_path=DEEGGER_LNK_PATH)
                self.log(f"DeEgger instructions:\nHost: {info['host']}\nEmbed file: {info['embed']}")
                messagebox.showinfo("DeEgger", f"DeEgger opened. Embed file created at:\n{info['embed']}\nFollow instructions in the info panel.")
                return

            self.log(f"Hidden message -> {out_name}")
            messagebox.showinfo("Success", f"Hidden message saved to:\n{out_name}")
            # auto-open output folder

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.log(f"Error: {e}")

    def on_extract(self):
        cat = self.category_var.get()
        method = self.method_var.get()

        # For extraction, audio/image/text need selected file; for video user picks extracted .txt
        try:
            if cat == "Image":
                if not self.current_file:
                    messagebox.showerror("Error", "Select image file first")
                    return
                if method == "LSB":
                    msg = image_stego.extract_lsb_image(self.current_file)
                elif method == "Parity":
                    msg = image_stego.extract_parity_image(self.current_file)
                else:
                    plane = max(0, min(7, int(self.plane_var.get()))) if self.plane_widget else 1
                    msg = image_stego.extract_bitplane_image(self.current_file, plane=plane)
                self.msg_text.delete("0.0", "end")
                self.msg_text.insert("0.0", msg or "")

            elif cat == "Audio":
                if not self.current_file:
                    messagebox.showerror("Error", "Select audio file first")
                    return
                if method == "LSB":
                    msg = audio_stego.extract_audio_lsb(self.current_file)
                elif method == "Parity":
                    msg = audio_stego.extract_audio_parity(self.current_file)
                elif method == "Phase":
                    msg = audio_stego.extract_audio_phase(self.current_file)
                else:
                    delay = int(self.echo_delay_var.get()) if self.echo_widget else 120
                    msg = audio_stego.extract_audio_echo(self.current_file, delay_samples=delay)
                self.msg_text.delete("0.0", "end")
                self.msg_text.insert("0.0", msg or "")

            elif cat == "Text":
                if not self.current_file:
                    messagebox.showerror("Error", "Select text file first")
                    return
                with open(self.current_file, "r", encoding="utf-8") as f:
                    cover = f.read()
                if method == "ZW":
                    msg = text_stego.extract_zw(cover)
                elif method == "Parity":
                    msg = text_stego.extract_parity_text(cover)
                else:
                    msg = text_stego.extract_whitespace(cover)
                self.msg_text.delete("0.0", "end")
                self.msg_text.insert("0.0", msg or "")

            elif cat == "Video":
                # For video extraction we ask user to select the extracted text file produced by DeEgger
                extracted = filedialog.askopenfilename(title="Select extracted .txt from DeEgger", filetypes=[("Text files", "*.txt")])
                if not extracted:
                    return
                msg = video_stego.extract_video_deegger(extracted)
                self.msg_text.delete("0.0", "end")
                self.msg_text.insert("0.0", msg or "")

            messagebox.showinfo("end", msg if msg else "[No message found]")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.log(f"Error: {e}")

if __name__ == "__main__":
    root = ctk.CTk()
    app = AdvancedStegoGUI(root)
    root.mainloop()