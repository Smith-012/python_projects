# Contact Book Application

A modern Python Tkinter-based **Contact Management App** featuring:

- Clean GUI (Light/Dark mode)
- Add, update, delete contacts
- Search contacts
- CSV import & export
- SQLite storage
- Country-code dropdown for phone numbers
- Live validation (name, phone, email)
- Gmail-only email enforcement
- ESC key closes the app
- Auto title-case name formatting
- 10-digit phone validation (no auto formatting)
- Max length limits:
  - Name: 20 characters
  - Phone: 10 digits
  - Email: 50 characters

---

## 🚀 Features

### ✔ Add Contact  
- Requires Name, Phone, Email, Address  
- Validates in real-time  
- Prevents incomplete or invalid entries  

### ✔ Update Contact  
- Select any contact from the table  
- Edit and update instantly  

### ✔ Delete Contact  
- Confirmation dialog prevents mistakes  

### ✔ CSV Export  
Exports contacts in a clean CSV file:
```
id,name,country_code,phone,email,address,created_at
```

### ✔ CSV Import  
- Supports **header** and **no-header** CSV  
- Skips invalid rows automatically  
- Shows summary of added/skipped rows  

### ✔ Live Validation  
- **Name** → Letters & spaces only, auto Title Case, max 20  
- **Phone** → Digits only, max & exactly 10  
- **Email** → Must be `@gmail.com`, max 50  

### ✔ Dark / Light Mode Toggle  
Instant theme switching.

---

## 📁 Project Structure

```
contact_book_gui.py
contacts.db  (auto-created)
README.md
```

---

## ▶ How to Run

```
python contact_book_gui.py
```

Requires Python 3.8+.

---

## 📦 Dependencies

None! Only built-in libraries:
- sqlite3
- tkinter
- csv
- re
- datetime

---