"""
login.py — ATM login window.

Changes from original:
- Hardcoded image paths replaced with relative paths (pathlib).
- Cross-platform window maximise via main.maximize_window.
- Lockout is persisted to the database via database.block_card().
- attempts counter is LOCAL to each open_login() call (no shared global).
- Bare except replaced with except Exception.
- Input validation added (card number and PIN must be non-empty).
- Login button disabled while a login attempt is in-flight (prevents
  double-clicks from consuming two attempts).
"""

import logging
import tkinter as tk
from pathlib import Path

from PIL import Image, ImageTk

from database import verify_login, block_card
from sound import play_sound, delayed_sound

logger = logging.getLogger(__name__)

BASE_DIR   = Path(__file__).parent
ICONS_DIR  = BASE_DIR / "icons"

MAX_ATTEMPTS = 3


def _find_image(stem: str) -> Path | None:
    for ext in (".png", ".jpg", ".jpeg", ".JPG", ".JPEG"):
        p = ICONS_DIR / (stem + ext)
        if p.exists():
            return p
    return None


def maximize_window(win):
    """Cross-platform window maximise (duplicated here to avoid circular import)."""
    try:
        win.state("zoomed")
    except tk.TclError:
        try:
            win.attributes("-zoomed", True)
        except tk.TclError:
            win.geometry(f"{win.winfo_screenwidth()}x{win.winfo_screenheight()}+0+0")


# ── deferred dashboard import ─────────────────────────────────────────────────
try:
    from dashboard import open_dashboard
except Exception as exc:
    logger.warning("Could not import dashboard: %s", exc)
    def open_dashboard(user_data=None):
        print("Dashboard opened")


# ── main login window ─────────────────────────────────────────────────────────
def open_login():
    """Open the login Toplevel window."""
    # Each call gets its own mutable state — no shared globals.
    state = {"attempts": MAX_ATTEMPTS}

    login_window = tk.Toplevel()
    login_window.title("ATM System")
    maximize_window(login_window)

    delayed_sound("sounds/enter_pin.wav", 0.6)

    screen_w = login_window.winfo_screenwidth()
    screen_h = login_window.winfo_screenheight()

    # ── background ────────────────────────────────────────────────────────────
    signin_path = _find_image("signin")
    if signin_path:
        try:
            bg = Image.open(signin_path).resize((screen_w, screen_h), Image.Resampling.LANCZOS)
            bg_photo = ImageTk.PhotoImage(bg)
            bg_label = tk.Label(login_window, image=bg_photo)
            bg_label.image = bg_photo
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as exc:
            logger.warning("Could not load signin background: %s", exc)
            login_window.configure(bg="#0a3d62")
    else:
        login_window.configure(bg="#0a3d62")

    # ── header ────────────────────────────────────────────────────────────────
    header = tk.Frame(login_window, bg="#0a3d62", height=80)
    header.pack(fill="x")

    logo_path = _find_image("logo")
    if logo_path:
        try:
            logo = Image.open(logo_path).resize((60, 60), Image.Resampling.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo)
            logo_label = tk.Label(header, image=logo_photo, bg="#0a3d62")
            logo_label.image = logo_photo
            logo_label.pack(side="left", padx=20, pady=10)
        except Exception as exc:
            logger.warning("Could not load logo: %s", exc)

    tk.Label(
        header, text="ATM System",
        font=("Segoe UI", 22, "bold"), fg="white", bg="#0a3d62",
    ).pack(side="left", padx=10)

    # ── login card ────────────────────────────────────────────────────────────
    card = tk.Frame(login_window, bg="white", padx=50, pady=40, bd=2, relief="ridge")
    card.place(relx=0.5, rely=0.55, anchor="center")

    tk.Label(
        card, text="ATM LOGIN",
        font=("Segoe UI", 24, "bold"), fg="#0a3d62", bg="white",
    ).grid(row=0, column=0, columnspan=2, pady=(0, 25))

    # Card number
    tk.Label(card, text="Card Number", font=("Segoe UI", 12), bg="white") \
        .grid(row=1, column=0, sticky="e", padx=10, pady=10)
    card_entry = tk.Entry(card, font=("Segoe UI", 12), width=25)
    card_entry.grid(row=1, column=1, pady=10)
    card_entry.focus_set()

    # PIN
    tk.Label(card, text="PIN", font=("Segoe UI", 12), bg="white") \
        .grid(row=2, column=0, sticky="e", padx=10, pady=10)
    pin_entry = tk.Entry(card, font=("Segoe UI", 12), width=25, show="*")
    pin_entry.grid(row=2, column=1, pady=10)

    # Buttons
    btn_frame = tk.Frame(card, bg="white")
    btn_frame.grid(row=3, column=0, columnspan=2, pady=20)

    login_btn = tk.Button(
        btn_frame, text="Login",
        font=("Segoe UI", 11, "bold"), bg="#0a3d62", fg="white",
        width=12, cursor="hand2",
    )
    login_btn.pack(side="left", padx=10)

    tk.Button(
        btn_frame, text="Cancel",
        font=("Segoe UI", 11, "bold"), bg="#c0392b", fg="white",
        width=12, cursor="hand2",
        command=login_window.destroy,
    ).pack(side="left", padx=10)

    message_label = tk.Label(card, text="", font=("Segoe UI", 11), bg="white")
    message_label.grid(row=4, column=0, columnspan=2)

    # ── check-PIN logic ───────────────────────────────────────────────────────
    def check_pin():
        entered_card = card_entry.get().strip()
        entered_pin  = pin_entry.get().strip()

        if not entered_card or not entered_pin:
            message_label.config(text="Please enter card number and PIN", fg="red")
            return

        # Disable button during the (possibly slow) DB call
        login_btn.config(state="disabled")
        login_window.update()

        success, result = verify_login(entered_card, entered_pin)

        if success:
            play_sound("sounds/login_success.wav")
            message_label.config(text="Login Successful ✔", fg="green")
            login_window.update()

            user_data = result
            # Add a display-formatted card number
            cn = user_data.get("card_number", "")
            if len(cn) == 16:
                user_data["card_number_display"] = " ".join(cn[i:i+4] for i in range(0, 16, 4))
            else:
                user_data["card_number_display"] = cn

            login_window.after(1000, lambda: [login_window.destroy(), open_dashboard(user_data)])

        else:
            state["attempts"] -= 1
            play_sound("sounds/invalid_pin.wav")

            if state["attempts"] > 0:
                message_label.config(
                    text=f"{result}. Attempts left: {state['attempts']}",
                    fg="red",
                )
                pin_entry.delete(0, tk.END)
                pin_entry.focus_set()
                login_btn.config(state="normal")   # re-enable for next try
            else:
                # Persist the block to the database
                block_card(entered_card)
                message_label.config(
                    text="Card Blocked ❌  Too many failed attempts",
                    fg="red",
                )
                pin_entry.config(state="disabled")
                card_entry.config(state="disabled")
                login_btn.config(state="disabled")
                logger.warning("Card blocked after failed attempts: %s", entered_card)

    login_btn.config(command=check_pin)
    login_window.bind("<Return>", lambda e: check_pin())
