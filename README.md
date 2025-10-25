# FastAPI + PostgreSQL Service

This is a simple **FastAPI** web service connected to a **PostgreSQL** database.
It provides REST APIs to manage employees.

## 🚀 Features
- Create, Read, Update, Delete (CRUD) employees
- Uses SQLAlchemy ORM
- PostgreSQL integration
- Auto-generated Swagger docs

## 🧠 Setup Instructions
```bash
pip install -r requirements.txt
uvicorn main:app --reload
