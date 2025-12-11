# pip install -U customtkinter google-generativeai python-dotenv
import os
import threading
import time
import customtkinter as ctk
from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai
from google.api_core.exceptions import NotFound

APP_TITLE = "Nebula Chat • Gemini"
DEFAULT_MODEL = "gemini-2.5-flash"
FALLBACK_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    # legacy, in case your key supports them:
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]

# ---------------------------
# Bubble widget
# ---------------------------
class Bubble(ctk.CTkFrame):
    def __init__(self, master, text: str, role: str = "assistant"):
        bg_user = ("#5B7CFF", "#5B7CFF")
        bg_bot  = ("#1f2937", "#111827")
        txt_user = "#ffffff"
        txt_bot  = "#e5e7eb"

        is_user = (role == "user")
        super().__init__(master,
                         fg_color=bg_user if is_user else bg_bot,
                         corner_radius=18)
        self.grid_columnconfigure(0, weight=1)

        self.label = ctk.CTkLabel(
            self,
            text=text.strip() or "(no response)",
            font=ctk.CTkFont(size=14),
            text_color=txt_user if is_user else txt_bot,
            justify="left",
            wraplength=760
        )
        self.label.grid(row=0, column=0, sticky="w", padx=12, pady=10)

# ---------------------------
# Main App
# ---------------------------
class ChatApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("980x720")
        ctk.set_appearance_mode("dark")     # "dark" | "light" | "system"
        ctk.set_default_color_theme("dark-blue")

        # State
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.req_model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL).strip()
        self.active_model = None
        self.chat = None
        self.typing = False
        self.stop_typing_flag = threading.Event()

        # Layout
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_chat()
        self._build_composer()

        # Auto connect
        self.after(300, self.auto_connect)

    # ---------------- Header ----------------
    def _build_header(self):
        self.header = ctk.CTkFrame(self, height=58, corner_radius=0)
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_columnconfigure(0, weight=1)

        left = ctk.CTkFrame(self.header, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w", padx=14, pady=10)

        logo = ctk.CTkLabel(left, text="●", font=ctk.CTkFont(size=24, weight="bold"))
        title = ctk.CTkLabel(left, text=APP_TITLE,
                             font=ctk.CTkFont(size=18, weight="bold"))
        logo.grid(row=0, column=0, padx=(0, 8))
        title.grid(row=0, column=1)

        right = ctk.CTkFrame(self.header, fg_color="transparent")
        right.grid(row=0, column=1, sticky="e", padx=14, pady=10)

        self.model_label = ctk.CTkLabel(
            right, text=f"Model: {self.req_model}",
            font=ctk.CTkFont(size=13), text_color="#93c5fd"
        )
        self.theme_btn = ctk.CTkButton(
            right, text="Toggle Theme",
            width=120, command=self._toggle_theme
        )

        self.model_label.grid(row=0, column=0, padx=(0, 10))
        self.theme_btn.grid(row=0, column=1)

    def _toggle_theme(self):
        current = ctk.get_appearance_mode().lower()
        ctk.set_appearance_mode("light" if current == "dark" else "dark")

    # ---------------- Chat area ----------------
    def _build_chat(self):
        self.chat_area = ctk.CTkScrollableFrame(
            self, corner_radius=0, fg_color=("white", "#0b1220")
        )
        self.chat_area.grid(row=1, column=0, sticky="nsew")
        self.chat_area.grid_columnconfigure(0, weight=1)

        # Warm welcome
        self._system("Starting… Auto-connecting to Gemini…")

    def _add_bubble(self, text, role):
        # Right-align user, left-align assistant
        container = ctk.CTkFrame(self.chat_area, fg_color="transparent")
        container.grid_columnconfigure(0, weight=1)
        container.grid(sticky="ew", padx=10, pady=5)

        bubble = Bubble(container, text, role=role)
        if role == "user":
            bubble.grid(row=0, column=0, sticky="e", padx=(120, 0))
        else:
            bubble.grid(row=0, column=0, sticky="w", padx=(0, 120))

        # Auto scroll
        self.after(50, lambda: self.chat_area._parent_canvas.yview_moveto(1.0))

    def _bot(self, text):    self._add_bubble(text, "assistant")
    def _user(self, text):   self._add_bubble(text, "user")
    def _system(self, text): self._add_bubble(f"System: {text}", "assistant")

    # --------------- Composer ----------------
    def _build_composer(self):
        self.composer = ctk.CTkFrame(self, height=72, corner_radius=0)
        self.composer.grid(row=2, column=0, sticky="ew")
        self.composer.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkTextbox(self.composer, height=56)
        self.entry.grid(row=0, column=0, padx=12, pady=10, sticky="ew")
        self.entry.bind("<Return>", self._on_enter)
        self.entry.bind("<Shift-Return>", lambda e: None)  # allow newline with Shift+Enter

        self.send_btn = ctk.CTkButton(self.composer, text="Send", width=110, command=self.send)
        self.send_btn.grid(row=0, column=1, padx=(6, 12), pady=10)

    def _on_enter(self, event):
        # Enter to send, Shift+Enter for new line
        if event.state & 0x0001:  # Shift pressed
            return
        self.send()
        return "break"

    # --------------- Auto connect ----------------
    def auto_connect(self):
        if not self.api_key:
            self._system("❌ Missing GEMINI_API_KEY in .env")
            return

        genai.configure(api_key=self.api_key)

        # Try requested then fallbacks
        tried = []
        for m in [self.req_model] + [x for x in FALLBACK_MODELS if x != self.req_model]:
            try:
                model = genai.GenerativeModel(m)
                self.chat = model.start_chat(history=[])
                self.active_model = m
                self.model_label.configure(text=f"Model: {m}")
                self._system(f"Connected to {m}. You can start chatting now ✨")
                self.send_btn.configure(state="normal")
                return
            except NotFound:
                tried.append(f"{m} → 404 (not found/unsupported)")
            except Exception as e:
                tried.append(f"{m} → {type(e).__name__}: {e}")

        self._system("❌ Could not connect to any model.\n" + "\n".join(tried))

    # --------------- Send flow ----------------
    def send(self):
        if not self.chat:
            self._system("Still connecting…")
            return

        text = self.entry.get("1.0", "end").strip()
        if not text:
            return

        self.entry.delete("1.0", "end")
        self._user(text)
        self._start_typing()

        # background thread
        threading.Thread(target=self._call_model, args=(text,), daemon=True).start()

    def _call_model(self, user_text):
        try:
            resp = self.chat.send_message(user_text)
            reply = getattr(resp, "text", "") or "(no response)"
        except Exception as e:
            reply = f"⚠️ Error: {e}"

        # back to UI
        self.after(0, lambda: (self._stop_typing(), self._bot(reply)))

    # --------------- Typing animation ---------------
    def _start_typing(self):
        self.typing = True
        self.stop_typing_flag.clear()
        t = threading.Thread(target=self._typing_loop, daemon=True)
        t.start()

    def _stop_typing(self):
        self.typing = False
        self.stop_typing_flag.set()

    def _typing_loop(self):
        dots = ["●", "●●", "●●●"]
        idx = 0
        holder = ctk.CTkLabel(self.chat_area, text="typing…", text_color="#9ca3af")
        row = len(self.chat_area.grid_slaves())
        holder.grid(row=row, column=0, sticky="w", padx=18, pady=(0, 6))

        while not self.stop_typing_flag.is_set():
            holder.configure(text=f"Assistant is typing {dots[idx % 3]}")
            idx += 1
            time.sleep(0.4)

        holder.destroy()


if __name__ == "__main__":
    app = ChatApp()
    app.mainloop()
