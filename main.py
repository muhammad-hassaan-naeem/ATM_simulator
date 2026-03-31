import tkinter as tk
from PIL import Image, ImageTk
import os
from playsound import playsound  # 🔊 make sure you `pip install playsound==1.2.2`

# Mock functions
try:
    from login import open_login
    from signup import open_signup
except ImportError:
    def open_login(): print("Login script triggered!")
    def open_signup(): print("Signup script triggered!")

# --------- Paths ---------
def find_file(base_name, folder):
    for ext in (".png", ".jpg", ".jpeg"):
        path = os.path.join(folder, base_name + ext)
        if os.path.exists(path):
            return path
    return None

ICONS_FOLDER = r"C:\Users\pc\Desktop\ATM_Project\icons"
BG_PATH = find_file("background", ICONS_FOLDER)
LOGO_PATH = find_file("logo", ICONS_FOLDER)

class ATMApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ATM Simulator")
        self.root.state("zoomed")

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        self.canvas = tk.Canvas(
            self.root,
            width=self.screen_width,
            height=self.screen_height,
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        self._setup_ui()

    def _setup_ui(self):
        self.canvas.delete("all")

        # Background
        try:
            if BG_PATH:
                bg_img = Image.open(BG_PATH).resize(
                    (self.screen_width, self.screen_height), 
                    Image.Resampling.LANCZOS
                )
                self.bg_photo = ImageTk.PhotoImage(bg_img)
                self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
        except:
            self.canvas.configure(bg="#0f172a")

        # Logo
        try:
            if LOGO_PATH:
                logo_img = Image.open(LOGO_PATH).resize((90, 90), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_img)
                self.canvas.create_image(120, 90, image=self.logo_photo, anchor="w")
        except: pass

        self.canvas.create_text(
            230, 85, text="ATM SIMULATOR", 
            font=("Montserrat", 44, "bold"), 
            fill="#ffffff", anchor="w"
        )

        btn_color = "#1e293b"
        btn_hover = "#334155"
        exit_color = "#991b1b"
        exit_hover = "#ef4444"

        center_x = self.screen_width // 2
        start_y = self.screen_height // 2 - 80

        # Buttons
        self._create_rounded_button(center_x, start_y, 320, 60, "SIGN IN", btn_color, btn_hover, open_login)
        self.canvas.create_text(center_x, start_y + 55, text="Access your existing account",
                                font=("Segoe UI", 18, "bold"), fill="#f8fafc")

        self._create_rounded_button(center_x, start_y + 150, 320, 60, "SIGN UP", btn_color, btn_hover, open_signup)
        self.canvas.create_text(center_x, start_y + 205, text="Create a new secure account",
                                font=("Segoe UI", 18, "bold"), fill="#f8fafc")

        self._create_rounded_button(center_x, start_y + 300, 320, 60, "EXIT", exit_color, exit_hover, self.exit_with_sound)

    def exit_with_sound(self):
        sound_path = os.path.join(os.getcwd(), "sounds", "thanks_message.wav")
        if os.path.exists(sound_path):
            try:
                playsound(sound_path)  # 🔊 Blocking play — will finish before closing
            except Exception as e:
                print("Sound error:", e)
        else:
            print("Sound file not found:", sound_path)
        self.root.destroy()  # Close after sound finishes

    def _create_rounded_button(self, x, y, width, height, text, color, hover_color, command):
        radius = 25
        rect = self._create_round_rect(x - width / 2, y - height / 2, x + width / 2, y + height / 2,
                                       radius, fill=color, outline="")
        txt = self.canvas.create_text(x, y, text=text, fill="white", font=("Montserrat", 16, "bold"))

        def on_enter(e): self.canvas.itemconfig(rect, fill=hover_color)
        def on_leave(e): self.canvas.itemconfig(rect, fill=color)

        self.canvas.tag_bind(rect, "<Button-1>", lambda e: command())
        self.canvas.tag_bind(txt, "<Button-1>", lambda e: command())
        for item in (rect, txt):
            self.canvas.tag_bind(item, "<Enter>", on_enter)
            self.canvas.tag_bind(item, "<Leave>", on_leave)

    def _create_round_rect(self, x1, y1, x2, y2, r=25, **kwargs):
        points = [
            x1+r, y1, x2-r, y1, x2, y1, x2, y1+r,
            x2, y2-r, x2, y2, x2-r, y2, x1+r, y2,
            x1, y2, x1, y2-r, x1, y1+r, x1, y1
        ]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)


if __name__ == "__main__":
    root = tk.Tk()
    app = ATMApp(root)
    root.mainloop()