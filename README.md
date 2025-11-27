# 📝 Masterblog API

A simple blog application built with **Flask**, featuring a RESTful API, JSON storage and a frontend interface.  
This project demonstrates backend and frontend integration using HTTP requests and persistent data storage.

---

## 🚀 Features

### 🗄 Backend (Flask API)
- CRUD operations for blog posts
- Data stored in `storage.json` (persistent storage)
- Validation for required fields
- Strict date validation (`YYYY-MM-DD`)
- Search or sort posts by:
  - `title`
  - `content`
  - `author`
  - `date`
- Error handling (404, 400, 500)
- API documentation using **Swagger UI**

### 🎨 Frontend (Flask + HTML/JS)
- Single-page static UI (served by Flask)
- Allows users to:
  - Load posts
  - Add a post
  - Edit a post
  - Delete a post
- Communicates with backend using `fetch()`

---

## 📂 Project Structure

```plaintext
backend/
│── backend_app.py        # REST API server
│── storage.json          # Persisted blog post data
│── static/
│   └── masterblog.json   # Swagger documentation

frontend/
│── frontend_app.py       # Frontend Flask host
│── templates/
│   └── index.html        # UI
│── static/
    ├── main.js           # Frontend logic (fetch requests)
    └── styles.css        # Styling
```

---

## ▶️ Running the Application

### 1️⃣ Start the Backend API

```bash
cd backend
python3 backend_app.py
```

This runs on port **5002** by default.

### 2️⃣ Start the Frontend

```bash
cd frontend
python3 frontend_app.py
```

Frontend runs on port **5001** by default.

---

## 🌐 Accessing the App

### 🖥 Frontend UI

```
http://localhost:5001/
```

### 📘 Swagger API Documentation

```
http://localhost:5002/api/docs
```

---

## 📡 Request Examples

### ➕ Create Post (POST)

```json
{
  "title": "Hello World",
  "content": "My first blog post!",
  "author": "Student",
  "date": "2023-06-07"
}
```

### 🔍 Search Posts

```
GET /api/posts/search?title=test&author=john
```

### 🔁 Sort Posts

```
GET /api/posts?sort=date&direction=desc
```

---

## 🛑 Validation Rules

| Field | Required | Notes |
|-------|----------|-------|
| `title` | ✔️ | Must be non-empty |
| `content` | ✔️ | Must be non-empty |
| `author` | ✔️ | Must be non-empty |
| `date` | ✔️ | Must follow `YYYY-MM-DD` format |

Invalid requests return a JSON error message and appropriate HTTP status code.

---

## 🏁 Conclusion

This project demonstrates:
- CRUD REST API development with Flask
- Persistent JSON storage
- Input validation & error handling
- Query parameters for search and sorting
- API documentation with Swagger
- Frontend communication via `fetch()`

✨ Built for learning backend + frontend integration using Python!

---

## 🤝 License

This project is for educational use.

---

## 🧑‍💻 Author

Created by **[margarita-bykadorova](https://github.com/margarita-bykadorova)**  
