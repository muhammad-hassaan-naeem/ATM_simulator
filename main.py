"""
main.py — ATM Simulator entry point and home screen.

Changes from original:
- All hardcoded C:\\Users\\pc\\... paths replaced with relative paths
  resolved from this file's location using pathlib.
- root.state("zoomed") wrapped in a cross-platform helper.
- playsound replaced with sound.play_sound_blocking.
- Database initialised on startup (creates tables if missing).
- Bare except clauses replaced with except Exception.
- Logging configured for the whole application.
"""

import logging
import tkinter as tk
from pathlib import Path

from PIL import Image, ImageTk

from db_config import init_database
from sound import play_sound_blocking

# ── logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ── project paths ─────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent
ICONS_DIR   = BASE_DIR / "icons"
SOUNDS_DIR  = BASE_DIR / "sounds"


def _find_image(stem: str, folder: Path) -> Path | None:
    """Return the first existing image with the given stem, or None."""
    for ext in (".png", ".jpg", ".jpeg", ".JPG", ".JPEG"):
        p = folder / (stem + ext)
        if p.exists():
            return p
    return None


BG_PATH   = _find_image("background", ICONS_DIR)
LOGO_PATH = _find_image("logo", ICONS_DIR)


# ── cross-platform window maximise ────────────────────────────────────────────
def maximize_window(win: tk.Tk | tk.Toplevel) -> None:
    """Maximise a Tkinter window on Windows, Linux and macOS."""
    try:
        win.state("zoomed")          # Windows
    except tk.TclError:
        try:
            win.attributes("-zoomed", True)   # Linux (most WMs)
        except tk.TclError:
            # macOS fallback — fill the screen manually
            win.geometry(f"{win.winfo_screenwidth()}x{win.winfo_screenheight()}+0+0")


# ── deferred imports (mock fallbacks kept for dev without full setup) ─────────
try:
    from login import open_login
except Exception as exc:
    logger.warning("Could not import login: %s", exc)
    def open_login():
        print("Login script triggered!")

try:
    from signup import open_signup
except Exception as exc:
    logger.warning("Could not import signup: %s", exc)
    def open_signup():
        print("Signup script triggered!")


# ── main application class ────────────────────────────────────────────────────
class ATMApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("ATM Simulator")
        maximize_window(self.root)

        self.screen_width  = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        self.canvas = tk.Canvas(
            self.root,
            width=self.screen_width,
            height=self.screen_height,
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)

        self._setup_ui()

    # ── UI construction ───────────────────────────────────────────────────────
    def _setup_ui(self):
        self.canvas.delete("all")

        # Background
        if BG_PATH:
            try:
                bg_img = Image.open(BG_PATH).resize(
                    (self.screen_width, self.screen_height),
                    Image.Resampling.LANCZOS,
                )
                self.bg_photo = ImageTk.PhotoImage(bg_img)
                self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
            except Exception as exc:
                logger.warning("Could not load background image: %s", exc)
                self.canvas.configure(bg="#0f172a")
        else:
            self.canvas.configure(bg="#0f172a")

        # Logo
        if LOGO_PATH:
            try:
                logo_img = Image.open(LOGO_PATH).resize((90, 90), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_img)
                self.canvas.create_image(120, 90, image=self.logo_photo, anchor="w")
            except Exception as exc:
                logger.warning("Could not load logo image: %s", exc)

        self.canvas.create_text(
            230, 85,
            text="ATM SIMULATOR",
            font=("Montserrat", 44, "bold"),
            fill="#ffffff",
            anchor="w",
        )

        btn_color  = "#1e293b"
        btn_hover  = "#334155"
        exit_color = "#991b1b"
        exit_hover = "#ef4444"

        center_x = self.screen_width  // 2
        start_y  = self.screen_height // 2 - 80

        self._create_rounded_button(center_x, start_y,        320, 60, "SIGN IN", btn_color,  btn_hover,  open_login)
        self.canvas.create_text(center_x, start_y + 55,  text="Access your existing account",  font=("Segoe UI", 18, "bold"), fill="#f8fafc")

        self._create_rounded_button(center_x, start_y + 150,  320, 60, "SIGN UP", btn_color,  btn_hover,  open_signup)
        self.canvas.create_text(center_x, start_y + 205, text="Create a new secure account",   font=("Segoe UI", 18, "bold"), fill="#f8fafc")

        self._create_rounded_button(center_x, start_y + 300,  320, 60, "EXIT",    exit_color, exit_hover, self.exit_with_sound)

    # ── exit handler ─────────────────────────────────────────────────────────
    def exit_with_sound(self):
        sound_path = SOUNDS_DIR / "thanks_message.wav"
        play_sound_blocking(str(sound_path))   # blocking — finishes before destroy
        self.root.destroy()

    # ── button helpers ────────────────────────────────────────────────────────
    def _create_rounded_button(self, x, y, width, height, text, color, hover_color, command):
        radius = 25
        rect = self._create_round_rect(
            x - width / 2, y - height / 2,
            x + width / 2, y + height / 2,
            radius, fill=color, outline="",
        )
        txt = self.canvas.create_text(x, y, text=text, fill="white", font=("Montserrat", 16, "bold"))

        def on_enter(e): self.canvas.itemconfig(rect, fill=hover_color)
        def on_leave(e): self.canvas.itemconfig(rect, fill=color)

        for item in (rect, txt):
            self.canvas.tag_bind(item, "<Button-1>", lambda e: command())
            self.canvas.tag_bind(item, "<Enter>",    on_enter)
            self.canvas.tag_bind(item, "<Leave>",    on_leave)

    def _create_round_rect(self, x1, y1, x2, y2, r=25, **kwargs):
        points = [
            x1+r, y1,  x2-r, y1,  x2, y1,   x2, y1+r,
            x2,   y2-r, x2,  y2,  x2-r, y2, x1+r, y2,
            x1,   y2,   x1,  y2-r, x1, y1+r, x1, y1,
        ]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)


# ── entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_database()          # create tables if they don't exist yet
    root = tk.Tk()
    app  = ATMApp(root)
    root.mainloop()
