# Universal Real-Time Web Scraper

A powerful **universal web scraper** capable of extracting real-time data from **ANY website**, whether static HTML or JavaScript-rendered. It supports automation, repeated scraping, concurrent requests, sitemap crawling, and custom data extraction using CSS selectors.

This project is ideal for:

* **Automation & scripting practice**
* **Learning web scraping fundamentals**
* **Building real-time data collectors**
* **Extracting information from any website** using CSS selectors
* **Handling JavaScript-heavy websites** using Playwright
* **Creating CSV / JSON datasets** from web data

---

## 🚀 Features

### 1. Static & JavaScript-Rendered Scraping

* **Static Mode (aiohttp)** → fast, lightweight
* **Render Mode (Playwright)** → executes JavaScript and loads full DOM

### 2. Universal CSS Selector Extraction

Extract any data using:

```
--select field_name=CSS_SELECTOR
```

Supports attribute extraction:

```
a::attr(href)
img::attr(src)
```

### 3. Real-Time Scraping (Live Mode)

You can run the scraper **continuously**:

```
--watch 60
```

This re-scrapes every 60 seconds and saves new timestamped results.

### 4. Sitemap Crawling

Automatically fetch all URLs from a website’s sitemap:

```
--sitemap https://example.com/sitemap.xml
```

### 5. Proxy, Headers & User-Agent Support

```
--proxy http://user:pass@host:port
--header "Accept-Language: en-US"
--user-agent "MyBot/1.0"
```

### 6. Respectful Web Scraping

* robots.txt checking (can disable)
* retries with exponential backoff
* rate limiting
* per-host concurrency control

### 7. Output Formats

* CSV
* JSON Lines (`.jsonl`)

---

## 📦 Installation

Install dependencies:

```bash
pip install aiohttp aiodns beautifulsoup4 lxml tqdm playwright
```

Then install the browser engine:

```bash
python -m playwright install chromium
```

---

## 📝 Basic Usage

### Extract Title From Any Website

```bash
python scraper.py --urls https://example.com --select title=title --out data.csv
```

### Extract Headings, Images, and Links

```bash
python scraper.py --urls https://example.com \
  --select title=title \
  --select headings='h1, h2' \
  --select images='img::attr(src)' \
  --select links='a::attr(href)' \
  --out scraped.jsonl --format jsonl
```

---

## 🖥️ JavaScript-Rendered Scraping

For sites like Flipkart, Amazon, etc.

```bash
python scraper.py --urls https://www.flipkart.com/ \
  --render --wait-for 'body' \
  --select title=title \
  --out flipkart_data.jsonl --format jsonl
```

---

## ⏱️ Real-Time Scraping (Every 60 Seconds)

```bash
python scraper.py --urls https://news.ycombinator.com \
  --select headline='a.storylink' \
  --watch 60 --out hn.csv
```

Creates:

```
hn_20250101_120000.csv
hn_20250101_120100.csv
...
```

---

## 🌐 Using Sitemap Mode

```bash
python scraper.py --sitemap https://example.com/sitemap.xml \
  --select h1=h1 \
  --out site_pages.csv
```

---

## 🔧 Additional Options

### Rate limiting

```
--delay 1   # 1 second between requests
```

### Disable robots.txt (not recommended)

```
--no-robots
```

### Set concurrency

```
--concurrency 20 --per-host 5
```

---

## 📤 Output Examples

### CSV:

```
url, title, timestamp
https://example.com, Example Domain, 2025-12-08T12:00:00Z
```

### JSONL:

```
{"url": "https://example.com", "title": "Example Domain", "timestamp": "2025-12-08T12:00:00Z"}
```

---

## 📘 When Should You Use This Scraper?

This project is perfect when you want to:

* Extract data **without writing new code each time**
* Scrape **any website**, not a fixed one
* Collect data **on a schedule** (price monitoring, news tracking, analytics)
* Handle websites that require **JavaScript execution**
* Build datasets for ML/automation projects
* Learn advanced scraping techniques

---

## 🛑 Disclaimer

* Always respect **robots.txt** and website Terms of Service.
* Use responsible scraping rates.
* This tool is for **educational and personal research** purposes.

---
