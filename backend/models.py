
import enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Time, Enum, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship
from database import Base





# Tabla para almacenar los datos de carrera
class Carrera(Base):
    __tablename__ = "carrera"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True, nullable=False)

    estudiante = relationship("Estudiante", back_populates="carrera") # Relación con la tabla estudiante


# Tabla para almacenar los datos de estudiante
class Estudiante(Base):
    __tablename__ = "estudiante"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuario.identificacion"), unique=True, nullable=False)
    carrera_id = Column(Integer, ForeignKey("carrera.id") , nullable=True)
    semestre = Column(Integer, nullable=False)

    usuario = relationship("Usuario", back_populates="estudiante") # Relación con la tabla Usuario
    carrera = relationship("Carrera", back_populates="estudiante") # Relación con la tabla Carrera


# Tabla para almacenar los datos de administrativo
class Administrativo(Base):
    __tablename__ = "administrativo"

    id = Column(Integer, ForeignKey("usuario.id"), primary_key=True, index=True)
    area = Column(String, nullable=False)
    cargo = Column(String, nullable=False)

    usuario = relationship("Usuario", back_populates="administrativo") # Relación con la tabla Usuario
    

# Tabla para almacenar los datos de usuario
class Usuario(Base):
    __tablename__ = "usuario"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True, nullable=False)
    identificacion = Column(Integer, unique=True, nullable=False)
    correo = Column(String, unique=True, nullable=False)
    contrasena = Column(String, nullable=False)

    estudiante = relationship("Estudiante", back_populates="usuario", uselist=False) # Relación con la tabla Estudiante
    administrativo = relationship("Administrativo", back_populates="usuario", uselist=False) # Relación con la tabla Administrativo
    inscripcion = relationship("Inscripcion", back_populates="usuario")  # Relación con la tabla Inscripcion


# Clase Enum para los tipos de curso
class TipoCurso(enum.Enum):
    """ Enum para los tipos de curso
    deporte = "Deporte Formativo"
    arte = "Arte y Cultura"
    catedra = "Catedra Santiaguina"
    """
    deporte = "Deporte Formativo"
    arte = "Arte y Cultura"
    catedra = "Catedra Santiaguina"


# Tabla para almacenar los datos de curso
class Curso(Base):
    __tablename__ = "curso"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True, nullable=False)
    tipo_curso = Column(Enum(TipoCurso, name="tipo_curso_enum"), nullable=False) # Hacemos uso de Enum "TipoCurso" para la columna tipo_curso
    descripcion = Column(String, nullable=True)
    imagen = Column(String)  # URL o path de la imagen del curso
    activo = Column(Boolean, default=True, nullable=False)  # Indica si el curso está activo o no

    horario = relationship("Horario", back_populates="curso")  # Relación con la tabla Horario



# Claese Enum para los días de la semana
class DiaSemana(enum.Enum):

    
    lunes = "lunes"
    martes = "martes"
    miercoles = "miercoles"
    jueves = "jueves"
    viernes = "viernes"
    sabado = "sabado"
    domingo = "domingo"


# Tabla para almacenar los datos de horario
class Horario(Base):
    __tablename__ = "horario"

    id = Column(Integer, primary_key=True, index=True)
    curso_id = Column(Integer, ForeignKey("curso.id"))
    dia = Column(Enum(DiaSemana, name="dia_enum"), nullable=False) # Hacemos uso de Enum "DiaSemana" para la columna dia
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    profesor = Column(String, nullable=True)
    cupo_maximo = Column(Integer, nullable=False)
    cupo_disponible = Column(Integer, default=0, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)  # Indica si la clase está activa o no

    curso = relationship("Curso", back_populates="horario")  # Relación con la tabla Curso
    inscripcion = relationship("Inscripcion", back_populates="horario")  # Relación con la tabla Inscripcion

 


# Tabla para almacenar los datos de inscripcion
class Inscripcion(Base):
    __tablename__ = "inscripcion"

    id = Column(Integer, primary_key=True, index=True)
    horario_id = Column(Integer, ForeignKey("horario.id"))
    usuario_id = Column(Integer, ForeignKey("usuario.id"))
    fecha_inscripcion = Column(DateTime, nullable=False) # DateTime almacena fecha y hora en formato (año, mes, dia, hora, minuto)
    estado = Column(Boolean, default=False, nullable=False)  # Indica si el usuario está inscrito o no

    __table_args__ = (
        # Aseguramos que un usuario no pueda inscribirse en la misma clase más de una vez
        UniqueConstraint('horario_id', 'usuario_id', name='usuario_clase_unico'), 
    )

    horario = relationship("Horario", back_populates="inscripcion")  # Relación con la tabla Clases
    usuario = relationship("Usuario", back_populates="inscripcion")  # Relación con la tabla Usuarios


