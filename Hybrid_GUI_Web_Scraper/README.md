# Hybrid Web Scraper (GUI)
### Requests + BeautifulSoup + Scrapy + Tkinter GUI

A powerful and user-friendly web scraping tool combining:
- Requests
- BeautifulSoup
- Scrapy
- Tkinter GUI

## Features
- GUI interface with URL input, max pages, progress bar, logs, timer, stop button
- Seed link extraction via Requests + BeautifulSoup
- Fast crawling via Scrapy
- Auto-open output files (site.csv, site.json)
- App closes automatically after completion

## Installation
```bash
pip install scrapy requests beautifulsoup4
```

## Usage
1. Run the script:
```bash
python gui_hybrid_scraper.py
```
2. Enter a website URL
3. Enter max pages
4. Click Start Scraping
5. On completion, click OK → both files open → app closes

## Output
- site.csv
- site.json

## Notes
- Check robots.txt
- JS-heavy sites may require Selenium/Playwright
