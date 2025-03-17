import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import sqlite3
import re
from PIL import Image, ImageTk

# Connect to SQLite database
conn = sqlite3.connect('blood_donation_platform.db')
cursor = conn.cursor()

# Create tables
#display donors
cursor.execute('''
CREATE TABLE IF NOT EXISTS donors (
    donor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    dob TEXT,
    blood_type TEXT,
    contact TEXT
)''')
#blood stock
cursor.execute('''
CREATE TABLE IF NOT EXISTS blood_stock (
    blood_type TEXT PRIMARY KEY,
    quantity INTEGER
)''')
#blood requests
cursor.execute('''
CREATE TABLE IF NOT EXISTS blood_requests (
    request_id INTEGER PRIMARY KEY AUTOINCREMENT,
    requestor_name TEXT,
    contact_number TEXT,
    email_address TEXT,
    blood_type_required TEXT,
    quantity_needed INTEGER,
    urgency TEXT,
    patient_name TEXT,
    datetime TEXT DEFAULT CURRENT_TIMESTAMP,
    status TEXT
)''')

# Function to validate date format (YYYY-MM-DD)
def validate_date_input(input_date):
    # Regular expression to match date format YYYY-MM-DD
    date_pattern = r"^\d{4}-\d{2}-\d{2}$"

    if not re.match(date_pattern, input_date): # Check if the input matches the pattern
        return False

    year, month, day = map(int, input_date.split('-'))  # Extract the year, month, and day from the input string

    if month < 1 or month > 12: # Check if the month is valid (1 to 12)
        return False

    if not is_valid_day_for_month(month, day, year):   # Check if the day is valid for the given month
        return False

    return True

# Function to check if the day is valid for the given month
def is_valid_day_for_month(month, day, year):
    # Days in each month (for non-leap year)
    days_in_month = {
        1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
        7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
    }
    # Check if the month is February and account for leap years
    if month == 2:
        # Leap year check (divisible by 4, but not by 100 unless divisible by 400)
        if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)):
            days_in_month[2] = 29  # February has 29 days in a leap year

    # Check if the day is valid for the month
    if day < 1 or day > days_in_month[month]:
        return False

    return True

# Function to check if a date is in the future
def is_future_date(date_str):
    try:
        entered_date = datetime.strptime(date_str, "%Y-%m-%d")
        current_date = datetime.now()
        return entered_date > current_date
    except ValueError:
        return False

def show_message(message):      # Function to show a message box
    messagebox.showinfo("Input Error", message)

# Function to calculate age
def calculate_age(dob):
    today = datetime.today()
    dob_date = datetime.strptime(dob, "%Y-%m-%d")
    age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
    return age

def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def clear_form():
    # Blood request form Entry fields
    blood_request_entries = [
        entry_requestor_name, entry_organization_name, entry_requestor_contact, entry_requestor_email,
        entry_quantity_needed, entry_patient_name, entry_patient_age, entry_patient_condition,
        entry_special_requirements
    ]

    # Donor form Entry fields
    donor_entries = [
        entry_name, entry_dob, entry_address, entry_contact, entry_email,
        entry_nationality, entry_last_donation, entry_emergency_contact_name, entry_emergency_contact_number
    ]

    # Clear all Entry fields (blood request + donor form)
    for entry in blood_request_entries + donor_entries:
        entry.delete(0, tk.END)

    # Reset all StringVar and IntVar values for both forms
    var_blood_type_request.set('')
    var_urgency.set('')
    var_purpose.set('')
    var_approval.set(0)

    var_gender.set('')
    var_blood_type.set('')
    var_transfusion.set(0)
    var_chronic_illness.set(0)
    var_allergies.set(0)
    var_surgeries.set(0)
    var_medication.set(0)
    var_high_risk.set(0)
    var_donated_before.set(0)
    var_consent.set(0)

# Function to handle Donor Registration form submission
def submit_donor():
    name = entry_name.get()
    gender = var_gender.get()
    dob = entry_dob.get()
    age = None  # None because age is calculated by calculate_age function and only people of age 18-65 yrs are eligible to donate
    blood_type = var_blood_type.get()
    address = entry_address.get()
    contact = entry_contact.get()
    email = entry_email.get()
    nationality = entry_nationality.get()
    transfusion = var_transfusion.get()
    chronic_illness = var_chronic_illness.get()
    allergies = var_allergies.get()
    surgeries = var_surgeries.get()
    medication = var_medication.get()
    high_risk = var_high_risk.get()
    donated_before = var_donated_before.get()
    last_donation = entry_last_donation.get()
    consent = var_consent.get()
    emergency_contact_name = entry_emergency_contact_name.get()
    emergency_contact_number = entry_emergency_contact_number.get()

    # Basic validation for ensuring required fields are filled
    if not (name and gender and email and nationality and dob and blood_type and contact):
        messagebox.showwarning("Input Error", "Please fill in all mandatory fields.")
        return

    try:
        age = calculate_age(dob)
    except ValueError:
        show_message("Invalid Date of Birth format. Please use YYYY-MM-DD.")
        return

    if is_future_date(entry_dob.get()):
        show_message("Date of Birth cannot be a future date.")
        return

    # Check age eligibility
    if age < 18 or age > 65:
        messagebox.showwarning("Eligibility Error", "Age must be between 18 and 65 to donate blood.")
        return

    # Validate phone number (must be 10 digits)
    if not contact.isdigit() or len(contact) != 10:
        messagebox.showwarning("Input Error", "Please enter a valid 10-digit phone number.")
        return

    # Check if email is valid
    if not is_valid_email(email):
        messagebox.showwarning("Invalid Email", "Please enter a valid email address.")
        return

    # Check medical history
    if any([transfusion, chronic_illness, allergies, surgeries, medication, high_risk]):
        messagebox.showwarning("Eligibility Error", "Donors with medical history are not eligible to donate blood.")
        return

     # Validate Last Donation Date (if provided, it must be a valid date and can't be in future)
    if entry_last_donation.get():
        if not validate_date_input(entry_last_donation.get()):
            show_message("Invalid Last Donation date format. Please use YYYY-MM-DD.")
            return

    if is_future_date(entry_last_donation.get()):
            show_message("Last donation date cannot be a future date.")
            return

    # Validate emergency contact number (must be 10 digits)
    if not emergency_contact_number.isdigit() or len(emergency_contact_number) != 10:
        messagebox.showwarning("Input Error", "Please enter a valid 10-digit emergency phone number.")
        return

    if consent != 1:
        messagebox.showwarning("Consent Error", "You must provide consent to register.")
    else:
        # Save donor details into the database
        cursor.execute('''
        INSERT INTO donors (name, dob, blood_type, contact)
        VALUES (?, ?, ?, ?)
        ''', (name, dob, blood_type, contact))

        # Commit changes and show success message
        conn.commit()
        messagebox.showinfo("Registration Successful", f"Donor {name} (Age: {age}) registered successfully!")
    clear_form()

# Function to display all donors
def display_donors():
    # Create a new window to display donor details
    donor_window = tk.Toplevel(root)
    donor_window.title("Donor List")

    # Create a treeview to display donors
    tree = ttk.Treeview(donor_window, columns=("Donor ID", "Name", "DOB", "Blood Type", "Contact"),
                        show="headings")
    tree.heading("Donor ID", text="Donor ID")
    tree.heading("Name", text="Name")
    tree.heading("DOB", text="DOB")
    tree.heading("Blood Type", text="Blood Type")
    tree.heading("Contact", text="Contact")

    tree.grid(row=0, column=0, padx=10, pady=10)

    # Fetch donor details from the database
    cursor.execute("SELECT * FROM donors")
    donors = cursor.fetchall()

    for donor in donors:
        tree.insert("", "end", values=donor)

# Function to handle blood request form submission
def submit_blood_request():
    blood_stock = 0

    requestor_name = entry_requestor_name.get()
    organization_name = entry_organization_name.get()
    contact_number = entry_requestor_contact.get()
    email_address = entry_requestor_email.get()
    blood_type_required = var_blood_type_request.get()
    quantity_needed = entry_quantity_needed.get()
    urgency = var_urgency.get()
    purpose = var_purpose.get()
    patient_name = entry_patient_name.get()
    patient_age = entry_patient_age.get()
    patient_condition = entry_patient_condition.get()
    # request_datetime = entry_request_datetime.get()   # not included this because date and time is auto generated by SQL command 'TIMESTAMP'
    special_requirements = entry_special_requirements.get()
    approval = var_approval.get()

    # Check if all fields are filled
    if not (requestor_name and contact_number and email_address and blood_type_required and quantity_needed and urgency and patient_name and patient_age and patient_condition):
        messagebox.showwarning("Input Error", "Please fill in all mandatory fields.")
        return

    # Validate phone number (must be 10 digits)
    if not contact_number.isdigit() or len(contact_number) != 10:
        messagebox.showwarning("Input Error", "Please enter a valid 10-digit phone number.")
        return

    # Check if email is valid
    if not is_valid_email(email_address):
        messagebox.showwarning("Invalid Email", "Please enter a valid email address.")
        return

    if approval != 1:
        messagebox.showwarning("Error", "You must have authorization to submit request.")
    else:
    # Fetch blood stock details to check availability
        cursor.execute("SELECT quantity FROM blood_stock WHERE blood_type = ?", (blood_type_required,))
        blood_stock = cursor.fetchone()

    if blood_stock:
        available_quantity = blood_stock[0]

        # Case 1: Sufficient stock
        if int(quantity_needed) <= available_quantity:
            status = "Fulfilled"
            # Update the blood stock quantity
            cursor.execute("UPDATE blood_stock SET quantity = quantity - ? WHERE blood_type = ?",
                           (quantity_needed, blood_type_required))
            message = f"Blood request for {patient_name} has been fulfilled."

        # Case 2: Insufficient stock (but stock available)
        elif int(quantity_needed) > available_quantity:
            status = "Pending"
            message = f"Insufficient stock for {blood_type_required}. Available stock: {available_quantity} units. Blood request for {patient_name} is pending."

    else:
        # Case 3: No stock available
        status = "Pending"
        message = f"Currently out of stock for {blood_type_required}. Blood request for {patient_name} is pending."

    # Save the blood request details with the status (Pending or Fulfilled)
    cursor.execute('''INSERT INTO blood_requests (requestor_name, contact_number, email_address, blood_type_required, quantity_needed, urgency, patient_name, status)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                   (requestor_name, contact_number, email_address, blood_type_required, quantity_needed, urgency,
                    patient_name, status))

    # Commit changes and show the appropriate message
    conn.commit()
    messagebox.showinfo("Request Submitted", message)
    clear_form()


# Function to display blood stock
def display_blood_stock():
    stock_window = tk.Toplevel(root)
    stock_window.title("Blood Stock")

    # Create a treeview to display blood stock
    tree = ttk.Treeview(stock_window, columns=("Blood Type", "Quantity"), show="headings")
    tree.heading("Blood Type", text="Blood Type")
    tree.heading("Quantity", text="Quantity")
    tree.grid(row=0, column=0, padx=10, pady=10)

    # Fetch blood stock details
    cursor.execute("SELECT * FROM blood_stock")
    stock = cursor.fetchall()

    for stock_item in stock:
        tree.insert("", "end", values=stock_item)

# Function to display blood request details
def display_blood_request_details():
    request_window = tk.Toplevel(root)
    request_window.title("Blood Request Details")

    # Create a treeview to display blood requests
    tree = ttk.Treeview(request_window, columns=("Request ID", "Requestor_name", "Contact", "Email", "Blood Type", "Quantity", "Urgency", "Patient Name","Datetime", "Status"), show="headings")
    tree.heading("Request ID", text="Request ID")
    tree.heading("Requestor_name", text="Requestor Name")
    tree.heading("Contact", text="Contact")
    tree.heading("Email", text="Email")
    tree.heading("Blood Type", text="Blood Type")
    tree.heading("Quantity", text="Quantity")
    tree.heading("Urgency", text="Urgency")
    tree.heading("Patient Name", text="Patient Name")
    tree.heading("Datetime", text="Datetime")
    tree.heading("Status", text="Status")

    # Set column widths
    tree.column("Request ID", width=70, anchor="center")
    tree.column("Requestor_name", width=150, anchor="center")
    tree.column("Contact", width=100, anchor="center")
    tree.column("Email", width=200, anchor="center")
    tree.column("Blood Type", width=100, anchor="center")
    tree.column("Quantity", width=80, anchor="center")
    tree.column("Urgency", width=100, anchor="center")
    tree.column("Patient Name", width=100, anchor="center")
    tree.column("Datetime", width=150, anchor="center")
    tree.column("Status", width=100, anchor="center")

    # Place the treeview in the window using grid layout
    tree.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

    # make the window size adjustable
    request_window.grid_rowconfigure(0, weight=1)
    request_window.grid_columnconfigure(0, weight=1)

    # Fetch blood request details
    cursor.execute("SELECT * FROM blood_requests")
    requests = cursor.fetchall()

    for request in requests:
        tree.insert("", "end", values=request)

# Function to show the form
def show_donor_registration_form():
    blood_request_form_frame.grid_forget()  # Hide the blood request form
    donor_form_frame.grid(row=1, column=0, sticky="nsew")#padx=10, #pady=10)  # Show the donor form

def show_blood_request_form():
    donor_form_frame.grid_forget()  # Hide the donor registration form
    blood_request_form_frame.grid(row=1, column=0,sticky="nsew") #padx=10, pady=10)  # Show the blood request form

# Main Tkinter window
root = tk.Tk()
root.title('"Blood Link" – Blood donation and request management platform')
root.geometry("800x600")

# Load the background image
bg_image = Image.open("B5.jpg")
bg_image = bg_image.resize((root.winfo_screenwidth(), root.winfo_screenheight()), Image.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)

canvas = tk.Canvas(root, width=200, height=200)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=bg_photo, anchor="nw")

# Create a scrollable frame for long forms
scrollable_frame = tk.Frame(canvas, bg="white")
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# Create frames for the forms
donor_form_frame = tk.Frame(scrollable_frame, bg="white")  # Donor registration form frame
blood_request_form_frame = tk.Frame(scrollable_frame, bg="white")  # Blood request form frame

# Radio button for form selection
var_form_selection = tk.StringVar()
tk.Label(scrollable_frame, text="Select the form type", font=("georgia", 14, "bold")).grid(row=0,column=0,padx=10,pady=5)
tk.Radiobutton(scrollable_frame, text="Donor Registration", variable=var_form_selection, value="donor",
               command=show_donor_registration_form, font=("georgia", 14,"bold")).grid(row=0, column=1, padx=10, pady=5, sticky="w")
tk.Radiobutton(scrollable_frame, text="Blood Request", variable=var_form_selection, value="request",
               command=show_blood_request_form, font=("georgia", 14,"bold")).grid(row=0, column=2, padx=10, pady=5, sticky="w")

scrollable_frame.grid_columnconfigure(0, weight=1, uniform="equal")
scrollable_frame.grid_columnconfigure(1, weight=1, uniform="equal")
scrollable_frame.grid_columnconfigure(2, weight=1, uniform="equal")

# Donor Registration Form Fields
tk.Label(donor_form_frame, text="Full Name:*",bg="white", font=("abadi", 10,"bold")).grid(row=1, column=0, sticky="w", pady=5)
entry_name = tk.Entry(donor_form_frame, width=30, bg="lightgrey", font=("abadi", 10))
entry_name.grid(row=1, column=1, pady=5)

tk.Label(donor_form_frame, text="Gender:*",bg="white", font=("abadi", 10,"bold")).grid(row=2, column=0, sticky="w", pady=5)
var_gender = tk.StringVar()
gender_menu = ttk.Combobox(donor_form_frame, textvariable=var_gender, values=["Male", "Female", "Other"],
                           state="readonly")
gender_menu.grid(row=2, column=1, pady=5)

tk.Label(donor_form_frame, text="Date of Birth (YYYY-MM-DD):*",bg="white", font=("abadi", 10,"bold")).grid(row=3, column=0, sticky="w", pady=5)
entry_dob = tk.Entry(donor_form_frame, width=30,bg="lightgrey", font=("abadi", 10))
entry_dob.grid(row=3, column=1, pady=5)

tk.Label(donor_form_frame, text="Blood Type:*",bg="white", font=("abadi", 10,"bold")).grid(row=4, column=0, sticky="w", pady=5)
var_blood_type = tk.StringVar()
blood_type_menu = ttk.Combobox(donor_form_frame, textvariable=var_blood_type,
                               values=["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"], state="readonly")
blood_type_menu.grid(row=4, column=1, pady=5)

tk.Label(donor_form_frame, text="Address:",bg="white", font=("abadi", 10,"bold")).grid(row=5, column=0, sticky="w", pady=5)
entry_address = tk.Entry(donor_form_frame, width=30,bg="lightgrey", font=("abadi", 10))
entry_address.grid(row=5, column=1, pady=5)

tk.Label(donor_form_frame, text="Contact Number:*", bg="white", font=("abadi", 10,"bold")).grid(row=6, column=0, sticky="w", pady=5)
entry_contact = tk.Entry(donor_form_frame, width=30,bg="lightgrey", font=("abadi", 10))
entry_contact.grid(row=6, column=1, pady=5)

tk.Label(donor_form_frame, text="Email Address:*",bg="white", font=("abadi", 10,"bold")).grid(row=7, column=0, sticky="w", pady=5)
entry_email = tk.Entry(donor_form_frame, width=30,bg="lightgrey", font=("abadi", 10))
entry_email.grid(row=7, column=1, pady=5)

tk.Label(donor_form_frame, text="Nationality:*",bg="white", font=("abadi", 10,"bold")).grid(row=8, column=0, sticky="w", pady=5)
entry_nationality = tk.Entry(donor_form_frame, width=30,bg="lightgrey", font=("abadi", 10))
entry_nationality.grid(row=8, column=1, pady=5)

tk.Label(donor_form_frame, text="Medical History:", bg="white", font=("abadi", 10,"bold")).grid(row=9, column=0, sticky="w", pady=5)
var_transfusion = tk.IntVar()
var_chronic_illness = tk.IntVar()
var_allergies = tk.IntVar()
var_surgeries = tk.IntVar()
var_medication = tk.IntVar()
var_high_risk = tk.IntVar()

tk.Checkbutton(donor_form_frame, text="Have you ever had a blood transfusion?", variable=var_transfusion,bg="white", font=("abadi", 10)).grid(row=10,
                                                                                                               column=0,
                                                                                                               columnspan=2,
                                                                                                               sticky="w",
                                                                                                               pady=2)
tk.Checkbutton(donor_form_frame, text="Do you have any chronic illnesses?", variable=var_chronic_illness,bg="white", font=("abadi", 10)).grid(row=11,
                                                                                                               column=0,
                                                                                                               columnspan=2,
                                                                                                               sticky="w",
                                                                                                               pady=2)
tk.Checkbutton(donor_form_frame, text="Do you have any known allergies?", variable=var_allergies,bg="white", font=("abadi", 10)).grid(row=12, column=0,
                                                                                                       columnspan=2,
                                                                                                       sticky="w",
                                                                                                       pady=2)
tk.Checkbutton(donor_form_frame, text="Have you had any surgeries in the last 12 months?", variable=var_surgeries,bg="white", font=("abadi", 10)).grid(
    row=13, column=0, columnspan=2, sticky="w", pady=2)
tk.Checkbutton(donor_form_frame, text="Are you currently on any medication?", variable=var_medication,bg="white", font=("abadi", 10)).grid(row=14,
                                                                                                            column=0,
                                                                                                            columnspan=2,
                                                                                                            sticky="w",
                                                                                                            pady=2)
tk.Checkbutton(donor_form_frame, text="Do you have a history of high-risk behavior?", variable=var_high_risk,bg="white", font=("abadi", 10)).grid(
    row=15, column=0, columnspan=2, sticky="w", pady=2)

tk.Label(donor_form_frame, text="Donor History:",bg="white", font=("abadi", 10,"bold")).grid(row=16, column=0, sticky="w", pady=5)
var_donated_before = tk.IntVar()
tk.Checkbutton(donor_form_frame, text="Have you donated blood before?", variable=var_donated_before,bg="white", font=("abadi", 10)).grid(row=17,
                                                                                                          column=0,
                                                                                                          columnspan=2,
                                                                                                          sticky="w",
                                                                                                          pady=2)
tk.Label(donor_form_frame, text="When was your last blood donation? (YYYY-MM-DD):",bg="white", font=("abadi", 10)).grid(row=18, column=0, sticky="w", pady=2)
entry_last_donation = tk.Entry(donor_form_frame, width=30,bg="lightgrey")
entry_last_donation.grid(row=18, column=1, pady=2)

tk.Label(donor_form_frame, text="Emergency Contact Information:",bg="white", font=("abadi", 10, "bold")).grid(row=19, column=0, sticky="w", pady=5)
tk.Label(donor_form_frame, text="Name:*", bg="white", font=("abadi", 10)).grid(row=20, column=0, sticky="w", pady=2)
entry_emergency_contact_name = tk.Entry(donor_form_frame, width=30,bg="lightgrey", font=("abadi", 10))
entry_emergency_contact_name.grid(row=20, column=1, pady=2)

tk.Label(donor_form_frame, text="Contact Number:*",bg="white", font=("abadi", 10)).grid(row=21, column=0, sticky="w", pady=2)
entry_emergency_contact_number = tk.Entry(donor_form_frame, width=30,bg="lightgrey", font=("abadi", 10))
entry_emergency_contact_number.grid(row=21, column=1, pady=2)

var_consent = tk.IntVar()
tk.Checkbutton(donor_form_frame, text="I consent to donate blood and acknowledge the risks.",
               variable=var_consent,bg="white", font=("abadi", 10, "bold")).grid(row=22, column=0, columnspan=2, sticky="w", pady=5)

tk.Label(donor_form_frame, text="* - Required fields",bg="white", font=("abadi", 10)).grid(row=23, column=0, sticky="w", pady=2)
# Submit Button
tk.Button(donor_form_frame, text="Submit", command=submit_donor,bg="lightgrey", font=("abadi", 10,"bold")).grid(row=24, column=0, columnspan=2, pady=10)

tk.Button(donor_form_frame, text="Display Donors", command = display_donors, font=("abadi", 10,"bold")).grid(row=25, column=0, columnspan=2, pady=10)


# Blood Request Form Fields
tk.Label(blood_request_form_frame, text="Requestor Name:*",bg="white", font=("abadi", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5)
entry_requestor_name = tk.Entry(blood_request_form_frame, width=30,bg="lightgrey", font=("abadi", 10))
entry_requestor_name.grid(row=1, column=1, pady=5)

tk.Label(blood_request_form_frame, text="Organization Name (if applicable):",bg="white", font=("abadi", 10, "bold")).grid(row=2, column=0, sticky="w", pady=5)
entry_organization_name = tk.Entry(blood_request_form_frame, width=30,bg="lightgrey", font=("abadi", 10))
entry_organization_name.grid(row=2, column=1, pady=5)

tk.Label(blood_request_form_frame, text="Contact Number:*",bg="white", font=("abadi", 10, "bold")).grid(row=3, column=0, sticky="w", pady=5)
entry_requestor_contact = tk.Entry(blood_request_form_frame, width=30,bg="lightgrey", font=("abadi", 10))
entry_requestor_contact.grid(row=3, column=1, pady=5)

tk.Label(blood_request_form_frame, text="Email Address:*",bg="white", font=("abadi", 10, "bold")).grid(row=4, column=0, sticky="w", pady=5)
entry_requestor_email = tk.Entry(blood_request_form_frame, width=30,bg="lightgrey", font=("abadi", 10))
entry_requestor_email.grid(row=4, column=1, pady=5)

tk.Label(blood_request_form_frame, text="Blood Type Required:*",bg="white", font=("abadi", 10, "bold")).grid(row=5, column=0, sticky="w", pady=5)
var_blood_type_request = tk.StringVar()
blood_type_request_menu = ttk.Combobox(blood_request_form_frame, textvariable=var_blood_type_request,
                                         values=["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"], state="readonly")
blood_type_request_menu.grid(row=5, column=1, pady=5)

tk.Label(blood_request_form_frame, text="Quantity of Blood Needed:*",bg="white", font=("abadi", 10, "bold")).grid(row=6, column=0, sticky="w", pady=5)
entry_quantity_needed = tk.Entry(blood_request_form_frame, width=30,bg="lightgrey", font=("abadi", 10))
entry_quantity_needed.grid(row=6, column=1, pady=5)

tk.Label(blood_request_form_frame, text="Urgency:*",bg="white", font=("abadi", 10, "bold")).grid(row=7, column=0, sticky="w", pady=5)
var_urgency = tk.StringVar()
urgency_menu = ttk.Combobox(blood_request_form_frame, textvariable=var_urgency, values=["Normal", "Urgent", "Critical"],
                             state="readonly")
urgency_menu.grid(row=7, column=1, pady=5)

tk.Label(blood_request_form_frame, text="Purpose of the Request:",bg="white", font=("abadi", 10, "bold")).grid(row=8, column=0, sticky="w", pady=5)
var_purpose = tk.StringVar()
purpose_menu = ttk.Combobox(blood_request_form_frame, textvariable=var_purpose,
                             values=["Medical Procedure", "Emergency", "Chronic Condition"], state="readonly")
purpose_menu.grid(row=8, column=1, pady=5)

tk.Label(blood_request_form_frame, text="Patient Name:*",bg="white", font=("abadi", 10, "bold")).grid(row=9, column=0, sticky="w", pady=5)
entry_patient_name = tk.Entry(blood_request_form_frame, width=30,bg="lightgrey", font=("abadi", 10))
entry_patient_name.grid(row=9, column=1, pady=5)

tk.Label(blood_request_form_frame, text="Patient Age:*",bg="white", font=("abadi", 10, "bold")).grid(row=10, column=0, sticky="w", pady=5)
entry_patient_age = tk.Entry(blood_request_form_frame, width=30,bg="lightgrey", font=("abadi", 10))
entry_patient_age.grid(row=10, column=1, pady=5)

tk.Label(blood_request_form_frame, text="Patient Condition:*",bg="white", font=("abadi", 10, "bold")).grid(row=11, column=0, sticky="w", pady=5)
entry_patient_condition = tk.Entry(blood_request_form_frame, width=30,bg="lightgrey", font=("abadi", 10))
entry_patient_condition.grid(row=11, column=1, pady=5)

tk.Label(blood_request_form_frame, text="Special Requirements or Notes:",bg="white", font=("abadi", 10, "bold")).grid(row=13, column=0, sticky="w", pady=5)
entry_special_requirements = tk.Entry(blood_request_form_frame, width=30,bg="lightgrey", font=("abadi", 10))
entry_special_requirements.grid(row=13, column=1, pady=5)

tk.Label(blood_request_form_frame, text="Approval/Authorization:*",bg="white", font=("abadi", 10, "bold")).grid(row=14, column=0, sticky="w", pady=5)
var_approval = tk.IntVar()
tk.Checkbutton(blood_request_form_frame, text="Request authorized by medical professional.", variable=var_approval,bg="white", font=("abadi", 10, "bold")).grid(
    row=14, column=1, pady=5)

tk.Label(blood_request_form_frame, text="* - Required fields",bg="white", font=("abadi", 10)).grid(row=15, column=0, sticky="w", pady=2)
tk.Button(blood_request_form_frame, text="Submit Blood Request", command=submit_blood_request,bg="lightgrey", font=("abadi", 10,"bold")).grid(row=16, column=0, columnspan=2, pady=20)

# Add buttons under the blood request form
tk.Button(blood_request_form_frame, text="Display Blood Stock", command=display_blood_stock, font=("abadi", 10,"bold")).grid(row=17, column=0, columnspan=2, pady=10)
tk.Button(blood_request_form_frame, text="Display Blood Request Details", command=display_blood_request_details, font=("abadi", 10,"bold")).grid(row=18, column=0, columnspan=2, pady=10)

# Run the Tkinter loop
root.mainloop()



