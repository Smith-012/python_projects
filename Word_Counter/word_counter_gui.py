import string
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

def count_words(text: str):
    text = text.lower().translate(str.maketrans("", "", string.punctuation))
    counts = {}
    for w in text.split():
        counts[w] = counts.get(w, 0) + 1
    return dict(sorted(counts.items()))

def open_file():
    path = filedialog.askopenfilename(
        title="Select a text file",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if not path:
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except Exception as e:
        messagebox.showerror("Read error", f"Couldn't read file:\n{e}")
        return

    results = count_words(text)
    output.delete("1.0", "end")
    if not results:
        output.insert("end", "(No words found)")
        return
    for w, n in results.items():
        output.insert("end", f"{w}: {n}\n")

root = tk.Tk()
root.title("Word Counter (Alphabetical)")

frm = ttk.Frame(root, padding=12)
frm.pack(fill="both", expand=True)

ttk.Label(frm, text="Choose a .txt file to analyze").pack(anchor="w")
ttk.Button(frm, text="Open File…", command=open_file).pack(anchor="w", pady=(6, 10))

output = tk.Text(frm, height=20, width=60, wrap="word")
output.pack(fill="both", expand=True)
ttk.Scrollbar(frm, command=output.yview).pack(side="right", fill="y")
output.configure(yscrollcommand=lambda *args: frm.children[list(frm.children)[-1]].set(*args))

root.geometry("600x520")
root.mainloop()
