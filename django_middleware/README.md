<h1 align="center">✨ Django Middleware – Request Logging & Status Graph ✨</h1>

<p align="center">
  A clean Django project that logs every request using custom middleware<br>
  and displays the results using a beautiful <b>Chart.js</b> bar graph.
</p>

---

## 🚀 Features

- 📄 Logs each HTTP request (path, method, status code)
- 💾 Saves logs into SQLite automatically
- 📊 Visualizes status codes using Chart.js
- 🧱 Clean Django middleware example
- 🎯 Great for learning logging, middleware, and dashboards

---

## 📂 Project Structure

```
django_middleware/
│
├── myproject/
│   ├── manage.py
│   ├── db.sqlite3
│   ├── myproject/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   │
│   ├── logsapp/
│   │   ├── models.py
│   │   ├── middleware.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── migrations/
│   │
│   └── templates/
│       └── logs_graph.html
```

---

## 🔧 Installation & Setup

### 1️⃣ Create virtual environment
```sh
python -m venv venv
```

### 2️⃣ Activate environment  
Windows:
```sh
venv\Scripts\activate
```

### 3️⃣ Install dependencies
```sh
pip install django
```

### 4️⃣ Run migrations
```sh
python manage.py makemigrations
python manage.py migrate
```

### 5️⃣ Start local server
```sh
python manage.py runserver
```

---

## 🌐 Open the Graph

Visit:

```
http://127.0.0.1:8000/logs-graph/
```

You’ll see a **bar graph** showing:

- 200 OK  
- 404 Not Found  
- 302 Redirect  
- …and more  

based on actual logged requests.

---

## 🧠 How It Works

### 🔹 Middleware  
Located at `logsapp/middleware.py`  
Logs every request and stores:

- Path  
- Method  
- Status Code  
- Timestamp  

### 🔹 Model  
`logsapp/models.py`  
Defines `RequestLog` table.

### 🔹 View  
`logsapp/views.py`  
Groups logs by status code.

### 🔹 Template  
`templates/logs_graph.html`  
Uses Chart.js to draw the graph.

---

## 📊 Example Graph

```
Status Code Count:
200 ██████████████
404 ████
302 ██
```

(Displayed visually in the browser)

---

## 🛠 Future Enhancements

- 📅 Date-range filtering
- 📈 Line chart of requests over time
- 📁 Export logs to CSV
- 🌐 Log IP address + user agent
- 🖥 Full dashboard UI

---

## 👨‍💻 Author

**Smith-012**  
GitHub: https://github.com/Smith-012

---

## 📄 License

This project follows the root repository license.
