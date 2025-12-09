# Python Projects (Web + GUI)

<p align="center">
  <img height="150em" src="https://streak-stats.vercel.app?user=Smith-012&theme=tokyonight" />
</p>

A collection of Python projects built using **Flask (web apps)** and GUI frameworks.

## Project Structure

```
python_projects/
├── web_apps/
│   └── <flask-project>/
│       ├── app.py
│       ├── static/
│       ├── templates/
│       └── requirements.txt
└── gui_apps/
    └── <gui-project>/
        ├── main.py
        └── requirements.txt
```

## Setup

### Clone
```bash
git clone https://github.com/Smith-012/python_projects.git
cd python_projects
```

### Create Virtual Environment
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

## Running Web (Flask) Projects
```bash
cd web_apps/<project>
pip install -r requirements.txt
flask run
```

## Running GUI Projects
```bash
cd gui_apps/<project>
pip install -r requirements.txt
python main.py
```

## License

This project is licensed under the **GNU GPL-3.0 License**.
See the [LICENSE](LICENSE) file for details.

## Author
**Smith-012**
