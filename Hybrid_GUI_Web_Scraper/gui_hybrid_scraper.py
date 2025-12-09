# gui_hybrid_scraper.py
# Requires: pip install scrapy requests beautifulsoup4

import os
import re
import sys
import time
import platform
import subprocess
import threading
from queue import Queue, Empty
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup

import scrapy
from scrapy.crawler import CrawlerProcess

# ------------------ GUI (Tkinter) ------------------
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import scrolledtext


# ------------------ OS helpers ------------------

def open_file(filepath):
    """Auto-open file on Windows, macOS, Linux."""
    system = platform.system()
    try:
        if system == "Windows":
            os.startfile(filepath)
        elif system == "Darwin":  # macOS
            subprocess.call(["open", filepath])
        else:  # Linux
            subprocess.call(["xdg-open", filepath])
    except Exception as e:
        print(f"Could not open {filepath}: {e}")


# ------------------ Requests + BS4 helpers ------------------

def polite_get(url, ua):
    resp = requests.get(url, timeout=20, headers={"User-Agent": ua})
    resp.raise_for_status()
    return resp


def same_domain_links(base_url, html, limit=15):
    """Extract up to limit same-domain links using BeautifulSoup."""
    seeds = []
    soup = BeautifulSoup(html, "html.parser")
    base = urlparse(base_url).netloc.lower()

    for a in soup.find_all("a", href=True):
        href = a.get("href")
        abs_url = urljoin(base_url, href)
        if urlparse(abs_url).netloc.lower() == base:
            if abs_url.startswith(("mailto:", "javascript:")):
                continue
            if abs_url not in seeds:
                seeds.append(abs_url)
        if len(seeds) >= limit:
            break

    return seeds or [base_url]


# ------------------ Scrapy Spider ------------------

class GenericSpider(scrapy.Spider):
    """
    Starts from user-provided seeds, stays on the same domain,
    limits total pages, parses content with BeautifulSoup.
    Uses progress callback to update GUI.
    """
    name = "hybrid_scraper_gui"

    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (compatible; HybridScraperGUI/1.0)",
        "DOWNLOAD_DELAY": 0.5,
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 0.5,
        "AUTOTHROTTLE_MAX_DELAY": 2.5,
        "FEEDS": {
            "site.csv": {"format": "csv", "overwrite": True},
            "site.json": {"format": "json", "overwrite": True},
        },
        "LOG_LEVEL": "ERROR",
    }

    def __init__(self, start_urls, allowed_netloc, max_pages=50,
                 progress_cb=None, stop_event=None, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = start_urls
        self.allowed_netloc = allowed_netloc.lower()
        self.max_pages = int(max_pages)
        self.visited = set()
        self.count = 0
        self.progress_cb = progress_cb
        self.stop_event = stop_event

    def _emit(self, kind, **data):
        if self.progress_cb:
            self.progress_cb(kind=kind, **data)

    def parse(self, response):
        if self.stop_event and self.stop_event.is_set():
            self._emit("log", message=f"Stopped before: {response.url}")
            return

        if self.count >= self.max_pages:
            return

        self.count += 1
        self.visited.add(response.url)
        self._emit("log", message=f"Visited: {response.url}")
        self._emit("progress", pages=self.count)

        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.string.strip() if soup.title and soup.title.string else ""

        meta_desc = ""
        m = soup.find("meta", attrs={"name": "description"})
        if m and m.get("content"):
            meta_desc = m["content"].strip()

        def extract_tags(tag):
            return " | ".join([t.get_text(strip=True) for t in soup.find_all(tag)])

        h1 = extract_tags("h1")
        h2 = extract_tags("h2")
        h3 = extract_tags("h3")

        links = []
        for a in soup.find_all("a", href=True):
            abs_url = urljoin(response.url, a["href"])
            if urlparse(abs_url).netloc.lower() == self.allowed_netloc:
                if abs_url not in links:
                    links.append(abs_url)

        yield {
            "url": response.url,
            "title": title,
            "meta_description": meta_desc,
            "h1": h1,
            "h2": h2,
            "h3": h3,
            "same_domain_links": len(links),
        }

        for link in links:
            if self.stop_event.is_set():
                return
            if self.count < self.max_pages and link not in self.visited:
                self.visited.add(link)
                yield scrapy.Request(link, callback=self.parse)


# ------------------ GUI Application ------------------

class ScraperApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hybrid Web Scraper — Requests + BS4 + Scrapy")
        self.root.geometry("720x520")
        self.root.minsize(700, 500)

        # state
        self.process = None
        self.stop_event = threading.Event()
        self.msg_queue: Queue = Queue()
        self.total_pages = 50
        self.pages_done = 0
        self.start_time = None
        self.running_thread = None

        self._build_ui()
        self._poll_queue()

    # ---------- UI ----------

    def _build_ui(self):
        pad = 10

        top = ttk.Frame(self.root, padding=pad)
        top.pack(fill="x")

        ttk.Label(top, text="Website URL:").grid(row=0, column=0, sticky="w")
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(top, textvariable=self.url_var, width=60)
        self.url_entry.grid(row=0, column=1, sticky="we")
        top.grid_columnconfigure(1, weight=1)

        ttk.Label(top, text="Max pages:").grid(row=0, column=2, sticky="e", padx=8)
        self.pages_var = tk.StringVar(value="50")
        ttk.Entry(top, textvariable=self.pages_var, width=8).grid(row=0, column=3)

        ctl = ttk.Frame(self.root, padding=(pad, 0, pad, 0))
        ctl.pack(fill="x")

        self.start_btn = ttk.Button(ctl, text="Start Scraping", command=self.on_start)
        self.start_btn.pack(side="left")

        self.stop_btn = ttk.Button(ctl, text="Stop", command=self.on_stop, state="disabled")
        self.stop_btn.pack(side="left", padx=8)

        prog = ttk.Frame(self.root, padding=pad)
        prog.pack(fill="x")

        self.progress = ttk.Progressbar(prog, orient="horizontal", mode="determinate", maximum=100)
        self.progress.pack(fill="x")

        self.percent_label = ttk.Label(prog, text="0%")
        self.percent_label.pack(anchor="w")

        self.timer_label = ttk.Label(prog, text="Elapsed: 00:00")
        self.timer_label.pack(anchor="w")

        logf = ttk.LabelFrame(self.root, text="Logs", padding=pad)
        logf.pack(fill="both", expand=True, padx=pad, pady=(0, pad))

        self.log = scrolledtext.ScrolledText(logf, height=16, wrap="word", state="disabled")
        self.log.pack(fill="both", expand=True)

        ttk.Label(self.root, text="Output: site.csv, site.json").pack(anchor="w", padx=pad)

    def log_write(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def set_progress(self, pages):
        self.pages_done = pages
        pct = min(int(self.pages_done / max(self.total_pages, 1) * 100), 100)
        self.progress["value"] = pct
        self.percent_label.config(text=f"{pct}%")

    def reset_ui(self):
        self.stop_event.clear()
        self.pages_done = 0
        self.start_time = None

        self.set_progress(0)
        self.timer_label.config(text="Elapsed: 00:00")
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def update_timer(self):
        if not self.start_time:
            return

        elapsed = int(time.time() - self.start_time)
        mm, ss = divmod(elapsed, 60)
        self.timer_label.config(text=f"Elapsed: {mm:02d}:{ss:02d}")

        if self.running_thread and self.running_thread.is_alive():
            self.root.after(1000, self.update_timer)

    # ---------- Queue polling ----------

    def _poll_queue(self):
        try:
            while True:
                kind, data = self.msg_queue.get_nowait()

                if kind == "log":
                    self.log_write(data.get("message", ""))

                elif kind == "progress":
                    self.set_progress(data.get("pages", 0))

                elif kind == "done":
                    self.finish_success()

                elif kind == "error":
                    self.finish_error(data.get("message", "Unknown error"))

        except Empty:
            pass

        self.root.after(100, self._poll_queue)

    # ---------- Buttons ----------

    def on_start(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a website URL.")
            return

        if not re.match(r"^https?://", url):
            url = "https://" + url
            self.url_var.set(url)

        pages = self.pages_var.get().strip() or "50"
        if not pages.isdigit() or int(pages) <= 0:
            messagebox.showerror("Error", "Max pages must be a positive integer.")
            return

        self.total_pages = int(pages)

        self.reset_ui()
        self.log_write(f"Starting crawl: {url}  (max_pages={self.total_pages})")

        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")

        self.start_time = time.time()
        self.update_timer()

        self.running_thread = threading.Thread(
            target=self._worker_scrape, args=(url, self.total_pages), daemon=True
        )
        self.running_thread.start()

    def on_stop(self):
        self.stop_event.set()
        self.log_write("STOP REQUESTED by user…")
        self.stop_btn.config(state="disabled")
        if self.process:
            try:
                self.process.stop()
            except:
                pass

    # ---------- Background scraper thread ----------

    def progress_cb(self, **data):
        kind = data.pop("kind", "log")
        self.msg_queue.put((kind, data))

    def _worker_scrape(self, url, max_pages):
        try:
            ua = "Mozilla/5.0 (compatible; HybridScraperGUI/1.0)"
            self.msg_queue.put(("log", {"message": f"Fetching: {url}"}))

            resp = polite_get(url, ua)
            time.sleep(0.2)

            seeds = same_domain_links(url, resp.text, limit=15)
            netloc = urlparse(url).netloc

            self.msg_queue.put(("log", {"message": f"Seeds: {len(seeds)} (domain: {netloc})"}))

            # Run Scrapy
            self.process = CrawlerProcess()
            self.process.crawl(
                GenericSpider,
                start_urls=seeds,
                allowed_netloc=netloc,
                max_pages=max_pages,
                progress_cb=self.progress_cb,
                stop_event=self.stop_event,
            )
            self.process.start()

            self.msg_queue.put(("done", {}))

        except Exception as e:
            self.msg_queue.put(("error", {"message": str(e)}))

    # ---------- Finalization ----------

    def finish_success(self):
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

        if self.stop_event.is_set():
            self.log_write("Scraping stopped.")
            messagebox.showinfo("Stopped", "Scraping was stopped.")
            self.root.destroy()
            return

        self.log_write("Scraping complete. Files saved: site.csv, site.json")

        # Wait for user click
        messagebox.showinfo("Done", "Scraping complete!\nClick OK to open files and close app.")

        # Auto-open files
        open_file("site.csv")
        open_file("site.json")

        # Close the GUI
        self.root.destroy()

    def finish_error(self, msg):
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

        self.log_write(f"ERROR: {msg}")
        messagebox.showerror("Error", msg)
        self.root.destroy()


# ------------------ Main ------------------

def main():
    app = ScraperApp()
    app.root.mainloop()


if __name__ == "__main__":
    main()
