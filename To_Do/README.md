# 📝 To-Do List Application (Python + Tkinter)

A simple and elegant **To-Do List GUI application** built using **Python (Tkinter)**.  
It allows users to **add, edit, delete, search, filter, and manage tasks**, with optional **calendar date picking** and **automatic JSON storage**.

## 🚀 Features

### ✔ Task Management
- Add tasks  
- Edit tasks  
- Delete tasks  
- Toggle Completed / Incomplete  
- Auto-save to `tasks.json`

### 🔍 Search & Filters
- Search tasks  
- Filter: All, Active, Completed  

### 📅 Due Date & Notes
- Optional due date (YYYY-MM-DD)  
- Date validation  
- Calendar picker (via `tkcalendar`)  
- Notes support  

### 🖥 GUI Features
- Clean UI  
- Keyboard shortcuts (Del, Enter, Ctrl+E)  
- Sorted task table  

## 💾 Persistence
Stored automatically in `tasks.json`.

## 📦 Requirements
Python 3.8+

Optional:
```
pip install tkcalendar
```

## ▶️ Run
```
python todo_gui.py
```

## 📁 Structure
todo_gui.py  
tasks.json  
README.md  
