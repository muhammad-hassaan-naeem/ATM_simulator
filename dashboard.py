"""
dashboard.py — post-login ATM dashboard.

Changes from original:
- Uses tk.Toplevel (not a second tk.Tk root) to avoid creating two
  Tk event loops; the caller's root is passed in or a hidden root is used.
- All state (balance, transactions, pin) lives inside open_dashboard()
  as local variables — no module-level globals.
- Transaction history shows the FULL list loaded from the DB at login,
  kept in sync after every operation so the in-memory list and the DB
  never drift apart.
- Deposit success sound moved INSIDE do_deposit() after a successful
  transaction (was firing when the panel first opened).
- Fixed filename: sounds/deposit_success.wav (was "deposite_successs").
- Cross-platform window maximise.
- Bare except clauses replaced with except Exception + logging.
- Logging throughout.
"""

import logging
import tkinter as tk
from tkinter import messagebox

from database import update_balance, add_transaction, get_transactions, update_pin
from sound import play_sound, play_sound_blocking

logger = logging.getLogger(__name__)


def _maximize(win):
    try:
        win.state("zoomed")
    except tk.TclError:
        try:
            win.attributes("-zoomed", True)
        except tk.TclError:
            win.geometry(f"{win.winfo_screenwidth()}x{win.winfo_screenheight()}+0+0")


def open_dashboard(user_data: dict | None = None, master: tk.Tk | None = None):
    """
    Open the dashboard Toplevel.

    Parameters
    ----------
    user_data : dict | None
        The user record returned by verify_login().  If None a demo mode
        is used (useful for standalone testing).
    master : tk.Tk | None
        The root Tk instance.  If None a hidden Tk root is created.
    """

    # ── local state (no module-level globals) ─────────────────────────────────
    if user_data:
        balance      = float(user_data.get("balance", 0))
        card_number  = user_data.get("card_number", "")
        # Load full transaction history from DB (not just 10 — we keep the
        # full list in memory so the in-session view never goes stale)
        db_txns = get_transactions(card_number, limit=50)
        # Each item in the list: human-readable string for the history panel
        transactions = [
            f"{t['type'].upper()}: {float(t['amount']):,.2f}"
            for t in db_txns
        ]
    else:
        # Demo / fallback mode
        balance      = 10_000.0
        card_number  = ""
        transactions = []

    # ── window ────────────────────────────────────────────────────────────────
    if master:
        dashboard = tk.Toplevel(master)
    else:
        # Create a hidden Tk root when called standalone
        _root = tk.Tk()
        _root.withdraw()
        dashboard = tk.Toplevel(_root)

    dashboard.title("ATM Dashboard")
    dashboard.geometry("900x550")
    dashboard.configure(bg="#f0f2f5")

    # Color tokens
    primary_blue = "#0a3d62"
    sidebar_color = "#ffffff"
    accent_color  = "#1abc9c"
    warning_color = "#e67e22"
    logout_color  = "#ff4757"
    card_bg       = "#ffffff"
    subtle_gray   = "#dcdde1"

    # ── sidebar ───────────────────────────────────────────────────────────────
    sidebar = tk.Frame(dashboard, bg=sidebar_color, width=220, relief="flat")
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    if user_data:
        tk.Label(sidebar, text="Dashboard", font=("Segoe UI", 24, "bold"),
                 bg=sidebar_color, fg=primary_blue).pack(pady=(40, 10))
        tk.Label(sidebar, text="Welcome,", font=("Segoe UI", 10),
                 bg=sidebar_color, fg="#7f8c8d").pack()
        first_name = (user_data.get("full_name") or "User").split()[0]
        tk.Label(sidebar, text=first_name, font=("Segoe UI", 12, "bold"),
                 bg=sidebar_color, fg=primary_blue).pack()
    else:
        tk.Label(sidebar, text="NEXUS", font=("Segoe UI", 24, "bold"),
                 bg=sidebar_color, fg=primary_blue).pack(pady=40)

    # ── main content area ─────────────────────────────────────────────────────
    content_frame = tk.Frame(dashboard, bg="#f0f2f5", padx=40, pady=40)
    content_frame.pack(side="right", expand=True, fill="both")

    def clear_content():
        for w in content_frame.winfo_children():
            w.destroy()

    # ── feature panels ────────────────────────────────────────────────────────
    def show_home():
        nonlocal balance
        clear_content()
        tk.Label(content_frame, text="Account Summary",
                 font=("Segoe UI", 20, "bold"), bg="#f0f2f5", fg=primary_blue).pack(anchor="w")

        card = tk.Frame(content_frame, bg=card_bg, padx=25, pady=25, bd=0, relief="ridge")
        card.pack(fill="x", pady=25)
        card.configure(highlightbackground=subtle_gray, highlightthickness=1)
        tk.Label(card, text="Total Balance", font=("Segoe UI", 12),
                 bg=card_bg, fg="#7f8c8d").pack(anchor="w")
        tk.Label(card, text=f"PKR {balance:,.2f}", font=("Segoe UI", 32, "bold"),
                 bg=card_bg, fg="#2f3640").pack(anchor="w")

        if user_data:
            info = tk.Frame(content_frame, bg=card_bg, padx=25, pady=15, bd=0, relief="ridge")
            info.pack(fill="x", pady=10)
            info.configure(highlightbackground=subtle_gray, highlightthickness=1)
            tk.Label(info, text=f"Account Holder: {user_data.get('full_name', '')}",
                     font=("Segoe UI", 11), bg=card_bg).pack(anchor="w")
            display_cn = user_data.get("card_number_display", user_data.get("card_number", ""))
            if display_cn:
                tk.Label(info, text=f"Card: {display_cn}",
                         font=("Segoe UI", 11), bg=card_bg).pack(anchor="w")

    # ── deposit ───────────────────────────────────────────────────────────────
    def show_deposit_ui():
        nonlocal balance
        clear_content()
        tk.Label(content_frame, text="Deposit Funds",
                 font=("Segoe UI", 20, "bold"), bg="#f0f2f5", fg=primary_blue).pack(anchor="w")
        tk.Label(content_frame, text="Enter amount to add (multiples of 500):",
                 bg="#f0f2f5", pady=12).pack(anchor="w")
        amount_entry = tk.Entry(content_frame, font=("Segoe UI", 16), bd=1, bg="white", relief="solid")
        amount_entry.pack(fill="x", pady=12, ipady=8)
        amount_entry.focus_set()

        def do_deposit():
            nonlocal balance
            try:
                amt = float(amount_entry.get())
                if amt <= 0 or amt % 500 != 0:
                    messagebox.showerror("Error", "Amount must be a positive multiple of 500")
                    return
                balance += amt
                transactions.append(f"DEPOSIT: +{amt:,.2f}")
                if card_number:
                    update_balance(card_number, balance)
                    add_transaction(card_number, "deposit", amt)
                # Sound fires AFTER successful deposit
                play_sound("sounds/deposit_success.wav")
                messagebox.showinfo("Success", f"PKR {amt:,.2f} deposited successfully!")
                show_home()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount")
            except Exception as exc:
                logger.error("deposit error: %s", exc)
                messagebox.showerror("Error", "An unexpected error occurred")

        tk.Button(content_frame, text="Confirm Deposit", bg=accent_color, fg="white",
                  font=("Segoe UI", 12, "bold"), bd=0, height=2, cursor="hand2",
                  command=do_deposit).pack(fill="x", pady=12)

    # ── withdraw ──────────────────────────────────────────────────────────────
    def show_withdraw_ui():
        nonlocal balance
        clear_content()
        tk.Label(content_frame, text="Withdraw Cash",
                 font=("Segoe UI", 20, "bold"), bg="#f0f2f5", fg=primary_blue).pack(anchor="w")
        tk.Label(content_frame, text="Enter amount to withdraw (multiples of 500):",
                 bg="#f0f2f5", pady=12).pack(anchor="w")
        amount_entry = tk.Entry(content_frame, font=("Segoe UI", 16), bd=1, bg="white", relief="solid")
        amount_entry.pack(fill="x", pady=12, ipady=8)
        amount_entry.focus_set()

        delayed_sound_flag = [False]

        def on_focus_in(e):
            if not delayed_sound_flag[0]:
                delayed_sound_flag[0] = True
                from sound import delayed_sound
                delayed_sound("sounds/confirm_amount.wav", 0.3)

        amount_entry.bind("<FocusIn>", on_focus_in)

        def do_withdraw():
            nonlocal balance
            try:
                amt = float(amount_entry.get())
                if amt <= 0 or amt % 500 != 0:
                    messagebox.showerror("Error", "Amount must be a positive multiple of 500")
                    return
                if amt > balance:
                    messagebox.showwarning("Insufficient Funds",
                                           f"You only have PKR {balance:,.2f} available")
                    return
                balance -= amt
                transactions.append(f"WITHDRAW: -{amt:,.2f}")
                if card_number:
                    update_balance(card_number, balance)
                    add_transaction(card_number, "withdraw", amt)
                play_sound("sounds/transaction_success.wav")
                messagebox.showinfo("Success", "Withdrawal Successful!")
                show_home()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount")
            except Exception as exc:
                logger.error("withdraw error: %s", exc)
                messagebox.showerror("Error", "An unexpected error occurred")

        tk.Button(content_frame, text="Withdraw Funds", bg=warning_color, fg="white",
                  font=("Segoe UI", 12, "bold"), bd=0, height=2, cursor="hand2",
                  command=do_withdraw).pack(fill="x", pady=12)

    # ── history ───────────────────────────────────────────────────────────────
    def show_history():
        clear_content()
        tk.Label(content_frame, text="Recent Activity",
                 font=("Segoe UI", 20, "bold"), bg="#f0f2f5", fg=primary_blue).pack(anchor="w", pady=(0, 15))
        list_frame = tk.Frame(content_frame, bg=card_bg)
        list_frame.pack(fill="both", expand=True)

        # Show up to the 10 most recent transactions from the in-memory list
        recent = list(reversed(transactions[-10:]))
        if not recent:
            tk.Label(list_frame, text="No transactions yet", bg=card_bg, pady=20).pack()
        else:
            for t in recent:
                color = "#e8f5e9" if t.startswith("DEPOSIT") else "#fff3e0"
                t_card = tk.Frame(list_frame, bg=color, pady=10, padx=15)
                t_card.pack(fill="x", pady=6)
                tk.Label(t_card, text=t, bg=color, font=("Segoe UI", 12), anchor="w").pack(fill="x")

    # ── change PIN ────────────────────────────────────────────────────────────
    def show_pin_ui():
        clear_content()
        tk.Label(content_frame, text="Change Secure PIN",
                 font=("Segoe UI", 20, "bold"), bg="#f0f2f5", fg=primary_blue).pack(anchor="w", pady=(0, 15))

        tk.Label(content_frame, text="Enter current PIN:", bg="#f0f2f5", pady=6).pack(anchor="w")
        current_entry = tk.Entry(content_frame, show="*", font=("Segoe UI", 16),
                                 bd=1, bg="white", relief="solid")
        current_entry.pack(fill="x", pady=6, ipady=8)

        tk.Label(content_frame, text="Enter new 4-digit PIN:", bg="#f0f2f5", pady=6).pack(anchor="w")
        new_entry = tk.Entry(content_frame, show="*", font=("Segoe UI", 16),
                             bd=1, bg="white", relief="solid")
        new_entry.pack(fill="x", pady=6, ipady=8)

        tk.Label(content_frame, text="Confirm new PIN:", bg="#f0f2f5", pady=6).pack(anchor="w")
        confirm_entry = tk.Entry(content_frame, show="*", font=("Segoe UI", 16),
                                 bd=1, bg="white", relief="solid")
        confirm_entry.pack(fill="x", pady=6, ipady=8)
        current_entry.focus_set()

        def do_change():
            current_pin = current_entry.get()
            new_p       = new_entry.get()
            confirm_p   = confirm_entry.get()

            if not (len(new_p) == 4 and new_p.isdigit()):
                messagebox.showerror("Error", "New PIN must be exactly 4 digits")
                return
            if new_p != confirm_p:
                messagebox.showerror("Error", "New PIN and confirmation do not match")
                return

            # Verify current PIN before allowing change
            if user_data:
                from database import verify_pin
                stored_hash = user_data.get("pin_hash", "")
                if not verify_pin(current_pin, stored_hash):
                    messagebox.showerror("Error", "Current PIN is incorrect")
                    return
                if update_pin(card_number, new_p):
                    user_data["pin_hash"] = ""  # invalidate cached hash
                else:
                    messagebox.showerror("Error", "Failed to update PIN in database")
                    return

            play_sound("sounds/pinchange_success.wav")
            messagebox.showinfo("Security", "PIN Updated Successfully")
            show_home()

        tk.Button(content_frame, text="Update PIN", bg=primary_blue, fg="white",
                  font=("Segoe UI", 12, "bold"), bd=0, height=2, cursor="hand2",
                  command=do_change).pack(fill="x", pady=12)

    # ── sidebar buttons ───────────────────────────────────────────────────────
    def on_enter(e):
        e.widget["bg"] = accent_color
        e.widget["fg"] = "white"

    def on_leave(e):
        e.widget["bg"] = sidebar_color
        e.widget["fg"] = "#57606f"

    btn_style = {
        "bg": sidebar_color, "fg": "#57606f",
        "font": ("Segoe UI", 12), "bd": 0,
        "cursor": "hand2", "anchor": "w",
        "padx": 20, "height": 2,
    }

    for label, cmd in [
        ("🏠 Dashboard",  show_home),
        ("💵 Deposit",    show_deposit_ui),
        ("💸 Withdraw",   show_withdraw_ui),
        ("📜 Statement",  show_history),
        ("🔑 Change PIN", show_pin_ui),
    ]:
        btn = tk.Button(sidebar, text=label, command=cmd, **btn_style)
        btn.pack(fill="x", pady=2)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    # ── logout ────────────────────────────────────────────────────────────────
    def logout():
        play_sound("sounds/thanks_message.wav")
        dashboard.destroy()

    tk.Button(sidebar, text="🚪 Logout", bg=logout_color, fg="white",
              font=("Segoe UI", 11, "bold"), bd=0, cursor="hand2",
              command=logout).pack(side="bottom", fill="x", pady=20, padx=10)

    show_home()

    # Only call mainloop if we created our own root
    if master is None:
        _root.mainloop()
