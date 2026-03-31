import tkinter as tk
from tkinter import messagebox
from database import update_balance, add_transaction, get_transactions, update_pin
from sound import play_sound, delayed_sound  # 🔊 sound functions

# Global Data
balance = 10000.0
transactions = []
pin = "1234"
current_user = None  # Will store logged in user data

def open_dashboard(user_data=None):
    global current_user, balance, transactions, pin
    current_user = user_data
    
    # Load user data if available
    if current_user:
        balance = float(current_user['balance'])
        pin = current_user['pin']
        db_transactions = get_transactions(current_user['card_number'])
        transactions = [f"{t['type'].upper()}: {t['amount']:,.2f}" for t in db_transactions]
    
    dashboard = tk.Tk()
    dashboard.title("ATM dashboard")
    dashboard.geometry("900x550")
    dashboard.configure(bg="#f0f2f5")

    primary_blue = "#0a3d62"
    sidebar_color = "#ffffff"
    accent_color = "#1abc9c"
    warning_color = "#e67e22"
    logout_color = "#ff4757"
    card_bg = "#ffffff"
    subtle_gray = "#dcdde1"

    # ---------- Sidebar ----------
    sidebar = tk.Frame(dashboard, bg=sidebar_color, width=220, relief="flat")
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    if current_user:
        tk.Label(sidebar, text="Dashboard", font=("Segoe UI", 24, "bold"), 
                 bg=sidebar_color, fg=primary_blue).pack(pady=(40, 10))
        tk.Label(sidebar, text=f"Welcome,", font=("Segoe UI", 10), 
                 bg=sidebar_color, fg="#7f8c8d").pack()
        tk.Label(sidebar, text=current_user['full_name'].split()[0] if current_user['full_name'] else "User", 
                 font=("Segoe UI", 12, "bold"), bg=sidebar_color, fg=primary_blue).pack()
    else:
        tk.Label(sidebar, text="NEXUS", font=("Segoe UI", 24, "bold"), 
                 bg=sidebar_color, fg=primary_blue).pack(pady=40)

    # ---------- Main Content Area ----------
    content_frame = tk.Frame(dashboard, bg="#f0f2f5", padx=40, pady=40)
    content_frame.pack(side="right", expand=True, fill="both")

    def clear_content():
        for widget in content_frame.winfo_children():
            widget.destroy()

    # ---------- Feature Functions ----------
    def show_home():
        clear_content()
        tk.Label(content_frame, text="Account Summary", font=("Segoe UI", 20, "bold"), 
                 bg="#f0f2f5", fg=primary_blue).pack(anchor="w")
        
        card = tk.Frame(content_frame, bg=card_bg, padx=25, pady=25, bd=0, relief="ridge")
        card.pack(fill="x", pady=25)
        card.configure(highlightbackground=subtle_gray, highlightthickness=1)

        tk.Label(card, text="Total Balance", font=("Segoe UI", 12), bg=card_bg, fg="#7f8c8d").pack(anchor="w")
        tk.Label(card, text=f"PKR {balance:,.2f}", font=("Segoe UI", 32, "bold"), bg=card_bg, fg="#2f3640").pack(anchor="w")
        
        if current_user:
            info_frame = tk.Frame(content_frame, bg=card_bg, padx=25, pady=15, bd=0, relief="ridge")
            info_frame.pack(fill="x", pady=10)
            info_frame.configure(highlightbackground=subtle_gray, highlightthickness=1)
            
            tk.Label(info_frame, text=f"Account Holder: {current_user['full_name']}", 
                    font=("Segoe UI", 11), bg=card_bg).pack(anchor="w")
            if 'card_number_display' in current_user:
                tk.Label(info_frame, text=f"Card: {current_user['card_number_display']}", 
                        font=("Segoe UI", 11), bg=card_bg).pack(anchor="w")

    def show_deposit_ui():
        clear_content()
        tk.Label(content_frame, text="Deposit Funds", font=("Segoe UI", 20, "bold"), bg="#f0f2f5", fg=primary_blue).pack(anchor="w")
        tk.Label(content_frame, text="Enter amount to add to your account (multiples of 500):", bg="#f0f2f5", pady=12).pack(anchor="w")
        amount_entry = tk.Entry(content_frame, font=("Segoe UI", 16), bd=1, bg="white", relief="solid")
        amount_entry.pack(fill="x", pady=12, ipady=8)
        amount_entry.focus_set()

        delayed_sound("sounds/deposite_successs.wav", 0.3)

        def do_deposit():
            global balance, transactions
            try:
                amt = float(amount_entry.get())
                if amt <= 0 or amt % 500 != 0:
                    messagebox.showerror("Error", "Amount must be a multiple of 500")
                    return
                
                balance += amt
                transactions.append(f"Deposit: +{amt:,.2f}")
                
                if current_user:
                    update_balance(current_user['card_number'], balance)
                    add_transaction(current_user['card_number'], 'deposit', amt)
                
                play_sound("sounds/transaction_success.wav")
                messagebox.showinfo("Success", f"PKR {amt:,.2f} deposited!")
                show_home()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount")

        tk.Button(content_frame, text="Confirm Deposit", bg=accent_color, fg="white", 
                  font=("Segoe UI", 12, "bold"), bd=0, height=2, cursor="hand2", command=do_deposit)\
            .pack(fill="x", pady=12)

    def show_withdraw_ui():
        clear_content()
        tk.Label(content_frame, text="Withdraw Cash", font=("Segoe UI", 20, "bold"), bg="#f0f2f5", fg=primary_blue).pack(anchor="w")
        tk.Label(content_frame, text="Enter amount to withdraw (multiples of 500):", bg="#f0f2f5", pady=12).pack(anchor="w")
        amount_entry = tk.Entry(content_frame, font=("Segoe UI", 16), bd=1, bg="white", relief="solid")
        amount_entry.pack(fill="x", pady=12, ipady=8)
        amount_entry.focus_set()

        delayed_sound("sounds/confirm_amount.wav", 0.3)

        def do_withdraw():
            global balance, transactions
            try:
                amt = float(amount_entry.get())
                if amt <= 0 or amt % 500 != 0:
                    messagebox.showerror("Error", "Amount must be a multiple of 500")
                    return
                if amt > balance:
                    messagebox.showwarning("Failed", "Insufficient Funds")
                    return
                balance -= amt
                transactions.append(f"Withdraw: -{amt:,.2f}")
                
                if current_user:
                    update_balance(current_user['card_number'], balance)
                    add_transaction(current_user['card_number'], 'withdraw', amt)
                
                play_sound("sounds/transaction_success.wav")
                messagebox.showinfo("Success", "Withdrawal Successful!")
                show_home()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount")

        tk.Button(content_frame, text="Withdraw Funds", bg=warning_color, fg="white", 
                  font=("Segoe UI", 12, "bold"), bd=0, height=2, cursor="hand2", command=do_withdraw)\
            .pack(fill="x", pady=12)

    def show_history():
        clear_content()
        tk.Label(content_frame, text="Recent Activity", font=("Segoe UI", 20, "bold"), bg="#f0f2f5", fg=primary_blue).pack(anchor="w", pady=(0,15))
        list_frame = tk.Frame(content_frame, bg=card_bg)
        list_frame.pack(fill="both", expand=True)

        if not transactions:
            tk.Label(list_frame, text="No transactions yet", bg=card_bg, pady=20).pack()
        else:
            for t in reversed(transactions[-5:]):
                t_card = tk.Frame(list_frame, bg="#f7f9fa", pady=10, padx=15)
                t_card.pack(fill="x", pady=8)
                tk.Label(t_card, text=t, bg="#f7f9fa", font=("Segoe UI", 12), anchor="w").pack(fill="x")

    def show_pin_ui():
        clear_content()
        tk.Label(content_frame, text="Change Secure PIN", font=("Segoe UI", 20, "bold"), bg="#f0f2f5", fg=primary_blue).pack(anchor="w", pady=(0,15))
        tk.Label(content_frame, text="Enter New 4-Digit PIN:", bg="#f0f2f5", pady=12).pack(anchor="w")
        pin_entry = tk.Entry(content_frame, show="*", font=("Segoe UI", 16), bd=1, bg="white", relief="solid")
        pin_entry.pack(fill="x", pady=12, ipady=8)

        def do_change():
            global pin
            new_p = pin_entry.get()
            if len(new_p) == 4 and new_p.isdigit():
                pin = new_p
                if current_user:
                    update_pin(current_user['card_number'], new_p)
                play_sound("sounds/pinchange_success.wav")
                messagebox.showinfo("Security", "PIN Updated Successfully")
                show_home()
            else:
                messagebox.showerror("Error", "PIN must be 4 digits")

        tk.Button(content_frame, text="Update PIN", bg=primary_blue, fg="white", 
                  font=("Segoe UI", 12, "bold"), bd=0, height=2, cursor="hand2", command=do_change)\
            .pack(fill="x", pady=12)

    # ---------- Sidebar Buttons ----------
    def on_enter(e):
        e.widget['bg'] = accent_color
        e.widget['fg'] = "white"
    def on_leave(e):
        e.widget['bg'] = sidebar_color
        e.widget['fg'] = "#57606f"

    btn_style = {
        "bg": sidebar_color,
        "fg": "#57606f",
        "font": ("Segoe UI", 12),
        "bd": 0,
        "cursor": "hand2",
        "anchor": "w",
        "padx": 20,
        "height": 2
    }

    buttons = [
        ("🏠 Dashboard", show_home),
        ("💵 Deposit", show_deposit_ui),
        ("💸 Withdraw", show_withdraw_ui),
        ("📜 Statement", show_history),
        ("🔑 Change PIN", show_pin_ui)
    ]

    for text, cmd in buttons:
        btn = tk.Button(sidebar, text=text, command=cmd, **btn_style)
        btn.pack(fill="x", pady=2)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    # ---------- Logout Button with Thanks Voice ----------
    def logout():
        play_sound("sounds/thanks_message.wav")
        dashboard.destroy()

    tk.Button(sidebar, text="🚪 Logout", bg=logout_color, fg="white", 
              font=("Segoe UI", 11, "bold"), bd=0, cursor="hand2", command=logout)\
        .pack(side="bottom", fill="x", pady=20, padx=10)

    show_home()
    dashboard.mainloop()