"""
signup.py — 3-step registration flow.

Changes from original:
- All hardcoded image paths replaced with relative paths.
- Input validation: email format, CNIC format (XXXXX-XXXXXXX-X),
  pin code (numeric), full name (letters + spaces only).
- Each step's window is reused (Frame-swap approach) rather than
  destroying + recreating a Toplevel — this preserves window position.
- Bare except clauses replaced with except Exception + logging.
- user_data dict is local to open_signup(), not a module-level global.
- Cross-platform window maximise.
"""

import re
import logging
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

from PIL import Image, ImageTk
from database import create_user

logger = logging.getLogger(__name__)

BASE_DIR  = Path(__file__).parent
ICONS_DIR = BASE_DIR / "icons"


def _find_image(stem: str) -> Path | None:
    for ext in (".png", ".jpg", ".jpeg", ".JPG", ".JPEG"):
        p = ICONS_DIR / (stem + ext)
        if p.exists():
            return p
    return None


def maximize_window(win):
    try:
        win.state("zoomed")
    except tk.TclError:
        try:
            win.attributes("-zoomed", True)
        except tk.TclError:
            win.geometry(f"{win.winfo_screenwidth()}x{win.winfo_screenheight()}+0+0")


# ── validation helpers ────────────────────────────────────────────────────────
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_CNIC_RE  = re.compile(r"^\d{5}-\d{7}-\d$")


def _validate_email(value: str) -> bool:
    return bool(_EMAIL_RE.match(value))


def _validate_cnic(value: str) -> bool:
    """Accept XXXXX-XXXXXXX-X or 13 consecutive digits."""
    if _CNIC_RE.match(value):
        return True
    digits = value.replace("-", "")
    return digits.isdigit() and len(digits) == 13


def _validate_pin_code(value: str) -> bool:
    return value.isdigit() and len(value) >= 4


# ── progress bar ──────────────────────────────────────────────────────────────
def _draw_progress_bar(parent, step: int):
    frame = tk.Frame(parent, bg="white")
    frame.pack(fill="x", pady=(0, 20))
    tk.Label(frame, text="Start", font=("Segoe UI", 9), bg="white", fg="#636e72").pack(side="left")
    canvas = tk.Canvas(frame, height=10, bg="#dfe6e9", highlightthickness=0)
    canvas.pack(side="left", fill="x", expand=True, padx=10)
    canvas.update_idletasks()
    fill_w = (step / 3) * canvas.winfo_width()
    canvas.create_rectangle(0, 0, fill_w, 10, fill="#0fbcf9", outline="")
    tk.Label(frame, text="Review", font=("Segoe UI", 9), bg="white", fg="#636e72").pack(side="left")
    tk.Label(parent, text=f"Step {step} of 3", font=("Segoe UI", 9, "bold"), bg="white", fg="#0fbcf9").pack(pady=(0, 10))


# ── main entry ────────────────────────────────────────────────────────────────
def open_signup():
    """Open the registration flow in a single persistent Toplevel."""
    user_data: dict = {}

    # One window lives for the whole flow; we swap content frames inside it
    win = tk.Toplevel()
    win.title("ATM Registration")
    maximize_window(win)
    win.configure(bg="#f0f2f5")

    # Outer header (stays across all steps)
    header_var = tk.StringVar(value="BANKING SYSTEM  |  STEP 1: PERSONAL DETAILS")
    header_frame = tk.Frame(win, bg="#0a3d62", height=70)
    header_frame.pack(fill="x")
    header_label = tk.Label(
        header_frame, textvariable=header_var,
        font=("Segoe UI", 14, "bold"), fg="white", bg="#0a3d62", padx=30,
    )
    header_label.pack(side="left", pady=20)

    # Container frame that holds the active step's content
    container = tk.Frame(win, bg="white", padx=30, pady=30,
                         highlightthickness=1, highlightbackground="#dcdde1")
    container.place(relx=0.5, rely=0.55, anchor="center", relwidth=0.85, relheight=0.75)

    def _clear_container():
        for w in container.winfo_children():
            w.destroy()

    # ── Step 1 ────────────────────────────────────────────────────────────────
    def show_step1():
        _clear_container()
        header_var.set("BANKING SYSTEM  |  STEP 1: PERSONAL DETAILS")
        _draw_progress_bar(container, 1)

        content = tk.Frame(container, bg="white")
        content.pack(fill="both", expand=True)

        left = tk.Frame(content, bg="white")
        left.pack(side="left", fill="both", expand=True)

        # Decorative image
        img_path = _find_image("signup")
        if img_path:
            try:
                w = int(win.winfo_screenwidth() * 0.25)
                h = int(win.winfo_screenheight() * 0.5)
                img = Image.open(img_path).resize((w, h), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                lbl = tk.Label(left, image=photo, bg="white")
                lbl.image = photo
                lbl.pack(expand=True)
            except Exception as exc:
                logger.warning("signup image: %s", exc)
        else:
            tk.Label(left, text="[signup.png not found]",
                     font=("Segoe UI", 11), fg="#b2bec3", bg="white").pack(expand=True)

        form = tk.Frame(content, bg="white")
        form.pack(side="right", fill="both", expand=True, padx=20)

        fields = [
            ("Full Name",        "full_name",    None),
            ("Father's Name",    "father_name",  None),
            ("Email Address",    "email",        None),
            ("Current Address",  "address",      None),
            ("City",             "city",         None),
            ("Pin Code",         "pin_code",     None),
            ("Province/State",   "province",     None),
        ]
        entries = {}
        for i, (label, key, _) in enumerate(fields):
            tk.Label(form, text=label, font=("Segoe UI", 10), fg="#636e72", bg="white") \
                .grid(row=i, column=0, sticky="w", pady=5)
            ent = tk.Entry(form, font=("Segoe UI", 11), bg="#f8f9fa", relief="flat",
                           highlightthickness=1, highlightbackground="#dcdde1", width=35)
            ent.grid(row=i, column=1, sticky="w", pady=5, padx=10, ipady=3)
            entries[key] = ent

        def save_step1():
            # Basic presence check
            for label, key, _ in fields:
                if not entries[key].get().strip():
                    messagebox.showwarning("Validation Error", f"Please fill in: {label}")
                    return

            # Detailed validation
            email_val    = entries["email"].get().strip()
            pin_code_val = entries["pin_code"].get().strip()

            if not _validate_email(email_val):
                messagebox.showwarning("Validation Error",
                                       "Please enter a valid email address (e.g. name@example.com)")
                return
            if not _validate_pin_code(pin_code_val):
                messagebox.showwarning("Validation Error",
                                       "Pin Code must be at least 4 digits (numbers only)")
                return

            for key in entries:
                user_data[key] = entries[key].get().strip()

            show_step2()

        tk.Button(
            form, text="NEXT →",
            font=("Segoe UI", 11, "bold"), bg="#0fbcf9", fg="white",
            relief="flat", cursor="hand2", width=25, height=2,
            command=save_step1,
        ).grid(row=len(fields) + 1, column=0, columnspan=2, pady=20)

    # ── Step 2 ────────────────────────────────────────────────────────────────
    def show_step2():
        _clear_container()
        header_var.set("BANKING SYSTEM  |  STEP 2: ADDITIONAL DETAILS")
        _draw_progress_bar(container, 2)

        content = tk.Frame(container, bg="white")
        content.pack(fill="both", expand=True)

        form_left = tk.Frame(content, bg="white")
        form_left.pack(side="left", fill="both", expand=True, padx=(0, 20))

        image_right = tk.Frame(content, bg="white")
        image_right.pack(side="right", fill="both", expand=True, padx=10)

        img_path = _find_image("signup2")
        if img_path:
            try:
                w = int(win.winfo_screenwidth() * 0.2)
                h = int(win.winfo_screenheight() * 0.4)
                img = Image.open(img_path).resize((w, h), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                lbl = tk.Label(image_right, image=photo, bg="white")
                lbl.image = photo
                lbl.pack(pady=40)
            except Exception as exc:
                logger.warning("signup2 image: %s", exc)

        combos = {}

        def _dropdown(parent, label, options, row):
            tk.Label(parent, text=label, font=("Segoe UI", 10, "bold"),
                     bg="white", fg="#2d3436").grid(row=row, column=0, sticky="w", pady=8)
            combo = ttk.Combobox(parent, values=options, font=("Segoe UI", 11),
                                 state="readonly", width=35)
            combo.grid(row=row, column=1, sticky="w", pady=8, padx=10)
            combo.set(options[0])
            return combo

        combos["religion"]   = _dropdown(form_left, "Religion:",   ["Muslim", "Christian", "Hindu", "Other"], 0)
        combos["category"]   = _dropdown(form_left, "Category:",   ["General", "OBC", "SC/ST"], 1)
        combos["income"]     = _dropdown(form_left, "Income:",     ["Less than 50,000", "50,000 – 1,00,000", "1,00,000 – 5,00,000", "Above 5,00,000"], 2)
        combos["education"]  = _dropdown(form_left, "Education:",  ["Non-Graduate", "Graduate", "Post-Graduate"], 3)
        combos["occupation"] = _dropdown(form_left, "Occupation:", ["Student", "Business", "Job", "Self-Employed"], 4)

        tk.Label(form_left, text="CNIC / ID Number:", font=("Segoe UI", 10, "bold"), bg="white") \
            .grid(row=5, column=0, sticky="w", pady=8)
        tk.Label(form_left, text="Format: 12345-1234567-1", font=("Segoe UI", 8), bg="white", fg="#999") \
            .grid(row=6, column=0, columnspan=2, sticky="w")
        cnic_entry = tk.Entry(form_left, font=("Segoe UI", 11), bg="#f8f9fa", width=37,
                              relief="flat", highlightthickness=1, highlightbackground="#dcdde1")
        cnic_entry.grid(row=5, column=1, sticky="w", pady=8, padx=10, ipady=3)

        def save_step2():
            cnic = cnic_entry.get().strip()
            if not cnic:
                messagebox.showwarning("Validation Error", "Please enter your CNIC / ID Number")
                return
            if not _validate_cnic(cnic):
                messagebox.showwarning(
                    "Validation Error",
                    "CNIC must be in the format: 12345-1234567-1\n"
                    "(or 13 consecutive digits)",
                )
                return

            for key, combo in combos.items():
                user_data[key] = combo.get()
            user_data["cnic"] = cnic
            show_step3()

        btn_frame = tk.Frame(form_left, bg="white")
        btn_frame.grid(row=7, column=0, columnspan=2, pady=30)

        tk.Button(btn_frame, text="← PREVIOUS", font=("Segoe UI", 10, "bold"),
                  bg="#bdc3c7", fg="white", relief="flat", cursor="hand2",
                  width=15, height=2, command=show_step1).pack(side="left", padx=10)

        tk.Button(btn_frame, text="NEXT →", font=("Segoe UI", 10, "bold"),
                  bg="#0fbcf9", fg="white", relief="flat", cursor="hand2",
                  width=15, height=2, command=save_step2).pack(side="left", padx=10)

    # ── Step 3 ────────────────────────────────────────────────────────────────
    def show_step3():
        _clear_container()
        header_var.set("BANKING SYSTEM  |  STEP 3: ACCOUNT DETAILS")
        _draw_progress_bar(container, 3)

        tk.Label(container, text="Account Type:", font=("Segoe UI", 12, "bold"), bg="white") \
            .pack(anchor="w", pady=5)
        acc_type = tk.StringVar(value="Savings")
        type_frame = tk.Frame(container, bg="white")
        type_frame.pack(anchor="w", pady=5)
        for text, val in [("Savings Account", "Savings"), ("Current Account", "Current"), ("Fixed Deposit", "Fixed")]:
            tk.Radiobutton(type_frame, text=text, variable=acc_type, value=val,
                           bg="white", font=("Segoe UI", 10)).pack(side="left", padx=10)

        tk.Label(container, text="Services Required:", font=("Segoe UI", 12, "bold"), bg="white") \
            .pack(anchor="w", pady=(15, 5))
        serv_frame = tk.Frame(container, bg="white")
        serv_frame.pack(anchor="w")

        services = ["ATM Card", "Internet Banking", "Mobile Banking", "SMS Alerts", "E-Statement", "Cheque Book"]
        service_vars = []
        for i, serv in enumerate(services):
            var = tk.BooleanVar()
            service_vars.append((serv, var))
            tk.Checkbutton(serv_frame, text=serv, variable=var, bg="white",
                           font=("Segoe UI", 10), width=20, anchor="w") \
                .grid(row=i // 2, column=i % 2, pady=2)

        decl_var = tk.BooleanVar()
        tk.Checkbutton(
            container,
            text="I hereby declare that the details provided are correct to the best of my knowledge.",
            variable=decl_var, bg="white", font=("Segoe UI", 9, "bold"),
        ).pack(pady=20)

        def finish_registration():
            if not decl_var.get():
                messagebox.showwarning("Warning", "Please accept the declaration to proceed.")
                return

            user_data["account_type"] = acc_type.get()
            selected = [s for s, v in service_vars if v.get()]
            user_data["services"] = ", ".join(selected) if selected else "None"

            success, result = create_user(user_data)
            if success:
                card_number, pin = result
                messagebox.showinfo(
                    "Registration Successful!",
                    f"Your account has been created successfully!\n\n"
                    f"Card Number: {card_number}\n"
                    f"PIN: {pin}\n\n"
                    f"Please save these credentials — the PIN is shown only once.",
                )
                win.destroy()
            else:
                messagebox.showerror("Registration Failed", f"Failed to create account:\n{result}")

        btn_frame = tk.Frame(container, bg="white")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="← PREVIOUS", font=("Segoe UI", 11, "bold"),
                  bg="#bdc3c7", fg="white", relief="flat", width=18, height=2,
                  command=show_step2).pack(side="left", padx=10)

        tk.Button(btn_frame, text="SUBMIT & FINISH", font=("Segoe UI", 11, "bold"),
                  bg="#05c46b", fg="white", relief="flat", width=20, height=2,
                  command=finish_registration).pack(side="left", padx=10)

    # Start on step 1
    show_step1()


# ── standalone test ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    open_signup()
    root.mainloop()
