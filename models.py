
import enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Time, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base





#Tabla para almacenar los datos de las Carreras
class Carrera(Base):
    __tablename__ = "carreras"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True, nullable=False)

    estudiantes = relationship("Estudiante", back_populates="carrera") #relacion con la tabla Estudiante


#Tabla para almacenar los datos de los estudiantes
class Estudiante(Base):
    __tablename__ = "estudiantes"

    id = Column(Integer, ForeignKey("usuarios.id"), primary_key=True, index=True)
    carrera_id = Column(Integer, ForeignKey("carreras.id"))

    usuario = relationship("Usuario", back_populates="estudiante") #relacion con la tabla Usuario
    carrera = relationship("Carrera", back_populates="estudiantes") #relacion con la tabla Carrera


class Administrativos(Base):
    __tablename__ = "administrativos"

    id = Column(Integer, ForeignKey("usuarios.id"), primary_key=True, index=True)
    area = Column(String, nullable=False)
    cargo = Column(String, nullable=False)

    usuario = relationship("Usuario", back_populates="administrativo") #relacion con la tabla Usuario
    



#Tabla para almacenar los datos de los usuarios
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True, nullable=False)
    identificacion = Column(Integer, unique=True, nullable=False)
    correo = Column(String, unique=True, nullable=False)
    contraseña = Column(String, nullable=False)

    estudiante = relationship("Estudiante", back_populates="usuario", uselist=False) #relacion con la tabla Estudiante
    administrativo = relationship("Administrativos", back_populates="usuario", uselist=False) #relacion con la tabla Administrativo
    inscripciones = relationship("Inscripciones", back_populates="usuario")  # Relación con la tabla Inscripciones





#Tabla para almacenar los datos de los tipos de cursos
class Tipo_curso(Base):
    __tablename__ = "tipo_curso"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True, nullable=False)

    cursos = relationship("Curso", back_populates="tipo_curso")  # Relación con la tabla Curso


#Tabla para almacenar los datos de los cursos
class Curso(Base):
    __tablename__ = "cursos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True, nullable=False)
    tipo_curso_id = Column(Integer, ForeignKey("tipo_curso.id"))
    descripcion = Column(String, nullable=True)

    tipo_curso = relationship("Tipo_curso", back_populates="cursos")  # Relación con la tabla tipo_curso
    clases = relationship("Clases", back_populates="cursos")  # Relación con la tabla Clases



#Clase enum.Enum para los días de la semana
class DiaSemana(enum.Enum):
    lunes = "lunes"
    martes = "martes"
    miercoles = "miércoles"
    jueves = "jueves"
    viernes = "viernes"
    sabado = "sábado"
    domingo = "domingo"


#Tabla para almacenar los datos de las clases
class Clases(Base):
    __tablename__ = "clases"

    id = Column(Integer, primary_key=True, index=True)
    curso_id = Column(Integer, ForeignKey("cursos.id"))
    dia = Column(Enum(DiaSemana, name="dia_enum"), nullable=False) #hacemos uso de Enum (tipo que restringe los valores) para la columna dia
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    cupo_maximo = Column(Integer, nullable=False)
    cupo_actual = Column(Integer, default=0, nullable=False)

    cursos = relationship("Curso", back_populates="clases")  # Relación con la tabla Curso
    incripciones = relationship("Inscripciones", back_populates="clase")  # Relación con la tabla Inscripciones


class Inscripciones(Base):
    __tablename__ = "inscripciones"

    id = Column(Integer, primary_key=True, index=True)
    clase_id = Column(Integer, ForeignKey("clases.id"))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    fecha_inscripcion = Column(DateTime, nullable=False) #DateTime alamacena fecha y hora en formato (año, mes, dia, hora, minuto)

    __table_args__ = (
        # Aseguramos que un usuario no pueda inscribirse en la misma clase más de una vez
        UniqueConstraint('clase_id', 'usuario_id', name='usuario_clase_unico'), 
    )

    clase = relationship("Clases", back_populates="incripciones")  # Relación con la tabla Clases
    usuario = relationship("Usuario", back_populates="inscripciones")  # Relación con la tabla Usuarios


