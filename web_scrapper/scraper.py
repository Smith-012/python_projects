#!/usr/bin/env python3
"""
Universal Real‑Time Web Scraper — Automation Project (Intermediate+)
===================================================================

What this does
--------------
- Works on **any website** (static or JavaScript‑rendered)
- Two fetch modes: **HTTP (aiohttp)** and **Rendered (Playwright/Chromium)**
- CLI with `argparse`
- Respectful scraping: robots.txt, per‑host concurrency, rate limiting, retries
- Extract via **CSS selectors** (with `::attr(name)` for attributes)
- Output **CSV** or **JSON Lines**
- Optional **sitemap.xml** discovery
- **Real‑time mode**: `--watch N` to re‑scrape periodically and timestamp outputs
- Simple **proxy**, headers & user‑agent override

Install deps
------------
```
pip install aiohttp aiodns beautifulsoup4 lxml tqdm playwright
python -m playwright install chromium
```

Examples
--------
1) Static fetch (fast) — title & meta description to CSV:
```
python scraper.py --urls https://example.com \
  --select title=title \
  --select description='meta[name="description"]::attr(content)' \
  --out out.csv
```

2) Rendered fetch (JS sites):
```
python scraper.py --urls https://www.flipkart.com/ \
  --render --wait-for 'body' --render-timeout 20 \
  --select title=title --out out.jsonl --format jsonl
```

3) Real‑time (every 60s, new file each run with timestamp suffix):
```
python scraper.py --urls https://news.ycombinator.com \
  --select headlines='a.storylink' \
  --watch 60 --out hn.csv
```

4) From sitemap + proxy + custom UA:
```
python scraper.py --sitemap https://example.com/sitemap.xml \
  --user-agent "MyResearchBot/1.0 (+contact@example.com)" \
  --proxy http://user:pass@host:port \
  --select h1=h1 --out pages.csv
```

Ethics & legality
-----------------
Always check each site’s **robots.txt** and **Terms of Service**. Use reasonable rates and identify yourself with a contactable UA string.
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import json
import logging
import random
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
from urllib.parse import urlparse, urljoin
import xml.etree.ElementTree as ET
import urllib.robotparser as robotparser

import aiohttp
from bs4 import BeautifulSoup
from tqdm import tqdm

# Playwright is optional (only used when --render is set)
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except Exception:
    PLAYWRIGHT_AVAILABLE = False

# -----------------------------
# Utilities
# -----------------------------

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36",
]

ATTRIBUTE_PATTERN = re.compile(r"::attr\(([^)]+)\)$")

def _normalize_url(url: str) -> str:
    p = urlparse(url)
    if not p.scheme:
        return f"http://{url}"
    return url

# -----------------------------
# Config
# -----------------------------

@dataclass
class ScraperConfig:
    urls: List[str] = field(default_factory=list)
    sitemap_url: Optional[str] = None
    selectors: Dict[str, str] = field(default_factory=dict)

    out_path: Path = Path("out.csv")
    output_format: str = "csv"  # or jsonl

    timeout: float = 25.0
    max_retries: int = 3
    backoff_base: float = 0.5
    backoff_max: float = 8.0
    concurrency: int = 10
    per_host: int = 4
    ratelimit_delay: float = 0.0

    verify_robots: bool = True
    user_agent: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    allow_status: Tuple[int, ...] = (200,)
    proxy: Optional[str] = None  # http://user:pass@host:port

    # Rendered mode
    render: bool = False
    render_timeout: float = 20.0
    wait_for: Optional[str] = None  # CSS selector to wait for

    # Real-time mode
    watch_seconds: int = 0  # 0 disables
    add_timestamp: bool = True

# -----------------------------
# Robots cache
# -----------------------------

class RobotsCache:
    def __init__(self, session: aiohttp.ClientSession, user_agent: str):
        self.session = session
        self.user_agent = user_agent
        self._cache: Dict[str, robotparser.RobotFileParser] = {}
        self._lock = asyncio.Lock()

    async def allowed(self, url: str) -> bool:
        host = urlparse(url).netloc
        async with self._lock:
            rp = self._cache.get(host)
            if rp is None:
                rp = robotparser.RobotFileParser()
                robots_url = f"{urlparse(url).scheme}://{host}/robots.txt"
                try:
                    async with self.session.get(robots_url, timeout=10, proxy=None) as resp:
                        if resp.status == 200:
                            txt = await resp.text()
                            rp.parse(txt.splitlines())
                        else:
                            rp.parse([])
                except Exception:
                    rp.parse([])
                self._cache[host] = rp
        return rp.can_fetch(self.user_agent, url)

# -----------------------------
# Downloader
# -----------------------------

class Downloader:
    def __init__(self, cfg: ScraperConfig):
        self.cfg = cfg
        self.semaphore = asyncio.Semaphore(cfg.concurrency)
        self.per_host_limits: Dict[str, asyncio.Semaphore] = {}
        self.per_host_limit = cfg.per_host
        self.session: Optional[aiohttp.ClientSession] = None
        self.robots: Optional[RobotsCache] = None
        # Playwright
        self._pw = None
        self._browser = None
        self._context = None

    async def __aenter__(self):
        headers = {
            "User-Agent": self.cfg.user_agent or random.choice(USER_AGENTS),
            **self.cfg.headers,
        }
        timeout = aiohttp.ClientTimeout(total=self.cfg.timeout)
        self.session = aiohttp.ClientSession(headers=headers, timeout=timeout)
        if self.cfg.verify_robots:
            self.robots = RobotsCache(self.session, headers["User-Agent"])

        if self.cfg.render:
            if not PLAYWRIGHT_AVAILABLE:
                raise RuntimeError("Playwright not installed. Run: pip install playwright && playwright install chromium")
            self._pw = await async_playwright().start()
            launch_args = {"headless": True}
            if self.cfg.proxy:
                launch_args["proxy"] = {"server": self.cfg.proxy}
            self._browser = await self._pw.chromium.launch(**launch_args)
            self._context = await self._browser.new_context(user_agent=headers["User-Agent"])
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._pw:
            await self._pw.stop()
        if self.session:
            await self.session.close()

    def _host_sem(self, url: str) -> asyncio.Semaphore:
        host = urlparse(url).netloc
        if host not in self.per_host_limits:
            self.per_host_limits[host] = asyncio.Semaphore(self.per_host_limit)
        return self.per_host_limits[host]

    async def fetch(self, url: str) -> Tuple[Optional[str], Optional[int], Optional[str]]:
        if self.cfg.render:
            return await self._fetch_rendered(url)
        return await self._fetch_http(url)

    async def _fetch_http(self, url: str) -> Tuple[Optional[str], Optional[int], Optional[str]]:
        assert self.session is not None
        if self.cfg.verify_robots and self.robots and not await self.robots.allowed(url):
            logging.info("Blocked by robots.txt: %s", url)
            return None, None, "robots"

        async with self.semaphore, self._host_sem(url):
            attempt = 0
            while True:
                attempt += 1
                if self.cfg.ratelimit_delay:
                    await asyncio.sleep(self.cfg.ratelimit_delay)
                try:
                    async with self.session.get(url, allow_redirects=True, proxy=self.cfg.proxy) as resp:
                        status = resp.status
                        if status in self.cfg.allow_status:
                            text = await resp.text(errors="ignore")
                            return text, status, None
                        err = f"bad_status:{status}"
                except Exception as e:
                    err = f"exception:{e!r}"
                if attempt > self.cfg.max_retries:
                    return None, None, err
                await self._sleep_backoff(attempt)

    async def _fetch_rendered(self, url: str) -> Tuple[Optional[str], Optional[int], Optional[str]]:
        assert self._context is not None
        # robots check still uses HTTP session (no proxy)
        if self.cfg.verify_robots and self.robots and not await self.robots.allowed(url):
            logging.info("Blocked by robots.txt: %s", url)
            return None, None, "robots"

        async with self.semaphore, self._host_sem(url):
            attempt = 0
            while True:
                attempt += 1
                try:
                    page = await self._context.new_page()
                    await page.route("**/*", lambda r: r.continue_())
                    await page.goto(url, wait_until="domcontentloaded", timeout=int(self.cfg.render_timeout * 1000))
                    if self.cfg.wait_for:
                        try:
                            await page.wait_for_selector(self.cfg.wait_for, timeout=int(self.cfg.render_timeout * 1000))
                        except Exception:
                            pass
                    html = await page.content()
                    # status code is not exposed directly after redirects; mark as 200 if loaded
                    await page.close()
                    return html, 200, None
                except Exception as e:
                    err = f"render_exception:{e!r}"
                if attempt > self.cfg.max_retries:
                    return None, None, err
                await self._sleep_backoff(attempt)

    async def _sleep_backoff(self, attempt: int):
        base = min(self.cfg.backoff_max, self.cfg.backoff_base * (2 ** (attempt - 1)))
        await asyncio.sleep(random.uniform(0, base))

# -----------------------------
# Extraction
# -----------------------------

class Extractor:
    def __init__(self, selectors: Dict[str, str]):
        self.selectors = selectors

    def extract(self, url: str, html: str, add_ts: bool) -> Dict[str, str]:
        soup = BeautifulSoup(html, "lxml")
        result: Dict[str, str] = {"url": url}
        if add_ts:
            result["timestamp"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        for name, selector in self.selectors.items():
            attr = None
            m = ATTRIBUTE_PATTERN.search(selector)
            sel = selector
            if m:
                attr = m.group(1)
                sel = ATTRIBUTE_PATTERN.sub("", selector)
            try:
                els = soup.select(sel)
            except Exception:
                els = []
            values: List[str] = []
            for el in els:
                if attr:
                    values.append(el.get(attr, ""))
                else:
                    values.append(el.get_text(strip=True))
            result[name] = "|".join(v for v in values if v)
        return result

# -----------------------------
# Output
# -----------------------------

def write_jsonl(path: Path, rows: Iterable[Dict[str, str]]):
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

def write_csv(path: Path, rows: Iterable[Dict[str, str]]):
    rows = list(rows)
    if not rows:
        path.write_text("")
        return
    fieldnames = sorted({k for row in rows for k in row.keys()})
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

# -----------------------------
# Sitemap helpers
# -----------------------------

def parse_sitemap(content: str, base_url: str) -> List[str]:
    urls: List[str] = []
    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        return urls
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    for loc in root.findall(".//sm:url/sm:loc", ns):
        if loc.text:
            urls.append(loc.text.strip())
    for sm_loc in root.findall(".//sm:sitemap/sm:loc", ns):
        if sm_loc.text:
            urls.append(sm_loc.text.strip())
    return [urljoin(base_url, u) for u in urls]

async def gather_from_sitemap(downloader: Downloader, sitemap_url: str, max_urls: int = 2000) -> List[str]:
    content, status, err = await downloader.fetch(sitemap_url)
    if not content:
        logging.warning("Failed to fetch sitemap %s (%s)", sitemap_url, err)
        return []
    urls = parse_sitemap(content, sitemap_url)
    leafs = [u for u in urls if u.endswith(".xml")]
    pages: List[str] = []
    if leafs:
        for leaf in leafs:
            c2, _, _ = await downloader.fetch(leaf)
            if c2:
                pages.extend(parse_sitemap(c2, leaf))
    else:
        pages = urls
    seen = set()
    final: List[str] = []
    for u in pages:
        u = _normalize_url(u)
        if u not in seen:
            seen.add(u)
            final.append(u)
            if len(final) >= max_urls:
                break
    return final

# -----------------------------
# Core run(s)
# -----------------------------

async def scrape_once(cfg: ScraperConfig) -> List[Dict[str, str]]:
    out_rows: List[Dict[str, str]] = []
    async with Downloader(cfg) as dl:
        urls = list(dict.fromkeys(_normalize_url(u) for u in cfg.urls))
        if cfg.sitemap_url:
            sitemap_urls = await gather_from_sitemap(dl, cfg.sitemap_url)
            urls.extend(u for u in sitemap_urls if u not in urls)

        extractor = Extractor(cfg.selectors)
        pbar = tqdm(total=len(urls), desc="scraping", unit="url")

        async def handle(url: str):
            try:
                html, status, err = await dl.fetch(url)
                if html:
                    data = extractor.extract(url, html, cfg.add_timestamp)
                    out_rows.append(data)
                else:
                    row = {"url": url, "error": err or f"status:{status}"}
                    if cfg.add_timestamp:
                        row["timestamp"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"
                    out_rows.append(row)
            finally:
                pbar.update(1)

        await asyncio.gather(*(handle(u) for u in urls))
        pbar.close()
    return out_rows

async def run(cfg: ScraperConfig):
    if cfg.watch_seconds > 0:
        i = 0
        while True:
            i += 1
            ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            out_path = cfg.out_path
            # create timestamped filename: name_YYYYmmdd_HHMMSS.ext
            out_path_ts = out_path.with_name(f"{out_path.stem}_{ts}{out_path.suffix}")
            rows = await scrape_once(cfg)
            out_path_ts.parent.mkdir(parents=True, exist_ok=True)
            if cfg.output_format == "jsonl" or out_path_ts.suffix.lower() == ".jsonl":
                write_jsonl(out_path_ts, rows)
            else:
                write_csv(out_path_ts, rows)
            logging.info("[%d] Wrote %s with %d rows", i, out_path_ts, len(rows))
            await asyncio.sleep(cfg.watch_seconds)
    else:
        rows = await scrape_once(cfg)
        cfg.out_path.parent.mkdir(parents=True, exist_ok=True)
        if cfg.output_format == "jsonl" or cfg.out_path.suffix.lower() == ".jsonl":
            write_jsonl(cfg.out_path, rows)
        else:
            write_csv(cfg.out_path, rows)
        logging.info("Wrote %s with %d rows", cfg.out_path, len(rows))

# -----------------------------
# CLI
# -----------------------------

def parse_kv_pairs(pairs: List[str]) -> Dict[str, str]:
    out = {}
    for p in pairs:
        if "=" not in p:
            raise argparse.ArgumentTypeError(f"Invalid selector mapping '{p}', expected name=CSS_SELECTOR")
        name, sel = p.split("=", 1)
        name = name.strip()
        sel = sel.strip()
        if not name or not sel:
            raise argparse.ArgumentTypeError(f"Invalid selector mapping '{p}'")
        out[name] = sel
    return out


def load_urls_file(path: Path) -> List[str]:
    if not path.exists():
        raise FileNotFoundError(path)
    urls: List[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        urls.append(line)
    return urls


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Universal real-time web scraper")

    gsrc = p.add_argument_group("Sources")
    gsrc.add_argument("--urls", nargs="*", default=[], help="URLs to scrape")
    gsrc.add_argument("--urls-file", type=Path, help="File with URLs (one per line)")
    gsrc.add_argument("--sitemap", dest="sitemap_url", help="Start from sitemap.xml URL")

    gsel = p.add_argument_group("Extraction")
    gsel.add_argument("--select", action="append", default=[], help="name=CSS_SELECTOR (use ::attr(x) for attributes)")

    gout = p.add_argument_group("Output")
    gout.add_argument("--out", dest="out_path", type=Path, default=Path("out.csv"), help="Output path (.csv or .jsonl)")
    gout.add_argument("--format", dest="output_format", choices=["csv", "jsonl"], default="csv", help="Output format (default: infer from extension)")

    gnet = p.add_argument_group("Networking & Politeness")
    gnet.add_argument("--timeout", type=float, default=25.0, help="Total request timeout")
    gnet.add_argument("--retries", dest="max_retries", type=int, default=3, help="Max retries per URL")
    gnet.add_argument("--concurrency", type=int, default=10, help="Global concurrent requests")
    gnet.add_argument("--per-host", dest="per_host", type=int, default=4, help="Concurrent requests per host")
    gnet.add_argument("--delay", dest="ratelimit_delay", type=float, default=0.0, help="Delay between requests (seconds)")
    gnet.add_argument("--no-robots", dest="verify_robots", action="store_false", help="Ignore robots.txt (not recommended)")
    gnet.add_argument("--user-agent", dest="user_agent", help="Override User-Agent")
    gnet.add_argument("--header", action="append", default=[], help="Extra header as Name: Value (can repeat)")
    gnet.add_argument("--proxy", dest="proxy", help="Proxy URL (e.g., http://user:pass@host:port)")

    grender = p.add_argument_group("Rendered mode (Playwright)")
    grender.add_argument("--render", action="store_true", help="Enable JS-rendered fetching (Chromium)")
    grender.add_argument("--render-timeout", type=float, default=20.0, help="Seconds to wait for page load/selector")
    grender.add_argument("--wait-for", dest="wait_for", help="CSS selector to wait for before scraping")

    grealtime = p.add_argument_group("Real-time scraping")
    grealtime.add_argument("--watch", dest="watch_seconds", type=int, default=0, help="Repeat scraping every N seconds; writes timestamped files")
    grealtime.add_argument("--no-timestamp", dest="add_timestamp", action="store_false", help="Do not add timestamp column")

    return p


def parse_headers(header_list: List[str]) -> Dict[str, str]:
    headers = {}
    for h in header_list:
        if ":" not in h:
            raise argparse.ArgumentTypeError(f"Invalid header '{h}', expected 'Name: Value'")
        name, value = h.split(":", 1)
        headers[name.strip()] = value.strip()
    return headers


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    selectors = parse_kv_pairs(args.select)
    if not selectors:
        parser.error("You must provide at least one --select name=CSS_SELECTOR")

    urls = [u for u in args.urls]
    if args.urls_file:
        urls.extend(load_urls_file(args.urls_file))

    if not urls and not args.sitemap_url:
        parser.error("Provide --urls / --urls-file or --sitemap")

    output_format = args.output_format
    if args.out_path.suffix.lower() == ".jsonl":
        output_format = "jsonl"

    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")

    cfg = ScraperConfig(
        urls=urls,
        sitemap_url=args.sitemap_url,
        selectors=selectors,
        out_path=args.out_path,
        output_format=output_format,
        timeout=args.timeout,
        max_retries=args.max_retries,
        concurrency=args.concurrency,
        per_host=args.per_host,
        ratelimit_delay=args.ratelimit_delay,
        verify_robots=args.verify_robots,
        user_agent=args.user_agent,
        headers=parse_headers(args.header),
        proxy=args.proxy,
        render=args.render,
        render_timeout=args.render_timeout,
        wait_for=args.wait_for,
        watch_seconds=args.watch_seconds,
        add_timestamp=args.add_timestamp,
    )

    try:
        asyncio.run(run(cfg))
    except KeyboardInterrupt:
        print("Interrupted.")
        return 130
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
