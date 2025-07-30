# -*- coding: utf-8 -*-

from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from database import Base

class DatosEstudiantes(Base):
    __tablename__ = "datos_estudiantes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    apellido = Column(String, index=True)
    carrera = Column(String, index=True)


class ClasesBienestarUniversitario(Base):
    __tablename__ = "clases_bienestar_universitario"

    id = Column(Integer, primary_key=True, index=True) 
    nombre = Column(String, index=True)
    descripcion = Column(String, index=True)

