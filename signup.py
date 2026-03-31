import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from database import create_user

# Store user data across pages
user_data = {}

# --- Progress Bar Function ---
def draw_progress_bar(parent, step):
    progress_frame = tk.Frame(parent, bg="white")
    progress_frame.pack(fill="x", pady=(0, 20))

    tk.Label(progress_frame, text="Start", font=("Segoe UI", 9), bg="white", fg="#636e72").pack(side="left")

    canvas = tk.Canvas(progress_frame, height=10, bg="#dfe6e9", highlightthickness=0)
    canvas.pack(side="left", fill="x", expand=True, padx=10)
    canvas.update_idletasks()

    fill_width = (step / 3) * canvas.winfo_width()
    canvas.create_rectangle(0, 0, fill_width, 10, fill="#0fbcf9", outline="")

    tk.Label(progress_frame, text="Review", font=("Segoe UI", 9), bg="white", fg="#636e72").pack(side="left")
    tk.Label(parent, text=f"Step {step} of 3", font=("Segoe UI", 9, "bold"), bg="white", fg="#0fbcf9").pack(pady=(0, 10))

# --- Page 1 ---
def open_signup():
    global user_data
    user_data = {}  # Reset user data
    
    signup_window = tk.Toplevel()
    signup_window.title("ATM Registration - Page 1")
    signup_window.state('zoomed')
    signup_window.configure(bg="#f0f2f5")

    header = tk.Frame(signup_window, bg="#0a3d62", height=70)
    header.pack(fill="x")
    tk.Label(header, text="BANKING SYSTEM | STEP 1: PERSONAL DETAILS", 
             font=("Segoe UI", 14, "bold"), fg="white", bg="#0a3d62", padx=30).pack(side="left", pady=20)

    container = tk.Frame(signup_window, bg="white", padx=30, pady=30, highlightthickness=1, highlightbackground="#dcdde1")
    container.place(relx=0.5, rely=0.55, anchor="center", relwidth=0.85, relheight=0.75)

    draw_progress_bar(container, 1)

    content_frame = tk.Frame(container, bg="white")
    content_frame.pack(fill="both", expand=True)

    left_frame = tk.Frame(content_frame, bg="white")
    left_frame.pack(side="left", fill="both", expand=True)

    # Page 1 Image
    try:
        img_path = r"C:\Users\pc\Desktop\ATM_Project\icons\signup.png"
        img = Image.open(img_path)
        w = int(signup_window.winfo_screenwidth() * 0.25)
        h = int(signup_window.winfo_screenheight() * 0.5)
        img = img.resize((w, h), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        img_label = tk.Label(left_frame, image=photo, bg="white")
        img_label.image = photo
        img_label.pack(expand=True)
    except:
        tk.Label(left_frame, text="[Upload signup.png in icons folder]", 
                font=("Segoe UI", 12), fg="#b2bec3", bg="white").pack(expand=True)

    form_frame = tk.Frame(content_frame, bg="white")
    form_frame.pack(side="right", fill="both", expand=True, padx=20)

    fields = ["Full Name", "Father's Name", "Email Address", "Current Address", "City", "Pin Code", "Province/State"]
    entries = {}
    
    for i, label_text in enumerate(fields):
        tk.Label(form_frame, text=label_text, font=("Segoe UI", 10), fg="#636e72", bg="white").grid(row=i, column=0, sticky="w", pady=5)
        entry = tk.Entry(form_frame, font=("Segoe UI", 11), bg="#f8f9fa", relief="flat", 
                        highlightthickness=1, highlightbackground="#dcdde1", width=35)
        entry.grid(row=i, column=1, sticky="w", pady=5, padx=10, ipady=3)
        entries[label_text] = entry

    def save_page1():
        # Validate required fields
        for field, entry in entries.items():
            if not entry.get().strip():
                messagebox.showwarning("Validation Error", f"Please fill {field}")
                return
        
        # Save data
        user_data['full_name'] = entries["Full Name"].get().strip()
        user_data['father_name'] = entries["Father's Name"].get().strip()
        user_data['email'] = entries["Email Address"].get().strip()
        user_data['address'] = entries["Current Address"].get().strip()
        user_data['city'] = entries["City"].get().strip()
        user_data['pin_code'] = entries["Pin Code"].get().strip()
        user_data['province'] = entries["Province/State"].get().strip()
        
        signup_window.destroy()
        open_page_2()

    tk.Button(form_frame, text="NEXT →", font=("Segoe UI", 11, "bold"), bg="#0fbcf9", fg="white", 
              relief="flat", cursor="hand2", width=25, height=2, 
              command=save_page1).grid(row=len(fields)+1, column=0, columnspan=2, pady=20)

# --- Page 2 ---
def open_page_2():
    global user_data
    
    p2_window = tk.Toplevel()
    p2_window.title("ATM Registration - Page 2")
    p2_window.state('zoomed')
    p2_window.configure(bg="#f0f2f5")

    header = tk.Frame(p2_window, bg="#0a3d62", height=70)
    header.pack(fill="x")
    tk.Label(header, text="BANKING SYSTEM | STEP 2: ADDITIONAL DETAILS", 
             font=("Segoe UI", 14, "bold"), fg="white", bg="#0a3d62", padx=30).pack(side="left", pady=20)

    container = tk.Frame(p2_window, bg="white", padx=30, pady=20, highlightthickness=1, highlightbackground="#dcdde1")
    container.place(relx=0.5, rely=0.55, anchor="center", relwidth=0.85, relheight=0.75)

    draw_progress_bar(container, 2)

    content_frame = tk.Frame(container, bg="white")
    content_frame.pack(fill="both", expand=True)

    form_left = tk.Frame(content_frame, bg="white")
    form_left.pack(side="left", fill="both", expand=True, padx=(0, 20))

    image_right = tk.Frame(content_frame, bg="white")
    image_right.pack(side="right", fill="both", expand=True, padx=10)

    # Page 2 Image
    try:
        side_img_path = r"C:\Users\pc\Desktop\ATM_Project\icons\signup2.png"
        s_img = Image.open(side_img_path)
        w = int(p2_window.winfo_screenwidth() * 0.2)
        h = int(p2_window.winfo_screenheight() * 0.4)
        s_img = s_img.resize((w, h), Image.Resampling.LANCZOS)
        s_photo = ImageTk.PhotoImage(s_img)
        side_img_label = tk.Label(image_right, image=s_photo, bg="white")
        side_img_label.image = s_photo
        side_img_label.pack(pady=40)
    except:
        tk.Label(image_right, text="[Upload signup2.png in icons folder]", 
                font=("Segoe UI", 10), fg="#b2bec3", bg="white").pack(pady=100)

    # Store combo boxes for later retrieval
    combos = {}
    
    def create_dropdown(parent, label, options, row):
        tk.Label(parent, text=label, font=("Segoe UI", 10, "bold"), bg="white", fg="#2d3436").grid(row=row, column=0, sticky="w", pady=8)
        combo = ttk.Combobox(parent, values=options, font=("Segoe UI", 11), state="readonly", width=35)
        combo.grid(row=row, column=1, sticky="w", pady=8, padx=10)
        combo.set(options[0])
        return combo

    combos['religion'] = create_dropdown(form_left, "Religion:", ["Muslim", "Christian", "Hindu", "Other"], 0)
    combos['category'] = create_dropdown(form_left, "Category:", ["General", "OBC", "SC/ST"], 1)
    combos['income'] = create_dropdown(form_left, "Income:", ["Less than 50,000", "50,000 – 1,00,000", "1,00,000 – 5,00,000", "Above 5,00,000"], 2)
    combos['education'] = create_dropdown(form_left, "Education:", ["Non-Graduate", "Graduate", "Post-Graduate"], 3)
    combos['occupation'] = create_dropdown(form_left, "Occupation:", ["Student", "Business", "Job", "Self-Employed"], 4)

    tk.Label(form_left, text="CNIC / ID Number:", font=("Segoe UI", 10, "bold"), bg="white").grid(row=5, column=0, sticky="w", pady=8)
    cnic_entry = tk.Entry(form_left, font=("Segoe UI", 11), bg="#f8f9fa", width=37, 
                         relief="flat", highlightthickness=1, highlightbackground="#dcdde1")
    cnic_entry.grid(row=5, column=1, sticky="w", pady=8, padx=10, ipady=3)

    def save_page2():
        # Validate CNIC
        if not cnic_entry.get().strip():
            messagebox.showwarning("Validation Error", "Please enter CNIC/ID Number")
            return
        
        # Save data
        user_data['religion'] = combos['religion'].get()
        user_data['category'] = combos['category'].get()
        user_data['income'] = combos['income'].get()
        user_data['education'] = combos['education'].get()
        user_data['occupation'] = combos['occupation'].get()
        user_data['cnic'] = cnic_entry.get().strip()
        
        p2_window.destroy()
        open_page_3()

    def go_back():
        p2_window.destroy()
        open_signup()

    btn_frame = tk.Frame(form_left, bg="white")
    btn_frame.grid(row=7, column=0, columnspan=2, pady=30)

    tk.Button(btn_frame, text="← PREVIOUS", font=("Segoe UI", 10, "bold"), bg="#bdc3c7", fg="white", 
              relief="flat", cursor="hand2", width=15, height=2, 
              command=go_back).pack(side="left", padx=10)

    tk.Button(btn_frame, text="NEXT →", font=("Segoe UI", 10, "bold"), bg="#0fbcf9", fg="white", 
              relief="flat", cursor="hand2", width=15, height=2,
              command=save_page2).pack(side="left", padx=10)

# --- Page 3 ---
def open_page_3():
    global user_data
    
    p3_window = tk.Toplevel()
    p3_window.title("ATM Registration - Page 3")
    p3_window.state('zoomed')
    p3_window.configure(bg="#f0f2f5")

    header = tk.Frame(p3_window, bg="#0a3d62", height=70)
    header.pack(fill="x")
    tk.Label(header, text="BANKING SYSTEM | STEP 3: ACCOUNT DETAILS", 
             font=("Segoe UI", 14, "bold"), fg="white", bg="#0a3d62", padx=30).pack(side="left", pady=20)

    container = tk.Frame(p3_window, bg="white", padx=50, pady=20, highlightthickness=1, highlightbackground="#dcdde1")
    container.place(relx=0.5, rely=0.55, anchor="center", relwidth=0.8, relheight=0.7)

    draw_progress_bar(container, 3)

    tk.Label(container, text="Account Type:", font=("Segoe UI", 12, "bold"), bg="white").pack(anchor="w", pady=5)
    acc_type = tk.StringVar(value="Savings")
    type_frame = tk.Frame(container, bg="white")
    type_frame.pack(anchor="w", pady=5)
    for text, val in [("Savings Account", "Savings"), ("Current Account", "Current"), ("Fixed Deposit", "Fixed")]:
        tk.Radiobutton(type_frame, text=text, variable=acc_type, value=val, bg="white", font=("Segoe UI", 10)).pack(side="left", padx=10)

    tk.Label(container, text="Services Required:", font=("Segoe UI", 12, "bold"), bg="white").pack(anchor="w", pady=(15, 5))
    serv_frame = tk.Frame(container, bg="white")
    serv_frame.pack(anchor="w")
    services = ["ATM Card", "Internet Banking", "Mobile Banking", "SMS Alerts", "E-Statement", "Cheque Book"]
    
    # Store service checkbuttons
    service_vars = []
    for i, serv in enumerate(services):
        var = tk.BooleanVar()
        service_vars.append((serv, var))
        tk.Checkbutton(serv_frame, text=serv, variable=var, bg="white", 
                      font=("Segoe UI", 10), width=20, anchor="w").grid(row=i//2, column=i%2, pady=2)

    decl_var = tk.BooleanVar()
    tk.Checkbutton(container, text="I hereby declare that the details provided are correct to the best of my knowledge.", 
                   variable=decl_var, bg="white", font=("Segoe UI", 9, "bold")).pack(pady=20)

    def go_back():
        p3_window.destroy()
        open_page_2()

    def finish_registration():
        if not decl_var.get():
            messagebox.showwarning("Warning", "Please accept the declaration to proceed.")
            return
        
        # Add account type and services to user_data
        user_data['account_type'] = acc_type.get()
        selected_services = [serv for serv, var in service_vars if var.get()]
        user_data['services'] = ", ".join(selected_services) if selected_services else "None"
        
        # Create user in database
        success, result = create_user(user_data)
        
        if success:
            card_number, pin = result
            messagebox.showinfo(
                "Registration Successful!", 
                f"Your account has been created successfully!\n\n"
                f"Card Number: {card_number}\n"
                f"PIN: {pin}\n\n"
                f"Please save these credentials for login."
            )
            p3_window.destroy()
        else:
            messagebox.showerror("Registration Failed", f"Failed to create account: {result}")

    btn_frame = tk.Frame(container, bg="white")
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="← PREVIOUS", font=("Segoe UI", 11, "bold"), bg="#bdc3c7", fg="white", 
              relief="flat", width=18, height=2, command=go_back).pack(side="left", padx=10)

    tk.Button(btn_frame, text="SUBMIT & FINISH", font=("Segoe UI", 11, "bold"), bg="#05c46b", fg="white", 
              relief="flat", width=20, height=2, command=finish_registration).pack(side="left", padx=10)

# --- Main ---
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    open_signup()
    root.mainloop()