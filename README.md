# 🩸Blood-Link🩸
### 📙**Overview**
This project is built using Python's **Tkinter** for the graphical user interface (GUI) and **SQLite** for the database. The platform allows users to:
1. **Register as blood donors** by providing personal and medical information.
2. **Request blood** by specifying the required blood type, quantity, and urgency.
3. **Manage blood stock** and track blood requests.
4. **View donor details**, blood stock levels, and blood request history.

The platform is designed to streamline the process of blood donation and requests, ensuring efficient management of blood resources.

---

### ⚙️**Features**
1. **Donor Registration**:
   - Collects **donor details** such as name, gender, date of birth, blood type, contact information, and medical history.
   - **Validates donor eligibility based on age (18–65 years) and medical history.**
   - **Stores donor information** in the `donors` table in the SQLite database.

2. **Blood Request Management**:
   - Allows **users to request blood** by providing details such as the requestor's name, contact information, required blood type, quantity, urgency, and patient information.
   - **Validates blood availability in the `blood_stock` table and updates the stock accordingly.**
   - **Tracks the status** of blood requests (e.g., "Pending" or "Fulfilled") in the `blood_requests` table.

3. **Blood Stock Management**:
   - **Tracks the available quantity** of each blood type in the `blood_stock` table.
   - **Updates stock levels automatically when a blood request is fulfilled.**

4. **Data Display**:
   - Displays a **list of registered donors** in a tabular format.
   - Shows the **current blood stock levels** for each blood type.
   - Displays detailed information about blood requests, including requestor details, patient details, and request status.

5. **Form Validation**:
   - **Validates user inputs for dates, phone numbers, email addresses, and blood types.**
   - **Ensures that mandatory fields** are filled before submission.

6. **User Interface**:
   - Provides a clean and intuitive GUI with a scrollable form for easy navigation.
   - Uses a background image to enhance the visual appeal of the application.

---

### 🌐**Technical Specifications**
1. **Programming Language**: Python
2. **GUI Framework**: Tkinter
3. **Database**: SQLite
4. **Libraries Used**:
   - `tkinter`: For creating the graphical user interface.
   - `sqlite3`: For database operations.
   - `PIL` (Pillow): For handling and displaying background images.
   - `re`: For regular expression-based validation (e.g., email and date formats).
   - `datetime`: For date-related calculations and validations.

---

### 🗂️**Database Schema**
The application uses an SQLite database (`blood_donation_platform.db`) with the following tables:

1. **`donors` Table**:
   - Stores donor information.
   - Columns:
     - `donor_id` (Primary Key, Auto-increment)
     - `name` (Text)
     - `dob` (Text, Date of Birth in `YYYY-MM-DD` format)
     - `blood_type` (Text)
     - `contact` (Text)

2. **`blood_stock` Table**:
   - Tracks the available quantity of each blood type.
   - Columns:
     - `blood_type` (Primary Key)
     - `quantity` (Integer)

3. **`blood_requests` Table**:
   - Stores details of blood requests.
   - Columns:
     - `request_id` (Primary Key, Auto-increment)
     - `requestor_name` (Text)
     - `contact_number` (Text)
     - `email_address` (Text)
     - `blood_type_required` (Text)
     - `quantity_needed` (Integer)
     - `urgency` (Text)
     - `patient_name` (Text)
     - `datetime` (Text, Timestamp of the request)
     - `status` (Text, e.g., "Pending" or "Fulfilled")

---

### 🛠️**Functionality Details**
1. **Donor Registration**:
   - Users can fill out a detailed donor registration form.
   - The form includes fields for personal information, medical history, and emergency contact details.
   - **Donor eligibility is validated based on age, medical history, and consent.**

2. **Blood Request Submission**:
   - Users can submit blood requests by specifying the required blood type, quantity, and urgency.
   - The system **checks the availability** of the requested blood type in the `blood_stock` table.
   - If sufficient stock is available, the request is marked as **"Fulfilled,"** and the stock is updated. Otherwise, the request is marked as **"Pending."**

3. **Data Display**:
   - **Users can view:**
     - A list of registered donors.
     - Current blood stock levels.
     - Detailed information about blood requests.

4. **Form Validation**:
   - Ensures that **all mandatory fields are filled.**
   - **Validates date formats, phone numbers, and email addresses.**
   - **Prevents future dates from being entered** for date of birth and last donation date.

---

### 💡**How to Run the Application**
1. **Prerequisites**:
   - Python installed.
   - Required libraries: `Pillow` (for image handling). Install it using:
     ```bash
     pip install pillow
     ```

2. **Steps**:
   - Clone the repository:
   
   - Navigate to the project directory:
     
   - Run the application:
     ```bash
     python bloodlink.py
     ```

---

### 🙌**Contributing**
Contributions are welcome! If you'd like to contribute, please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a detailed description of your changes.

---

### 🎫**License**
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---
### 📌**Conclusion**
This project ensures seamless donor registration, request processing, and real-time data visualization for effective resource management.
