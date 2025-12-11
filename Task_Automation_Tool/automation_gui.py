import os
import re
import shutil
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
from bs4 import BeautifulSoup

# -------- Settings --------
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
IMAGE_EXTS = (".jpg",".jpeg",".png",".gif",".bmp",".webp",".tif",".tiff",".heic",".heif",".svg")

class App(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=16)
        master.title("Task Automation Toolbox")
        master.minsize(900, 600)
        master.configure(bg="#0f172a")
        self._style()

        # undo + manual selection
        self._last_move_pairs = []   # [(old_path, new_path)]
        self._manual_files = []      # selected files to move manually

        nb = ttk.Notebook(self); nb.grid(row=0, column=0, sticky="nsew")
        self.rowconfigure(0, weight=1); self.columnconfigure(0, weight=1)

        self.tab_move = ttk.Frame(nb); self.tab_emails = ttk.Frame(nb); self.tab_title = ttk.Frame(nb)
        nb.add(self.tab_move, text="Move Images")
        nb.add(self.tab_emails, text="Extract Emails")
        nb.add(self.tab_title, text="Scrape Title")

        self._build_move_tab(); self._build_emails_tab(); self._build_title_tab()
        self.grid(sticky="nsew")

    # ---------- styling ----------
    def _style(self):
        s = ttk.Style()
        try: s.theme_use("clam")
        except: pass
        s.configure(".", background="#0f172a", foreground="#e2e8f0")
        s.configure("TFrame", background="#0f172a")
        s.configure("TLabel", background="#0f172a", foreground="#e2e8f0")
        s.configure("Muted.TLabel", foreground="#cbd5e1")
        s.configure("TButton", padding=10, background="#0b1220", foreground="#e2e8f0")
        s.map("TButton", background=[("active", "#1e293b")], foreground=[("active", "#e2e8f0")])
        s.configure("Accent.TButton", background="#a7f3d0", foreground="#0f172a")
        s.map("Accent.TButton", background=[("active", "#6ee7b7")], foreground=[("active", "#0f172a")])
        s.configure("Input.TEntry", foreground="#000", fieldbackground="#fff")
        s.configure("TCheckbutton", background="#0f172a", foreground="#e2e8f0")

    # ---------- Move Images tab ----------
    def _build_move_tab(self):
        f = self.tab_move
        for c in range(4): f.columnconfigure(c, weight=1)

        ttk.Label(f, text="Move image files (root only or include subfolders) or manually pick specific images.", style="Muted.TLabel")\
            .grid(row=0, column=0, columnspan=4, sticky="w", pady=(0,10))
        ttk.Label(f, text="Supported: jpg, jpeg, png, gif, bmp, webp, tif, tiff, heic, heif, svg", style="Muted.TLabel")\
            .grid(row=1, column=0, columnspan=4, sticky="w", pady=(0,8))

        # Paths
        ttk.Label(f, text="Source Folder").grid(row=2, column=0, sticky="w")
        self.src_var = tk.StringVar()
        ttk.Entry(f, textvariable=self.src_var, style="Input.TEntry").grid(row=2, column=1, sticky="ew", padx=8)
        ttk.Button(f, text="Browse", command=lambda: self._pick_dir(self.src_var)).grid(row=2, column=2, sticky="ew")

        ttk.Label(f, text="Destination Folder").grid(row=3, column=0, sticky="w", pady=(8,0))
        self.dst_var = tk.StringVar()
        ttk.Entry(f, textvariable=self.dst_var, style="Input.TEntry").grid(row=3, column=1, sticky="ew", padx=8, pady=(8,0))
        ttk.Button(f, text="Browse", command=lambda: self._pick_dir(self.dst_var)).grid(row=3, column=2, sticky="ew", pady=(8,0))

        # Options
        self.include_sub = tk.BooleanVar(value=True)
        ttk.Checkbutton(f, text="Include subfolders", variable=self.include_sub).grid(row=4, column=0, sticky="w", pady=(8,0))

        # Manual select files
        ttk.Button(f, text="Pick specific images…", command=self._pick_images).grid(row=4, column=1, sticky="w", pady=(8,0))
        self.sel_count_var = tk.StringVar(value="No manual files selected")
        ttk.Label(f, textvariable=self.sel_count_var, style="Muted.TLabel").grid(row=4, column=2, columnspan=2, sticky="w", pady=(8,0))

        # Log
        self.move_log = tk.Text(f, height=14, bg="#0b1220", fg="#e2e8f0", insertbackground="#e2e8f0")
        self.move_log.grid(row=5, column=0, columnspan=4, sticky="nsew", pady=10); f.rowconfigure(5, weight=1)

        # Buttons
        btns = ttk.Frame(f); btns.grid(row=6, column=0, columnspan=4, sticky="ew")
        for c in range(3): btns.columnconfigure(c, weight=1)
        ttk.Button(btns, text="Move Images", style="Accent.TButton", command=self._run_move)\
            .grid(row=0, column=0, sticky="ew", padx=(0,6))
        self.undo_btn = ttk.Button(btns, text="Undo Last Move", command=self._undo_move, state="disabled")
        self.undo_btn.grid(row=0, column=1, sticky="ew", padx=6)
        ttk.Button(btns, text="Clear Selection", command=self._clear_manual).grid(row=0, column=2, sticky="ew", padx=(6,0))

    def _pick_dir(self, var):
        d = filedialog.askdirectory()
        if d: var.set(d)

    def _pick_images(self):
        filetypes = [("Images","*.jpg *.jpeg *.png *.gif *.bmp *.webp *.tif *.tiff *.heic *.heif *.svg"),
                     ("All files","*.*")]
        files = filedialog.askopenfilenames(title="Select images to move…", filetypes=filetypes)
        if files:
            seen = set(self._manual_files)
            for p in files:
                if p not in seen:
                    self._manual_files.append(p)
                    seen.add(p)
            self.sel_count_var.set(f"{len(self._manual_files)} file(s) selected manually")

    def _clear_manual(self):
        self._manual_files = []
        self.sel_count_var.set("No manual files selected")

    def _iter_source_images(self, src_folder, include_subfolders):
        """Yield image files from src_folder. If include_subfolders is False,
        ONLY list files in the root (no recursion)."""
        if not src_folder or not os.path.isdir(src_folder):
            return
        if include_subfolders:
            for root, _, files in os.walk(src_folder):
                for name in files:
                    if name.lower().endswith(IMAGE_EXTS):
                        yield os.path.join(root, name)
        else:
            try:
                for name in os.listdir(src_folder):
                    p = os.path.join(src_folder, name)
                    if os.path.isfile(p) and name.lower().endswith(IMAGE_EXTS):
                        yield p
            except (FileNotFoundError, PermissionError):
                return

    def _run_move(self):
        src = self.src_var.get().strip()
        dst = self.dst_var.get().strip()
        include_sub = self.include_sub.get()

        if not dst:
            messagebox.showwarning("Missing", "Choose a destination folder.")
            return

        # Build list of files to move:
        if self._manual_files:
            files_to_move = [p for p in self._manual_files if os.path.isfile(p)]
        else:
            if not src:
                messagebox.showwarning("Missing", "Choose a source folder or pick specific images.")
                return
            files_to_move = list(self._iter_source_images(src, include_sub))

        # If root-only mode and none found, say that explicitly
        if not files_to_move:
            if not self._manual_files and not include_sub:
                messagebox.showinfo("No root images",
                                    "No images found in the selected folder (excluding subfolders).")
            else:
                messagebox.showinfo("Nothing to move",
                                    "No image files found or selected.")
            return

        def task():
            moved = 0
            pairs = []
            try:
                os.makedirs(dst, exist_ok=True)
                for old in files_to_move:
                    if not os.path.exists(old):
                        continue
                    new = os.path.join(dst, os.path.basename(old))
                    base, ext = os.path.splitext(new); k = 1
                    while os.path.exists(new):
                        new = f"{base}_{k}{ext}"; k += 1
                    shutil.move(old, new)
                    moved += 1
                    pairs.append((old, new))
                    self.move_log.insert("end", f"Moved: {old} -> {new}\n"); self.move_log.see("end")

                self._last_move_pairs = pairs
                self.undo_btn.state(["!disabled"] if pairs else ["disabled"])
                if self._manual_files:
                    self._clear_manual()
                messagebox.showinfo("Done", f"Moved {moved} image file(s).")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        threading.Thread(target=task, daemon=True).start()

    def _undo_move(self):
        if not self._last_move_pairs:
            messagebox.showinfo("Nothing to undo", "No previous move batch found.")
            return

        def task():
            restored = 0
            try:
                for old, new in reversed(self._last_move_pairs):
                    if not os.path.exists(new):
                        continue
                    os.makedirs(os.path.dirname(old), exist_ok=True)
                    target = old
                    base, ext = os.path.splitext(target); i = 1
                    while os.path.exists(target):
                        target = f"{base}_restored_{i}{ext}"; i += 1
                    shutil.move(new, target)
                    restored += 1
                    self.move_log.insert("end", f"Restored: {new} -> {target}\n"); self.move_log.see("end")
                self._last_move_pairs = []
                self.undo_btn.state(["disabled"])
                messagebox.showinfo("Undo complete", f"Restored {restored} file(s).")
            except Exception as e:
                messagebox.showerror("Undo failed", str(e))

        threading.Thread(target=task, daemon=True).start()

    # ---------- Extract Emails ----------
    def _build_emails_tab(self):
        f = self.tab_emails; f.columnconfigure(1, weight=1)
        ttk.Label(f, text="Extract email addresses from a text file", style="Muted.TLabel")\
            .grid(row=0, column=0, columnspan=3, sticky="w", pady=(0,10))

        ttk.Label(f, text="Input .txt").grid(row=1, column=0, sticky="w")
        self.in_txt_var = tk.StringVar()
        ttk.Entry(f, textvariable=self.in_txt_var, style="Input.TEntry").grid(row=1, column=1, sticky="ew", padx=8)
        ttk.Button(f, text="Browse", command=lambda: self._pick_file(self.in_txt_var, [("Text","*.txt")]))\
            .grid(row=1, column=2)

        ttk.Label(f, text="Output .txt").grid(row=2, column=0, sticky="w", pady=(8,0))
        self.out_txt_var = tk.StringVar()
        ttk.Entry(f, textvariable=self.out_txt_var, style="Input.TEntry").grid(row=2, column=1, sticky="ew", padx=8, pady=(8,0))
        ttk.Button(f, text="Save As", command=lambda: self._save_file(self.out_txt_var, ".txt"))\
            .grid(row=2, column=2, pady=(8,0))

        self.email_log = tk.Text(f, height=16, bg="#0b1220", fg="#e2e8f0", insertbackground="#e2e8f0")
        self.email_log.grid(row=3, column=0, columnspan=3, sticky="nsew", pady=10); f.rowconfigure(3, weight=1)

        ttk.Button(f, text="Extract", style="Accent.TButton", command=self._run_extract)\
            .grid(row=4, column=0, columnspan=3, sticky="ew")

    def _pick_file(self, var, types):
        p = filedialog.askopenfilename(filetypes=types)
        if p: var.set(p)

    def _save_file(self, var, ext):
        p = filedialog.asksaveasfilename(defaultextension=ext)
        if p: var.set(p)

    def _run_extract(self):
        src, dst = self.in_txt_var.get().strip(), self.out_txt_var.get().strip()
        if not src or not dst:
            messagebox.showwarning("Missing", "Choose input and output .txt files."); return

        def task():
            try:
                with open(src, "r", encoding="utf-8", errors="ignore") as f:
                    data = f.read()
                emails = sorted(set(EMAIL_RE.findall(data)))
                with open(dst, "w", encoding="utf-8") as f:
                    for e in emails: f.write(e + "\n")
                self.email_log.delete("1.0", "end")
                self.email_log.insert("end", f"Found {len(emails)} email(s):\n\n" + "\n".join(emails))
                messagebox.showinfo("Done", f"Saved {len(emails)} emails to:\n{dst}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        threading.Thread(target=task, daemon=True).start()

    # ---------- Scrape Title (URL + Title) ----------
    def _build_title_tab(self):
        f = self.tab_title; f.columnconfigure(1, weight=1)
        ttk.Label(f, text="Fetch the <title> of a webpage and save it (URL + Title)", style="Muted.TLabel")\
            .grid(row=0, column=0, columnspan=3, sticky="w", pady=(0,10))

        ttk.Label(f, text="URL (https://...)").grid(row=1, column=0, sticky="w")
        self.url_var = tk.StringVar(value="https://www.python.org/")
        ttk.Entry(f, textvariable=self.url_var, style="Input.TEntry").grid(row=1, column=1, sticky="ew", padx=8)

        ttk.Label(f, text="Output .txt").grid(row=2, column=0, sticky="w", pady=(8,0))
        self.title_out_var = tk.StringVar()
        ttk.Entry(f, textvariable=self.title_out_var, style="Input.TEntry").grid(row=2, column=1, sticky="ew", padx=8, pady=(8,0))
        ttk.Button(f, text="Save As", command=lambda: self._save_file(self.title_out_var, ".txt")).grid(row=2, column=2, pady=(8,0))

        self.title_log = tk.Text(f, height=12, bg="#0b1220", fg="#e2e8f0", insertbackground="#e2e8f0")
        self.title_log.grid(row=3, column=0, columnspan=3, sticky="nsew", pady=10); f.rowconfigure(3, weight=1)

        ttk.Button(f, text="Scrape Title", style="Accent.TButton", command=self._run_title)\
            .grid(row=4, column=0, columnspan=3, sticky="ew")

    def _run_title(self):
        url = self.url_var.get().strip()
        dst = self.title_out_var.get().strip()
        if not url or not dst:
            messagebox.showwarning("Missing", "Enter URL and choose output file."); return

        def task():
            try:
                headers = {"User-Agent":"Mozilla/5.0"}
                r = requests.get(url, headers=headers, timeout=10); r.raise_for_status()
                soup = BeautifulSoup(r.text, "html.parser")
                title = (soup.title.string or "").strip() if soup.title else ""
                if not title: raise ValueError("No <title> found.")
                with open(dst, "w", encoding="utf-8") as f:
                    f.write(f"URL: {url}\nTitle: {title}\n")
                self.title_log.delete("1.0", "end")
                self.title_log.insert("end", f"URL: {url}\nTitle: {title}\nSaved to: {dst}")
                messagebox.showinfo("Done", "Title saved.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        threading.Thread(target=task, daemon=True).start()

def main():
    root = tk.Tk(); root.rowconfigure(0, weight=1); root.columnconfigure(0, weight=1)
    App(root); root.mainloop()

if __name__ == "__main__":
    main()
