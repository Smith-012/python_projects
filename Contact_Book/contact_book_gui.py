import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import re
import csv

DB_FILE = "contacts.db"

# Regex
EMAIL_GMAIL_RE = re.compile(r"^[^@\s]+@gmail\.com$", re.IGNORECASE)
NAME_ALLOWED_RE = re.compile(r"^[A-Za-z\s]*$")
DIGITS_RE = re.compile(r"^\d*$")

# ---------------------------
# Helpers
# ---------------------------
def only_digits(s: str) -> str:
    return "".join(ch for ch in s if ch.isdigit())

def format_phone_10(digits: str) -> str:
    """Return formatted ###-###-#### for up to 10 digits."""
    d = only_digits(digits)[:10]
    if len(d) <= 3:
        return d
    if len(d) <= 6:
        return f"{d[:3]}-{d[3:]}"
    return f"{d[:3]}-{d[3:6]}-{d[6:]}"

def titlecase_letters_and_spaces(text: str) -> str:
    """
    Keep only letters and spaces (extra chars removed),
    lowercase everything then capitalize first letter of each word.
    """
    filtered = "".join(ch for ch in text if (ch.isalpha() or ch.isspace()))
    filtered = filtered.lower()
    # manual title-casing so multiple spaces are handled
    out = []
    prev_space = True
    for ch in filtered:
        if prev_space and ch.isalpha():
            out.append(ch.upper())
            prev_space = False
        else:
            out.append(ch)
            prev_space = ch.isspace()
    return "".join(out)

# ---------------------------
# Database Layer
# ---------------------------
class ContactDB:
    def __init__(self, path=DB_FILE):
        self.conn = sqlite3.connect(path)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                country_code TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                created_at TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def add(self, name, country_code, phone_digits, email, address):
        self.conn.execute(
            "INSERT INTO contacts (name, country_code, phone, email, address, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (name.strip(), country_code.strip(), phone_digits.strip(), email.strip(), address.strip(),
             datetime.utcnow().isoformat()),
        )
        self.conn.commit()

    def update(self, cid, name, country_code, phone_digits, email, address):
        self.conn.execute(
            "UPDATE contacts SET name=?, country_code=?, phone=?, email=?, address=? WHERE id=?",
            (name.strip(), country_code.strip(), phone_digits.strip(), email.strip(), address.strip(), cid),
        )
        self.conn.commit()

    def delete(self, cid):
        self.conn.execute("DELETE FROM contacts WHERE id=?", (cid,))
        self.conn.commit()

    def list(self, query=""):
        query = (query or "").strip()
        cur = self.conn.cursor()
        if query:
            like = f"%{query}%"
            cur.execute(
                "SELECT id, name, country_code, phone, email, address, created_at "
                "FROM contacts WHERE name LIKE ? OR phone LIKE ? "
                "ORDER BY name COLLATE NOCASE",
                (like, like),
            )
        else:
            cur.execute(
                "SELECT id, name, country_code, phone, email, address, created_at "
                "FROM contacts ORDER BY name COLLATE NOCASE"
            )
        return cur.fetchall()

    def export_csv(self, path):
        rows = self.list()
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["id", "name", "country_code", "phone", "email", "address", "created_at"])
            for r in rows:
                w.writerow(r)

# ---------------------------
# GUI Layer
# ---------------------------
class ContactBookApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Contact Book")
        self.geometry("980x600")
        self.minsize(920, 560)
        self.db = ContactDB()
        self.selected_id = None
        self.dark_mode = True   # default theme

        self._create_styles()
        self._build_ui()
        self.refresh_table()

        # ESC to quit
        self.bind("<Escape>", lambda e: self.destroy())

    # ---------------- STYLES / THEME ----------------
    def _create_styles(self):
        self.configure(bg="#0b1220" if self.dark_mode else "#f4f6fb")
        s = ttk.Style(self)
        try:
            s.theme_use("clam")
        except tk.TclError:
            pass

        if self.dark_mode:
            bg = "#0b1220"
            fg = "#e6edf7"
            entry_bg = "#0f172a"
            err_bg = "#3a0b0b"
            ghost_fg = "#9fb7ff"
        else:
            bg = "#f4f6fb"
            fg = "#0b1220"
            entry_bg = "#ffffff"
            err_bg = "#ffe5e5"
            ghost_fg = "#1b3a8c"

        self.configure(bg=bg)
        s.configure("TFrame", background=bg)
        s.configure("TLabel", background=bg, foreground=fg)
        s.configure("Title.TLabel", background=bg, foreground=fg, font=("Segoe UI", 16, "bold"))
        s.configure("Lbl.TLabel", background=bg, foreground=fg, font=("Segoe UI", 10))

        s.configure("Good.TEntry", fieldbackground=entry_bg, foreground=fg)
        s.configure("Error.TEntry", fieldbackground=err_bg, foreground="#000000" if not self.dark_mode else "#ffffff")

        s.configure("TButton", font=("Segoe UI", 10, "bold"))
        s.map("TButton",
              background=[("!disabled", "#1b2a4a" if self.dark_mode else "#c7d2fe"),
                          ("active", "#23365f" if self.dark_mode else "#a5b4fc")],
              foreground=[("!disabled", fg)])

        s.configure("Ghost.TButton", padding=6,
                    background=bg, foreground=ghost_fg, borderwidth=1, relief="solid")
        s.map("Ghost.TButton", background=[("active", "#152039" if self.dark_mode else "#e2e8f0")])

    # ---------------- BUILD UI ----------------
    def _build_ui(self):
        root = ttk.Frame(self, padding=14)
        root.pack(fill="both", expand=True)

        # Top bar
        top = ttk.Frame(root)
        top.pack(fill="x", pady=(0, 10))

        ttk.Label(top, text="Contact Book", style="Title.TLabel").pack(side="left")

        # Theme toggle
        self.theme_var = tk.BooleanVar(value=self.dark_mode)
        theme_btn = ttk.Checkbutton(top, text="Dark Mode", variable=self.theme_var,
                                    command=self._toggle_theme, style="TCheckbutton")
        theme_btn.pack(side="left", padx=(12, 0))

        # File menu (Import / Export)
        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Import CSV", command=self.import_csv)
        file_menu.add_command(label="Export CSV", command=self.export_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        menu_bar.add_cascade(label="File", menu=file_menu)
        self.config(menu=menu_bar)

        # Search
        self.search_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.search_var, width=30, style="Good.TEntry").pack(side="right", padx=(6, 0))
        ttk.Button(top, text="Search", command=self.refresh_table).pack(side="right")

        # Split pane
        main = ttk.Frame(root)
        main.pack(fill="both", expand=True)

        # --- LEFT: Form ---
        form = ttk.Frame(main)
        form.pack(side="left", fill="y", padx=(0, 16))

        # Name
        ttk.Label(form, text="Name :", style="Lbl.TLabel").grid(row=0, column=0, sticky="w")
        self.name_var = tk.StringVar()
        self.name_ent = ttk.Entry(form, textvariable=self.name_var, width=30, style="Good.TEntry")
        self.name_ent.grid(row=0, column=1, pady=5, sticky="w")

        # Phone row
        ttk.Label(form, text="Phone :", style="Lbl.TLabel").grid(row=1, column=0, sticky="w")
        phone_row = ttk.Frame(form)
        phone_row.grid(row=1, column=1, sticky="w")

        self.country_var = tk.StringVar(value="+91")
        codes = ["+1","+7","+20","+33","+44","+49","+61","+81","+91","+92","+94","+971","+974","+966","+880"]
        self.country_menu = ttk.Combobox(phone_row, textvariable=self.country_var, values=codes,
                                         width=6, state="readonly")
        self.country_menu.pack(side="left")

        self.phone_var = tk.StringVar()
        self.phone_ent = ttk.Entry(phone_row, textvariable=self.phone_var, width=24, style="Good.TEntry")
        self.phone_ent.pack(side="left", padx=(8, 0))

        self.phone_help = ttk.Label(form, text="", style="Lbl.TLabel", foreground="#b91c1c")
        self.phone_help.grid(row=2, column=1, sticky="w")

        # Email
        ttk.Label(form, text="Email :", style="Lbl.TLabel").grid(row=3, column=0, sticky="w")
        self.email_var = tk.StringVar()
        self.email_ent = ttk.Entry(form, textvariable=self.email_var, width=30, style="Good.TEntry")
        self.email_ent.grid(row=3, column=1, pady=5, sticky="w")

        self.email_help = ttk.Label(form, text="", style="Lbl.TLabel", foreground="#b91c1c")
        self.email_help.grid(row=4, column=1, sticky="w")

        # Address
        ttk.Label(form, text="Address :", style="Lbl.TLabel").grid(row=5, column=0, sticky="w")
        self.address_var = tk.StringVar()
        self.address_ent = ttk.Entry(form, textvariable=self.address_var, width=30, style="Good.TEntry")
        self.address_ent.grid(row=5, column=1, pady=5, sticky="w")

        # Buttons row
        btns = ttk.Frame(form)
        btns.grid(row=6, column=0, columnspan=2, pady=15, sticky="w")
        ttk.Button(btns, text="Add Contact", command=self.add_contact).pack(side="left", padx=3)
        ttk.Button(btns, text="Update", command=self.update_contact).pack(side="left", padx=3)
        ttk.Button(btns, text="Delete", command=self.delete_contact).pack(side="left", padx=3)
        ttk.Button(btns, text="Clear", style="Ghost.TButton", command=self.clear_form).pack(side="left", padx=3)
        ttk.Button(btns, text="Import CSV", style="Ghost.TButton", command=self.import_csv).pack(side="left", padx=3)
        ttk.Button(btns, text="Export CSV", style="Ghost.TButton", command=self.export_csv).pack(side="left", padx=3)

        # --- RIGHT: Table ---
        cols = ("id", "name", "country", "phone", "email", "address")
        self.tree = ttk.Treeview(main, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c.capitalize())
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("name", width=150)
        self.tree.column("country", width=80)
        self.tree.column("phone", width=120)
        self.tree.column("email", width=200)
        self.tree.column("address", width=220)
        self.tree.pack(side="left", fill="both", expand=True)
        ttk.Scrollbar(main, orient="vertical", command=self.tree.yview).pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.bind("<Double-1>", self.load_to_form)

        # VALIDATION BINDINGS
        self.phone_ent.bind("<KeyRelease>", self._phone_runtime_check)
        self.email_ent.bind("<KeyRelease>", self._gmail_runtime_check)
        self.name_ent.bind("<KeyRelease>", self._name_runtime_capitalize)

    # ---------------- THEME TOGGLE ----------------
    def _toggle_theme(self):
        self.dark_mode = bool(self.theme_var.get())
        self._create_styles()
        # refresh helper label colors to ensure contrast
        self.phone_help.configure(foreground="#b91c1c")
        self.email_help.configure(foreground="#b91c1c")

    # ---------------- VALIDATION (RUNTIME) ----------------
    def _style_field(self, ent, ok):
        ent.configure(style="Good.TEntry" if ok else "Error.TEntry")

    def _name_runtime_capitalize(self, _e=None):
        """
        Allow only letters/spaces, hard-cap to 20 chars,
        and format as Title Case (first letter of each word uppercase, rest lowercase).
        """
        raw = self.name_var.get()
        # keep only letters/spaces and cap length
        filtered = "".join(ch for ch in raw if (ch.isalpha() or ch.isspace()))[:20]
        # lowercase all then capitalize word initials
        formatted = titlecase_letters_and_spaces(filtered)
        if formatted != raw:
            self.name_var.set(formatted)
        self._style_field(self.name_ent, bool(formatted))

    def _phone_runtime_check(self, _e=None):
        # allow typing with auto-format; validate on digits count
        raw = self.phone_var.get()
        digits = only_digits(raw)[:10]
        self.phone_var.set(digits)

        if len(digits) == 0:
            self._style_field(self.phone_ent, False)
            self.phone_help.config(text="Phone is required.")
        elif len(digits) < 10:
            self._style_field(self.phone_ent, False)
            self.phone_help.config(text="Phone must be exactly 10 digits.")
        else:
            self._style_field(self.phone_ent, True)
            self.phone_help.config(text="")

    def _gmail_runtime_check(self, _e=None):
        # hard-cap to 50 chars while typing
        text = self.email_var.get()
        if len(text) > 50:
            text = text[:50]
            self.email_var.set(text)

        text = text.strip()
        if not text:
            self._style_field(self.email_ent, False)
            self.email_help.config(text="Email is required.")
            return
        if not EMAIL_GMAIL_RE.match(text):
            self._style_field(self.email_ent, False)
            self.email_help.config(text="Email must be a valid Gmail address (example@gmail.com).")
            return
        self._style_field(self.email_ent, True)
        self.email_help.config(text="")

    def _mark_empty_errors(self):
        empty = False
        for ent, val in [
            (self.name_ent, self.name_var.get().strip()),
            (self.phone_ent, only_digits(self.phone_var.get())),
            (self.email_ent, self.email_var.get().strip()),
            (self.address_ent, self.address_var.get().strip()),
        ]:
            if not val:
                self._style_field(ent, False)
                empty = True
        if empty:
            messagebox.showerror("Missing Data", "Please fill in all required fields.")
        return empty

    def _validate_all_rules(self):
        if self._mark_empty_errors():
            return False

        name = self.name_var.get().strip()
        phone_digits = only_digits(self.phone_var.get())
        email = self.email_var.get().strip()

        # Name: letters & spaces only, <= 20
        if not NAME_ALLOWED_RE.fullmatch(name) or len(name) > 20:
            messagebox.showwarning("Invalid Name", "Name must be letters/spaces only and ≤ 20 characters.")
            self._style_field(self.name_ent, False)
            return False

        # Phone: exactly 10 digits
        if not DIGITS_RE.fullmatch(phone_digits) or len(phone_digits) != 10:
            messagebox.showwarning("Invalid Phone", "Phone number must be exactly 10 digits.")
            self._style_field(self.phone_ent, False)
            return False

        # Email: gmail only, ≤ 50
        if len(email) > 50 or not EMAIL_GMAIL_RE.match(email):
            messagebox.showwarning("Invalid Email", "Email must be a Gmail address and ≤ 50 characters.")
            self._style_field(self.email_ent, False)
            return False

        return True

    # ---------------- CRUD ----------------
    def add_contact(self):
        if not self._validate_all_rules():
            return
        self.db.add(
            self.name_var.get().strip(),
            self.country_var.get().strip(),
            only_digits(self.phone_var.get()),
            self.email_var.get().strip(),
            self.address_var.get().strip(),
        )
        self.refresh_table()
        self.clear_form()
        messagebox.showinfo("Success", "Contact added successfully!")

    def update_contact(self):
        if not self.selected_id:
            messagebox.showinfo("Select", "Select a contact first.")
            return
        if not self._validate_all_rules():
            return
        self.db.update(
            self.selected_id,
            self.name_var.get().strip(),
            self.country_var.get().strip(),
            only_digits(self.phone_var.get()),
            self.email_var.get().strip(),
            self.address_var.get().strip(),
        )
        self.refresh_table()
        messagebox.showinfo("Updated", "Contact updated successfully!")

    def delete_contact(self):
        if not self.selected_id:
            messagebox.showinfo("Select", "Select a contact to delete.")
            return
        if messagebox.askyesno("Confirm", "Delete this contact?"):
            self.db.delete(self.selected_id)
            self.refresh_table()
            self.clear_form()
            messagebox.showinfo("Deleted", "Contact removed.")

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        # Show formatted phone with country code in the table
        for cid, name, cc, phone_digits, email, addr, _ in self.db.list(self.search_var.get()):
            formatted = format_phone_10(phone_digits) if phone_digits else ""
            self.tree.insert("", "end", values=(cid, name, cc, f"{cc} {formatted}".strip(), email, addr))

    def load_to_form(self, _e=None):
        sel = self.tree.selection()
        if not sel:
            return
        cid, name, cc, phone_disp, email, addr = self.tree.item(sel[0])["values"]
        # phone_disp is like "+91 123-456-7890" — extract digits
        just_digits = only_digits(phone_disp)
        self.selected_id = cid
        self.name_var.set(name)
        self.country_var.set(cc)
        self.phone_var.set(format_phone_10(just_digits))
        self.email_var.set(email)
        self.address_var.set(addr)
        self._gmail_runtime_check()
        self._phone_runtime_check()
        self._name_runtime_capitalize()

    def on_select(self, _e=None):
        sel = self.tree.selection()
        if sel:
            self.selected_id = self.tree.item(sel[0])["values"][0]

    def clear_form(self):
        self.selected_id = None
        self.name_var.set("")
        self.country_var.set("+91")
        self.phone_var.set("")
        self.email_var.set("")
        self.address_var.set("")
        self.phone_help.config(text="")
        self.email_help.config(text="")
        self._style_field(self.name_ent, True)
        self._style_field(self.phone_ent, False)
        self._style_field(self.email_ent, False)
        self._style_field(self.address_ent, True)

    # ---------------- THEME & MENU ----------------
    def _toggle_theme(self):
        self.dark_mode = bool(self.theme_var.get())
        self._create_styles()
        self.phone_help.configure(foreground="#b91c1c")
        self.email_help.configure(foreground="#b91c1c")

    # ---------------- IMPORT / EXPORT ----------------
    def import_csv(self):
        path = filedialog.askopenfilename(
            title="Import Contacts from CSV",
            filetypes=[("CSV files", "*.csv")]
        )
        if not path:
            return
        added = skipped = 0
        with open(path, "r", encoding="utf-8") as f:
            sniffer = csv.Sniffer()
            sample = f.read(2048)
            f.seek(0)
            has_header = sniffer.has_header(sample)
            reader = csv.DictReader(f) if has_header else csv.reader(f)

            for row in reader:
                try:
                    if has_header:
                        name = (row.get("name") or "").strip()
                        cc = (row.get("country_code") or "+91").strip()
                        phone_digits = only_digits(row.get("phone") or "")
                        email = (row.get("email") or "").strip()
                        address = (row.get("address") or "").strip()
                    else:
                        # fallback order: name, country_code, phone, email, address
                        cols = list(row)
                        name = (cols[0] if len(cols) > 0 else "").strip()
                        cc = (cols[1] if len(cols) > 1 else "+91").strip()
                        phone_digits = only_digits(cols[2] if len(cols) > 2 else "")
                        email = (cols[3] if len(cols) > 3 else "").strip()
                        address = (cols[4] if len(cols) > 4 else "").strip()

                    # minimal validation like UI
                    # apply same name formatting & caps
                    name = titlecase_letters_and_spaces(name)[:20]

                    if (not name or not NAME_ALLOWED_RE.fullmatch(name) or len(name) > 20 or
                        len(phone_digits) != 10 or not EMAIL_GMAIL_RE.match(email) or len(email) > 50 or
                        not address):
                        skipped += 1
                        continue

                    self.db.add(name, cc, phone_digits, email, address)
                    added += 1
                except Exception:
                    skipped += 1

        self.refresh_table()
        messagebox.showinfo("Import Complete", f"Added: {added}\nSkipped: {skipped}")

    def export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="contacts.csv"
        )
        if not path:
            return
        self.db.export_csv(path)
        messagebox.showinfo("Exported", f"Contacts saved to:\n{path}")

if __name__ == "__main__":
    app = ContactBookApp()
    app.mainloop()
