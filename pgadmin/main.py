from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
from models import Employee

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Employee Service with PostgreSQL")

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {"message": "Welcome to Employee API with PostgreSQL"}


@app.post("/employees/")
def create_employee(name: str, role: str, salary: int, db: Session = Depends(get_db)):
    emp = Employee(name=name, role=role, salary=salary)
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return {"message": "Employee added", "employee": emp}


@app.get("/employees/")
def get_employees(db: Session = Depends(get_db)):
    return db.query(Employee).all()


@app.get("/employees/{emp_id}")
def get_employee(emp_id: int, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp


@app.put("/employees/{emp_id}")
def update_employee(emp_id: int, name: str, role: str, salary: int, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    emp.name = name
    emp.role = role
    emp.salary = salary
    db.commit()
    db.refresh(emp)
    return {"message": "Employee updated", "employee": emp}


@app.delete("/employees/{emp_id}")
def delete_employee(emp_id: int, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(emp)
    db.commit()
    return {"message": "Employee deleted"}
