import json
import os
import time
import re
import tkinter as tk
from tkinter import ttk, messagebox

# ---- Optional calendar support ----------------------------------------------
Calendar = None
try:
    from tkcalendar import Calendar  # pip install tkcalendar
except Exception:
    Calendar = None
# -----------------------------------------------------------------------------

DATA_FILE = "tasks.json"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")  # YYYY-MM-DD


def load_tasks():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
        tasks = []
        for t in raw:
            tasks.append({
                "id": int(t.get("id", int(time.time() * 1000))),
                "title": (t.get("title") or "").strip(),
                "done": bool(t.get("done", False)),
                "created": int(t.get("created", int(time.time()))),
                "due": (t.get("due") or "").strip(),
                "notes": (t.get("notes") or "").strip(),
            })
        return tasks
    except Exception as e:
        messagebox.showerror("Load error", f"Could not read {DATA_FILE}:\n{e}")
        return []


def save_tasks(tasks):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("Save error", f"Could not write {DATA_FILE}:\n{e}")


def is_valid_date(s: str) -> bool:
    """Accepts empty or YYYY-MM-DD that is a real calendar date."""
    if not s:
        return True
    if not DATE_RE.match(s):
        return False
    y, m, d = map(int, s.split("-"))
    import datetime
    try:
        datetime.date(y, m, d)
        return True
    except Exception:
        return False


class DatePicker(tk.Toplevel):
    """A tiny modal calendar picker (uses tkcalendar if available)."""
    def __init__(self, master, initial=""):
        super().__init__(master)
        self.title("Pick a date")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.chosen = None

        frm = ttk.Frame(self, padding=10)
        frm.pack()

        if Calendar:
            # tkcalendar widget
            self.cal = Calendar(frm, selectmode="day")
            self.cal.pack(pady=6)
        else:
            # Fallback if tkcalendar not installed
            ttk.Label(frm, text="tkcalendar not installed.\nType date below (YYYY-MM-DD).").pack(pady=8)
            self.var = tk.StringVar(value=initial)
            ttk.Entry(frm, textvariable=self.var, width=18).pack()

        btns = ttk.Frame(frm)
        btns.pack(pady=(8, 0))
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side="left", padx=4)
        ttk.Button(btns, text="OK", command=self.on_ok).pack(side="left")

    def on_ok(self):
        if Calendar:
            dt = self.cal.selection_get()  # datetime.date
            self.chosen = dt.strftime("%Y-%m-%d")
        else:
            s = (self.var.get() or "").strip()
            if not is_valid_date(s):
                messagebox.showwarning("Invalid date", "Please enter date as YYYY-MM-DD.")
                return
            self.chosen = s
        self.destroy()


class TaskDialog(tk.Toplevel):
    def __init__(self, master, title="Add Task", task=None):
        super().__init__(master)
        self.title(title)
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.result = None

        frm = ttk.Frame(self, padding=14)
        frm.grid(sticky="nsew")

        ttk.Label(frm, text="Title *").grid(row=0, column=0, sticky="w")
        self.title_var = tk.StringVar(value=(task["title"] if task else ""))
        self.title_entry = ttk.Entry(frm, textvariable=self.title_var, width=46)
        self.title_entry.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 10))

        ttk.Label(frm, text="Due (YYYY-MM-DD, optional)").grid(row=2, column=0, sticky="w")
        self.due_var = tk.StringVar(value=(task.get("due") if task else ""))
        self.due_entry = ttk.Entry(frm, textvariable=self.due_var, width=20)
        self.due_entry.grid(row=3, column=0, sticky="w")

        ttk.Button(frm, text="Pick…", command=self.pick_date).grid(row=3, column=1, padx=(8, 0))

        ttk.Label(frm, text="Notes").grid(row=4, column=0, sticky="w", pady=(10, 0))
        self.notes_text = tk.Text(frm, height=6, width=46)
        if task:
            self.notes_text.insert("1.0", task.get("notes", ""))
        self.notes_text.grid(row=5, column=0, columnspan=3, sticky="ew")

        btns = ttk.Frame(frm)
        btns.grid(row=6, column=0, columnspan=3, sticky="e", pady=(12, 0))
        ttk.Button(btns, text="Cancel", command=self.destroy).grid(row=0, column=0, padx=4)
        ttk.Button(btns, text="Save", command=self.on_ok).grid(row=0, column=1)

        self.bind("<Return>", lambda e: self.on_ok())
        self.bind("<Escape>", lambda e: self.destroy())
        self.title_entry.focus()

    def pick_date(self):
        dlg = DatePicker(self, self.due_var.get())
        self.wait_window(dlg)
        if dlg.chosen:
            self.due_var.set(dlg.chosen)

    def on_ok(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("Missing title", "Please enter a task title.")
            return
        due = self.due_var.get().strip()
        if not is_valid_date(due):
            messagebox.showwarning("Invalid date", "Please enter date as YYYY-MM-DD.")
            return

        self.result = {
            "title": title,
            "due": due,
            "notes": self.notes_text.get("1.0", "end").strip(),
        }
        self.destroy()


class ToDoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("To-Do List")
        self.geometry("800x540")
        self.minsize(760, 480)

        self.tasks = load_tasks()

        # Toolbar
        top = ttk.Frame(self, padding=(10, 10, 10, 6))
        top.pack(fill="x")
        ttk.Button(top, text="➕ Add", command=self.add_task).pack(side="left")
        ttk.Button(top, text="✏️ Edit", command=self.edit_selected).pack(side="left", padx=(6, 0))
        ttk.Button(top, text="🗑 Delete", command=self.delete_selected).pack(side="left", padx=(6, 0))
        ttk.Button(top, text="✔ Toggle Done", command=self.toggle_selected).pack(side="left", padx=(6, 0))
        ttk.Button(top, text="🧹 Clear Completed", command=self.clear_completed).pack(side="left", padx=(6, 0))
        self.stats_var = tk.StringVar()
        ttk.Label(top, textvariable=self.stats_var).pack(side="right")

        # Filter/search
        bar = ttk.Frame(self, padding=(10, 0, 10, 8))
        bar.pack(fill="x")
        ttk.Label(bar, text="Filter:").pack(side="left")
        self.filter_var = tk.StringVar(value="All")
        cb = ttk.Combobox(bar, textvariable=self.filter_var,
                          values=["All", "Active", "Completed"], width=12, state="readonly")
        cb.pack(side="left", padx=(4, 12))
        cb.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        ttk.Label(bar, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        ent = ttk.Entry(bar, textvariable=self.search_var, width=30)
        ent.pack(side="left")
        ent.bind("<KeyRelease>", lambda e: self.refresh())

        # Tree
        body = ttk.Frame(self, padding=(10, 0, 10, 10))
        body.pack(fill="both", expand=True)

        cols = ("done", "title", "due", "created", "notes")
        self.tree = ttk.Treeview(body, columns=cols, show="headings", selectmode="extended")
        self.tree.heading("done", text="✓")
        self.tree.heading("title", text="Task")
        self.tree.heading("due", text="Due")
        self.tree.heading("created", text="Created")
        self.tree.heading("notes", text="Notes")

        self.tree.column("done", width=40, anchor="center")
        self.tree.column("title", width=330, anchor="w")
        self.tree.column("due", width=110, anchor="center")
        self.tree.column("created", width=130, anchor="center")
        self.tree.column("notes", width=220, anchor="w")

        vsb = ttk.Scrollbar(body, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # Key bindings
        self.tree.bind("<Delete>", lambda e: self.delete_selected())
        self.tree.bind("<Return>", lambda e: self.toggle_selected())
        self.tree.bind("<Control-e>", lambda e: self.edit_selected())

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.refresh()

    # ---------- helpers ----------
    def _selected_task_ids(self):
        """Return list of task ids selected in the Treeview."""
        ids = []
        for iid in self.tree.selection():
            try:
                ids.append(int(self.tree.item(iid, "tags")[0]))  # we store ID in tags
            except Exception:
                pass
        return ids

    # ---------- actions ----------
    def add_task(self):
        dlg = TaskDialog(self, "Add Task")
        self.wait_window(dlg)
        if dlg.result:
            self.tasks.append({
                "id": int(time.time() * 1000),
                "title": dlg.result["title"],
                "done": False,
                "created": int(time.time()),
                "due": dlg.result["due"],
                "notes": dlg.result["notes"],
            })
            self.save_and_refresh()

    def edit_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Edit", "Select a task to edit.")
            return
        task_id = int(self.tree.item(sel[0], "tags")[0])
        task = next((t for t in self.tasks if t["id"] == task_id), None)
        if not task:
            return
        dlg = TaskDialog(self, "Edit Task", task)
        self.wait_window(dlg)
        if dlg.result:
            task["title"] = dlg.result["title"]
            task["due"] = dlg.result["due"]
            task["notes"] = dlg.result["notes"]
            self.save_and_refresh()

    def delete_selected(self):
        ids = self._selected_task_ids()
        if not ids:
            messagebox.showinfo("Delete", "Select one or more tasks to delete.")
            return
        if not messagebox.askyesno("Confirm", f"Delete {len(ids)} task(s)?"):
            return
        self.tasks = [t for t in self.tasks if t["id"] not in ids]
        self.save_and_refresh()

    def toggle_selected(self):
        ids = self._selected_task_ids()
        if not ids:
            messagebox.showinfo("Toggle", "Select one or more tasks to toggle.")
            return
        for t in self.tasks:
            if t["id"] in ids:
                t["done"] = not t["done"]
        self.save_and_refresh()

    def clear_completed(self):
        if not any(t["done"] for t in self.tasks):
            messagebox.showinfo("Clear", "No completed tasks.")
            return
        if not messagebox.askyesno("Confirm", "Clear all completed tasks?"):
            return
        self.tasks = [t for t in self.tasks if not t["done"]]
        self.save_and_refresh()

    # ---------- UI refresh ----------
    def refresh(self):
        self.tree.delete(*self.tree.get_children())

        filt = self.filter_var.get()
        q = self.search_var.get().strip().lower()

        view = []
        for t in self.tasks:
            if filt == "Active" and t["done"]:
                continue
            if filt == "Completed" and not t["done"]:
                continue
            if q:
                blob = f"{t['title']} {t.get('notes','')} {t.get('due','')}".lower()
                if q not in blob:
                    continue
            view.append(t)

        for t in sorted(view, key=lambda x: (x["done"], -x["created"])):
            created_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(t["created"]))
            done = "✓" if t["done"] else ""
            iid = str(t["id"])
            self.tree.insert(
                "", "end", iid=iid, tags=(iid,),
                values=(done, t["title"], t.get("due", ""), created_str, t.get("notes", "")),
            )

        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t["done"])
        self.stats_var.set(f"Total: {total} • Done: {completed} • Left: {total - completed}")

    def save_and_refresh(self):
        save_tasks(self.tasks)
        self.refresh()

    def on_close(self):
        save_tasks(self.tasks)
        self.destroy()


if __name__ == "__main__":
    app = ToDoApp()
    app.mainloop()
