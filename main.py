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


@app.get("/datos_clases_bienestar_universitario/")
async def datos_clases(db: db_dependency):
    clases = db.query(models.ClasesBienestarUniversitario).all()
    return clases




@app.post("/clases_bienestar_universitario/")
#endpoint para crear una clase de bienestar universitario (sigue la estructura de la clase ClaseBienestarUniversitario)
def crear_clase(clase: ClaseBienestarUniversitario, db: db_dependency):
    db_clase = models.ClasesBienestarUniversitario()



""""
@app.get("/clases_bienestar_universitario_nombre/", response_model=List[ClaseBienestarUniversitario])
def buscar_clase_por_nombre(nombre: str, db: db_dependency):

    Busca clases de bienestar universitario por nombre.

    clases = db.query(models.ClasesBienestarUniversitario).filter(
        models.ClasesBienestarUniversitario.nombre == nombre
    ).all()
    return clases


"""


