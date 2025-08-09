from typing import Union, List, Annotated
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr, constr
import models
from database import engine, SessionLocal

from sqlalchemy.orm import Session


app = FastAPI()

#Crea todas las tablas en columnas en postgreSQL
models.Base.metadata.create_all(bind=engine)




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


"""
Diferencia entre códigos de status_code:

200: OK. Todo salió bien.
201: Created. Recurso creado exitosamente.
400: Bad Request. La petición es incorrecta (por ejemplo, datos inválidos).
401: Unauthorized. No autorizado (credenciales incorrectas).
403: Forbidden. Prohibido (no tienes permisos).
404: Not Found. No se encontró el recurso.
500: Internal Server Error. Error interno del servidor.
"""


##########################################

#modelo para registrar un usuario
class UsuarioRegistrar(BaseModel):
    nombre: str
    identificacion: int
    correo: EmailStr
    contraseña: constr(min_length=8)


#modelo para login de usuario
class UsuarioLogin(BaseModel):
    identificacion: int
    contraseña: str


# Ruta para registrar un nuevo usuario
@app.post("/registrar_usuario")
def registrar_usuario(usuario: UsuarioRegistrar, db: db_dependency):
    # Busca en la BD si el usuario ya existe por identificacion o correo
    existe = db.query(models.Usuario).filter(
        (models.Usuario.identificacion == usuario.identificacion) |
        (models.Usuario.correo == usuario.correo)
    ).first()
    # Si el usuario ya existe, lanza una excepción HTTP 400 ()
    if existe:
        raise HTTPException(status_code=400, detail="Usuario ya existe")
    
    # De lo contrario crea un nuevo usuario
    nuevo_usuario = models.Usuario(
        nombre=usuario.nombre,
        identificacion=usuario.identificacion,
        correo=usuario.correo,
        contraseña=usuario.contraseña
    )
    # Añade el nuevo usuario a la sesión de la BD
    db.add(nuevo_usuario) #añade el nuevo usuario a la sesion de la BD
    db.commit() #guarda los cambios en la BD
    db.refresh(nuevo_usuario)  #Actualiza el objeto nuevo_usuario con los datos de la BD
    return {"msg": "Usuario registrado correctamente", "usuario_id": nuevo_usuario.id}



# Ruta para iniciar sesión
@app.post("/iniciar_sesion")
def iniciar_sesion(usuario: UsuarioLogin, db: db_dependency):
    # Busca en la BD si el usuario existe por identificacion
    usuario = db.query(models.Usuario).filter(
        (models.Usuario.identificacion == usuario.identificacion) &
        (models.Usuario.contraseña == usuario.contraseña)
    ).first()
    # Verifica si el usuario existe y si la contraseña es coincide
    if not usuario or usuario.contraseña != usuario.contraseña:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    return {"msg": "Inicio de sesión exitoso", "usuario_id": usuario.id}

