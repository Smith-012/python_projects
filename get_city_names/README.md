# India Cities Fetcher

A Python project that fetches and saves a list of cities from India using the Countries Now API.

## Features

- Fetches cities from the Countries Now Space API
- Saves cities to a CSV file
- Clean, sorted list with duplicates removed

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd Task-1
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell
```

3. Install dependencies:
```bash
pip install requests
```

## Usage

Run the script:
```bash
python run.py
```

This will fetch all cities from India and save them to `india_cities.csv`.

## Project Structure

- `fetch_india_cities.py` - Main module with API functions
- `run.py` - Entry point script
- `india_cities.csv` - Output file (generated)

## Requirements

- Python 3.10+
- requests library
