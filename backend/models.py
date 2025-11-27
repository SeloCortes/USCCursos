
import enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Time, Enum, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship
from database import Base





# Clase Enum para los tipos de facultad
class TipoFacultad(enum.Enum):
    """ Enum para los tipos de facultad
    salud = "Salud"
    derecho = "Derecho"
    ingenieria = "Ingenieria"
    educacion = "Educacion"
    ciencias_basicas = "Ciencias Basicas"
    ciencias_economicas_y_empresariales = "Ciencias Economicas y Empresariales"    
    """
    salud = "Salud"
    derecho = "Derecho"
    ingenieria = "Ingenieria"
    educacion = "Educacion"
    ciencias_basicas = "Ciencias Basicas"
    humanidades_y_artes = "Humanidades y Artes"
    ciencias_economicas_y_empresariales = "Ciencias Economicas y Empresariales"

# Clase Enum para los nombres de las carreras
class TipoNombreCarrera(enum.Enum):
    """ Enum para los nombres de las carreras de todas las facultades
    """
    medicina = "Medicina"
    enfermeria = "Enfermeria"
    fisioterapia = "Fisioterapia"
    odontologia = "Odontologia"
    psicologia = "Psicologia"
    fonoaudiologia = "Fonoaudiologia"
    terapia_respiratoria = "Terapia Respiratoria"
    instrumentacion_quirurgica = "Instrumentacion Quirurgica"

    derecho = "Derecho"
    ciencia_politica = "Ciencia Politica"

    bioingenieria = "Bioingenieria"
    ingenieria_civil = "Ingenieria Civil"
    ingenieria_quimica = "Ingenieria Quimica"
    ingenieria_industrial = "Ingenieria Industrial"
    ingenieria_comercial = "Ingenieria Comercial"
    ingenieria_electronica = "Ingenieria Electronica"
    ingenieria_en_energias = "Ingenieria en Energias"
    ingenieria_en_sistemas = "Ingenieria en Sistemas"

    licenciatura_en_educacion_infantil = "Educacion Infantil"
    licenciatura_en_educacion_fisica_y_deporte = "Educacion Fisica"
    licenciatura_en_lenguas_extranjeras = "Lenguas Extranjeras con enfasis en Ingles - Frances"

    quimica = "Quimica"
    microbiologia = "Microbiologia"
    medicina_veterinaria = "Medicina Veterinaria"
    quimica_farmaceutica = "Quimica Farmaceutica"

    publicidad = "Publicidad"
    trabajo_social = "Trabajo Social"
    comunicacion_social = "Comunicacion Social"

    economia = "Economia"
    mercadeo = "Mercadeo"
    contaduria_publica = "Contaduria Publica"
    administracion_de_empresas = "Administracion de Empresas"
    finanzas_y_negocios_internacionales = "Finanzas y Negocios Internacionales"

# Tabla para almacenar los datos de estudiante
class Estudiante(Base):
    __tablename__ = "estudiante"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuario.identificacion"), unique=True, nullable=False)
    facultad = Column(Enum(TipoFacultad, name="tipo_facultad_enum"), nullable=False) 
    nombre_carrera = Column(Enum(TipoNombreCarrera, name="tipo_nombre_carrera_enum"), nullable=False)
    semestre = Column(Integer, nullable=False)

    usuario = relationship("Usuario", back_populates="estudiante") # Relación con la tabla Usuario



# Clase Enum para los tipos de rol administrativo
class TipoRol(enum.Enum):
    """ Enum para los tipos de rol administrativo
    admin = "admin"
    coordinador = "coordinador"
    administrativo = "administrativo"    
    """
    admin = "admin"
    coordinador = "coordinador"
    administrativo = "administrativo"
# Tabla para almacenar los datos de administrativo
class Administrativo(Base):
    __tablename__ = "administrativo"

    id = Column(Integer, ForeignKey("usuario.id"), primary_key=True, index=True)
    area = Column(String, nullable=False)
    rol = Column(Enum(TipoRol, name="tipo_rol_enum"), nullable=False) 

    usuario = relationship("Usuario", back_populates="administrativo") # Relación con la tabla Usuario



# Clase Enum para los tipos de estamento tercero
class TipoEstamento(enum.Enum):
    """ Enum para los tipos de estamento tercero
    egresado = "egresado"
    profesor = "profesor"
    asistente = "asistente"   
    """
    egresado = "egresado"
    profesor = "profesor"
    asistente = "asistente"
#Tabla para usuarios terceros
class Tercero(Base):
    __tablename__ = "tercero"

    id = Column(Integer, primary_key=True, index=True)
    estamento = Column(Enum(TipoEstamento, name="tipo_estamento_enum"), nullable=False)



class TipoGenero(enum.Enum):
    """ Enum para los tipos de genero
    masculino = "masculino"
    femenino = "femenino"
    otro = "otro"   
    """
    masculino = "masculino"
    femenino = "femenino"
    otro = "otro"
# Tabla para almacenar los datos de usuario
class Usuario(Base):
    __tablename__ = "usuario"

    id = Column(Integer, primary_key=True, index=True)
    nombre_apellido = Column(String, index=True, nullable=False)
    identificacion = Column(Integer, unique=True, nullable=False)
    correo = Column(String, unique=True, nullable=False)
    contrasena = Column(String, nullable=False)
    telefono = Column(String, nullable=True)
    genero = Column(Enum(TipoGenero, name="tipo_genero_enum"), nullable=True)
    etnia = Column(String, nullable=True)
    discapacidad = Column(String, nullable=True)

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

    __table_args__ = (
        # Aseguramos que un usuario no pueda inscribirse en la misma clase más de una vez
        UniqueConstraint('horario_id', 'usuario_id', name='usuario_clase_unico'), 
    )

    horario = relationship("Horario", back_populates="inscripcion")  # Relación con la tabla Clases
    usuario = relationship("Usuario", back_populates="inscripcion")  # Relación con la tabla Usuarios


