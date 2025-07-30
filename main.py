from typing import Union, List, Annotated
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import models
from database import engine, SessionLocal

from sqlalchemy.orm import Session


app = FastAPI()

#Crea todas las tablas en columnas en postgreSQL
models.Base.metadata.create_all(bind=engine)


class Estudiante(BaseModel):
    id: int
    nombre: str
    apellido: str
    carrera: str


class ClaseBienestarUniversitario(BaseModel):
    id: int
    nombre: str
    descripcion: str


# Conexion con la BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]



@app.get("/")
def read_root():
    return {"Hello": "World"}




@app.post("/clases_bienestar_universitario/", response_model=ClaseBienestarUniversitario)
def create_clase(clase: ClaseBienestarUniversitario, db: db_dependency):
    db_clase = models.ClasesBienestarUniversitario(**clase.dict())
    db.add(db_clase)
    db.commit()
    db.refresh(db_clase)
    return db_clase
