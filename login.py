import tkinter as tk
from PIL import Image, ImageTk
from database import verify_login
import tkinter.messagebox as messagebox
from sound import play_sound, delayed_sound  # 🔊 sound functions

# try importing dashboard
try:
    from dashboard import open_dashboard
except:
    def open_dashboard(user_data=None):
        print("Dashboard opened")

attempts = 3

def open_login():
    global pin_entry, message_label, attempts, card_entry
    
    attempts = 3  # Reset attempts
    
    login_window = tk.Toplevel()
    login_window.title("ATM System")
    login_window.state("zoomed")

    # 🔊 Play enter PIN sound when login window opens
    delayed_sound("sounds/enter_pin.wav", 0.6)

    screen_width = login_window.winfo_screenwidth()
    screen_height = login_window.winfo_screenheight()

    # ---------------- BACKGROUND IMAGE ----------------
    try:
        bg_image = Image.open(r"C:\Users\pc\Desktop\ATM_Project\icons\signin.jpeg")
        bg_image = bg_image.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
        bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label = tk.Label(login_window, image=bg_photo)
        bg_label.image = bg_photo
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    except:
        login_window.configure(bg="#0a3d62")

    # ---------------- HEADER ----------------
    header = tk.Frame(login_window, bg="#0a3d62", height=80)
    header.pack(fill="x")

    try:
        logo = Image.open(r"C:\Users\pc\Desktop\ATM_Project\icons\logo.png")
        logo = logo.resize((60, 60), Image.Resampling.LANCZOS)
        logo_photo = ImageTk.PhotoImage(logo)
        logo_label = tk.Label(header, image=logo_photo, bg="#0a3d62")
        logo_label.image = logo_photo
        logo_label.pack(side="left", padx=20, pady=10)
    except:
        pass

    title = tk.Label(
        header,
        text="ATM System",
        font=("Segoe UI", 22, "bold"),
        fg="white",
        bg="#0a3d62"
    )
    title.pack(side="left", padx=10)

    # ---------------- LOGIN CARD ----------------
    card = tk.Frame(login_window, bg="white", padx=50, pady=40, bd=2, relief="ridge")
    card.place(relx=0.5, rely=0.55, anchor="center")

    tk.Label(
        card,
        text="ATM LOGIN",
        font=("Segoe UI", 24, "bold"),
        fg="#0a3d62",
        bg="white"
    ).grid(row=0, column=0, columnspan=2, pady=(0, 25))

    # CARD NUMBER
    tk.Label(card, text="Card Number", font=("Segoe UI", 12), bg="white")\
        .grid(row=1, column=0, sticky="e", padx=10, pady=10)

    card_entry = tk.Entry(card, font=("Segoe UI", 12), width=25)
    card_entry.grid(row=1, column=1, pady=10)
    card_entry.focus_set()

    # PIN
    tk.Label(card, text="PIN", font=("Segoe UI", 12), bg="white")\
        .grid(row=2, column=0, sticky="e", padx=10, pady=10)

    pin_entry = tk.Entry(card, font=("Segoe UI", 12), width=25, show="*")
    pin_entry.grid(row=2, column=1, pady=10)

    # ---------------- BUTTONS ----------------
    btn_frame = tk.Frame(card, bg="white")
    btn_frame.grid(row=3, column=0, columnspan=2, pady=20)

    login_btn = tk.Button(
        btn_frame,
        text="Login",
        font=("Segoe UI", 11, "bold"),
        bg="#0a3d62",
        fg="white",
        width=12,
        cursor="hand2",
        command=lambda: check_pin(login_window, login_btn)
    )
    login_btn.pack(side="left", padx=10)

    cancel_btn = tk.Button(
        btn_frame,
        text="Cancel",
        font=("Segoe UI", 11, "bold"),
        bg="#c0392b",
        fg="white",
        width=12,
        cursor="hand2",
        command=login_window.destroy
    )
    cancel_btn.pack(side="left", padx=10)

    # MESSAGE
    message_label = tk.Label(
        card,
        text="",
        font=("Segoe UI", 11),
        bg="white"
    )
    message_label.grid(row=4, column=0, columnspan=2)

    login_window.bind("<Return>", lambda event: check_pin(login_window, login_btn))


def check_pin(login_window, login_btn):
    global attempts, pin_entry, card_entry, message_label
    
    entered_card = card_entry.get().strip()
    entered_pin = pin_entry.get().strip()
    
    if not entered_card or not entered_pin:
        message_label.config(text="Please enter card number and PIN", fg="red")
        return
    
    success, result = verify_login(entered_card, entered_pin)
    
    if success:
        play_sound("sounds/login_success.wav")  # 🔊 success sound
        message_label.config(text="Login Successful ✔", fg="green")
        login_window.update()
        
        user_data = result
        if len(user_data['card_number']) == 16:
            formatted_card = " ".join(
                [user_data['card_number'][i:i+4] for i in range(0, 16, 4)]
            )
            user_data['card_number_display'] = formatted_card
        else:
            user_data['card_number_display'] = user_data['card_number']
        
        login_window.after(1000, lambda: [login_window.destroy(), open_dashboard(user_data)])
        
    else:
        attempts -= 1

        play_sound("sounds/invalid_pin.wav")  # 🔊 invalid PIN sound
        
        if attempts > 0:
            message_label.config(
                text=f"{result} Attempts left: {attempts}",
                fg="red"
            )
            pin_entry.delete(0, tk.END)
            pin_entry.focus_set()
        else:
            message_label.config(
                text="Card Blocked ❌ Too many failed attempts",
                fg="red"
            )
            pin_entry.config(state="disabled")
            card_entry.config(state="disabled")
            login_btn.config(state="disabled")