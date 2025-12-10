
import security
import models
import io
from openpyxl import Workbook
from fastapi.responses import StreamingResponse

from typing import Union, List, Annotated
from fastapi import FastAPI, HTTPException, Depends, Response
from pydantic import BaseModel, EmailStr, Field, HttpUrl
from datetime import time, datetime
from enum import Enum
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware







app = FastAPI()

# Crea todas las tablas en la base de datos (PostgreSQL)
models.Base.metadata.create_all(bind=engine)




# Conexion con la BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


app.add_middleware(
    CORSMiddleware,
    # Temporalmente permitir todos los orígenes para depuración. Revertir a origen específico en producción.
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)




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

# Modelo para registrar un usuario
class UsuarioRegistrar(BaseModel):
    nombre: str
    identificacion: int
    correo: EmailStr
    contrasena: str = Field(..., min_length=8)

# Ruta para registrar un nuevo usuario
@app.post("/registrar_usuario")
def registrar_usuario(usuario: UsuarioRegistrar, db: Session = Depends(get_db)):
    # Busca en la db si el usuario ya existe por identificación o correo
    existe = db.query(models.Usuario).filter(
        (models.Usuario.identificacion == usuario.identificacion) |
        (models.Usuario.correo == usuario.correo)
    ).first()
    # Si el usuario ya existe, lanza una excepción HTTP 400
    if existe:
        raise HTTPException(status_code=400, detail="Usuario ya existe")
    
    # En caso contrario, crea un nuevo usuario
    nuevo_usuario = models.Usuario(
        nombre_apellido=usuario.nombre,
        identificacion=usuario.identificacion,
        correo=usuario.correo,
        contrasena=security.hash_password(usuario.contrasena) # Hasheamos la contraseña antes de guardarla en la base de datos
    )
    # Añade el nuevo usuario a la sesión de la BD
    db.add(nuevo_usuario) # Añade el nuevo usuario a la sesion de la BD
    db.commit() # Guarda los cambios en la BD
    db.refresh(nuevo_usuario)  #Actualiza el objeto nuevo_usuario con los datos de la BD
    return {"msg": "Usuario registrado correctamente", "usuario_id": nuevo_usuario.id}



# Modelo para login de usuario
class UsuarioLogin(BaseModel):
    identificacion: int
    contrasena: str

# Ruta para iniciar sesión (ahora emite JWT)
@app.post("/iniciar_sesion")
def iniciar_sesion(credenciales: UsuarioLogin, response: Response, db: Session = Depends(get_db)):
    # Busca en la BD si el usuario existe por identificación
    existe_usuario = db.query(models.Usuario).filter(models.Usuario.identificacion == credenciales.identificacion).first()
    # Verificamos la contraseña contra el hash almacenado
    if not existe_usuario or not security.verify_password(credenciales.contrasena, existe_usuario.contrasena):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    # Construimos la información que devolveremos al frontend
    usuario_info = {"usuario_nombre": existe_usuario.nombre_apellido, "usuario_identificacion": existe_usuario.identificacion}

    rol = db.query(models.Administrativo).join(models.Usuario).filter(models.Usuario.identificacion == credenciales.identificacion).first()
    if rol:
        usuario_info.update({"area": rol.area, "rol": rol.rol})
    else:
        estudiante = db.query(models.Estudiante).join(models.Usuario).filter(models.Usuario.identificacion == credenciales.identificacion).first()
        if estudiante:
            semestre = estudiante.semestre if estudiante else None
            carrera = estudiante.nombre_carrera.value if estudiante and estudiante.nombre_carrera else None
            usuario_info.update({"semestre": semestre, "carrera": carrera, "rol": "Estudiante"})
        else:
            usuario_info.update({"rol": "Indefinido"})

    # Payload mínimo para el token (puedes añadir más claims si los necesitas)
    token_payload = {
        "sub": str(existe_usuario.identificacion),
        "usuario_nombre": existe_usuario.nombre_apellido,
        "identificacion": existe_usuario.identificacion,
        "rol": usuario_info.get("rol"),
        "area": usuario_info.get("area")
    }

    access_token = security.create_access_token(token_payload)

    # Opcional: establecer cookie HttpOnly (más segura que exponer token en localStorage)
    # En producción configurar `secure=True` y usar HTTPS
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=security.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    # Devolvemos el token y la info del usuario (frontend puede preferir usar solo la cookie)
    return {"msg": "Inicio de sesión exitoso", **usuario_info, "access_token": access_token, "token_type": "bearer"}



# Ruta para los cursos
@app.get('/cursos')
def listar_cursos(db: Session = Depends(get_db)):
    cursos = db.query(models.Curso).all()

    lista_cursos = []
    for c in cursos:
        lista_cursos.append({
            'id': c.id,
            'nombre': c.nombre,
            'descripcion': c.descripcion,
            'tipo_curso': c.tipo_curso,
            'imagen': getattr(c, 'imagen', None),
            'activo': getattr(c, 'activo', True)
        })
    return lista_cursos



# Ruta para obtener los horarios de un curso específico
@app.get('/cursos/{curso_id}/horario')
def obtener_horarios_curso(curso_id: int, identificacion: int, db: Session = Depends(get_db)):
    # Buscamos el curso y comprobamos existencia
    curso = db.query(models.Curso).filter(models.Curso.id == curso_id).first()
    if not curso:
        raise HTTPException(status_code=404, detail='Curso no encontrado')

    # Estado del curso (botón global): si el curso está desactivado, no dejar inscribir
    curso_activo = bool(getattr(curso, 'activo', True))

    # Traemos los horarios asociados al curso (todos) y los iteramos
    horarios_q = db.query(models.Horario).filter(models.Horario.curso_id == curso_id).all()
    horarios = []


    usuario = db.query(models.Usuario).filter(models.Usuario.identificacion == identificacion).first()
    if not usuario:
        raise HTTPException(status_code=404, detail='Usuario no encontrado')



    for hor in horarios_q:
        # Determinar si el horario está activo
        horario_activo = bool(getattr(hor, 'activo', True))

        # Cupo disponible
        cupo_disponible = getattr(hor, 'cupo_disponible', None)

        # Validamos si el usuario ya está inscrito en este horario
        # Por defecto: usuario no inscrito
        inscrito = False
        if usuario:
            existe = db.query(models.Inscripcion).filter(
                models.Inscripcion.horario_id == hor.id,
                models.Inscripcion.usuario_id == usuario.id
            ).first()
            inscrito = True if existe else False


        horarios.append({
            'id': hor.id,
            'dia': hor.dia.value if hasattr(hor.dia, 'value') else str(hor.dia),
            'hora_inicio': hor.hora_inicio.isoformat() if hor.hora_inicio else None,
            'hora_fin': hor.hora_fin.isoformat() if hor.hora_fin else None,
            'profesor': hor.profesor,
            'cupo_disponible': cupo_disponible,
            'activo_horario': horario_activo,
            'inscrito': inscrito
        })

    return {'horarios': horarios}



# Ruta para inscribirse o cancelar la inscripción en un horario de un curso
@app.post('/horario/{horario_id},{curso_id}/inscripcion')
def gestionar_inscripcion(horario_id: int, curso_id: int, identificacion: int, db: Session = Depends(get_db)):
    # Verificamos que el usuario exista
    usuario = db.query(models.Usuario).filter(models.Usuario.identificacion == identificacion).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Verificamos que el horario exista
    horario = db.query(models.Horario).filter(models.Horario.id == horario_id).first()
    if not horario:
        raise HTTPException(status_code=404, detail="Horario no encontrado")
    
    # Verificamos que el curso asociado al horario esté activo
    curso = db.query(models.Curso).filter(models.Curso.id == horario.curso_id).first()
    if not curso or not getattr(curso, 'activo', True):
        raise HTTPException(status_code=400, detail="El curso asociado al horario no está activo")
    
    # Verificamos que el horario esté activo
    if not getattr(horario, 'activo', True):
        raise HTTPException(status_code=400, detail="El horario no está activo")
    
    # Verificamos si el usuario ya está inscrito en este horario
    inscripcion_existente = db.query(models.Inscripcion).filter(
        models.Inscripcion.horario_id == horario.id,
        models.Inscripcion.usuario_id == usuario.id
    ).first()

    if inscripcion_existente:
        # Si ya está inscrito, procedemos a cancelar la inscripción
        db.delete(inscripcion_existente)
        # Incrementamos el cupo disponible si es aplicable
        if horario.cupo_disponible is not None:
            horario.cupo_disponible += 1
        db.commit()
        return {"msg": "Inscripción cancelada correctamente"}
    else:
        # Si no está inscrito, verificamos si hay cupo disponible para inscribir
        if horario.cupo_disponible is not None and horario.cupo_disponible <= 0:
            raise HTTPException(status_code=400, detail="No hay cupo disponible en este horario")
        
        # Procedemos a inscribir al usuario
        nueva_inscripcion = models.Inscripcion(
            horario_id=horario.id,
            usuario_id=usuario.id,
            fecha_inscripcion=datetime.now(),
        )
        db.add(nueva_inscripcion)
        # Decrementamos el cupo disponible si es aplicable
        if horario.cupo_disponible is not None:
            horario.cupo_disponible -= 1
        db.commit()
        return {"msg": "Inscripción realizada correctamente"}












# Endpoints para administradores


# Ruta para reporte de cursos, horarios, inscripciones y usuarios
@app.get("/reporte_cursos/{identificacion}")
def reporte_cursos(identificacion: int, tipo_curso: Union[models.TipoCurso, None] = None,  db: Session = Depends(get_db)):
    query = db.query(models.Curso)
    if tipo_curso:
        query = query.filter(models.Curso.tipo_curso == tipo_curso)
    
    cursos = query.all()
    reporte = []

    for curso in cursos:
        curso_info = {
            "nombre": curso.nombre,
            "tipo_curso": curso.tipo_curso,
            "horarios": []
        }

        for horario in curso.horario:
            horario_info = {
                "dia": horario.dia.value if hasattr(horario.dia, 'value') else str(horario.dia),
                "hora_inicio": horario.hora_inicio.isoformat() if horario.hora_inicio else None,
                "hora_fin": horario.hora_fin.isoformat() if horario.hora_fin else None,
                "profesor": horario.profesor,
                "cantidad de matriculados": len(horario.inscripcion) if horario.inscripcion else 0,
                "inscripciones": []
            }

            for inscripcion in horario.inscripcion:
                usuario = db.query(models.Usuario).filter(models.Usuario.id == inscripcion.usuario_id).first()
                usuario_info = {
                    "nombre": usuario.nombre_apellido,
                    "identificacion": usuario.identificacion,
                    "correo": usuario.correo
                }
                inscripcion_info = {
                    "usuario": usuario_info,
                    "fecha_inscripcion": inscripcion.fecha_inscripcion.isoformat() if inscripcion.fecha_inscripcion else None,
                }
                horario_info["inscripciones"].append(inscripcion_info)

            curso_info["horarios"].append(horario_info)

        reporte.append(curso_info)

    return reporte



@app.get("/reporte_cursos/{identificacion}/excel")
def reporte_cursos_excel(identificacion: int, tipo_curso: Union[models.TipoCurso, None] = None, db: Session = Depends(get_db)):
    """Genera un archivo Excel (.xlsx) con el mismo contenido que devuelve `/reporte_cursos`.
    Se crea una hoja por curso; cada fila representa un horario y sus inscripciones (si las hay).
    Devuelve un StreamingResponse con el archivo para descarga.
    """
    query = db.query(models.Curso)
    if tipo_curso:
        query = query.filter(models.Curso.tipo_curso == tipo_curso)

    cursos = query.all()

    wb = Workbook()
    # Si hay al menos un curso, eliminamos la hoja por defecto y creamos por curso
    if cursos:
        # eliminar hoja por defecto
        default = wb.active
        wb.remove(default)

        for curso in cursos:
            # sheet title max 31 chars
            title = f"{curso.id}_{curso.nombre}"[:31]
            ws = wb.create_sheet(title=title)
            # Encabezados
            ws.append(["Dia", "Hora Inicio", "Hora Fin", "Profesor", "Cantidad Matriculados", "Usuario Nombre", "Identificacion", "Correo", "Fecha Inscripcion"])

            for horario in curso.horario:
                cantidad = len(horario.inscripcion) if horario.inscripcion else 0
                # Si hay inscripciones, escribir una fila por cada inscripcion
                if horario.inscripcion:
                    for inscripcion in horario.inscripcion:
                        usuario = db.query(models.Usuario).filter(models.Usuario.id == inscripcion.usuario_id).first()
                        ws.append([
                            horario.dia.value if hasattr(horario.dia, 'value') else str(horario.dia),
                            horario.hora_inicio.isoformat() if horario.hora_inicio else None,
                            horario.hora_fin.isoformat() if horario.hora_fin else None,
                            horario.profesor,
                            cantidad,
                            usuario.nombre if usuario else None,
                            usuario.identificacion if usuario else None,
                            usuario.correo if usuario else None,
                            inscripcion.fecha_inscripcion.isoformat() if inscripcion.fecha_inscripcion else None
                        ])
                else:
                    # Sin inscripciones, una sola fila con columnas de usuario vacías
                    ws.append([
                        horario.dia.value if hasattr(horario.dia, 'value') else str(horario.dia),
                        horario.hora_inicio.isoformat() if horario.hora_inicio else None,
                        horario.hora_fin.isoformat() if horario.hora_fin else None,
                        horario.profesor,
                        cantidad,
                        None,
                        None,
                        None,
                        None
                    ])
    else:
        # Sin cursos: dejar una hoja con un mensaje
        ws = wb.active
        ws.title = "Reporte"
        ws.append(["No hay cursos para el filtro especificado"]) 

    # Guardar en buffer y devolver como streaming
    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)

    filename = f"reporte_cursos_{identificacion}.xlsx"
    headers = {"Content-Disposition": f"attachment; filename={filename}"}
    return StreamingResponse(stream, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)










# Modelo para registrar un curso
class RegistrarCurso (BaseModel):
    nombre: str
    tipo_curso: models.TipoCurso
    descripcion: str = None
    imagen: HttpUrl
    activo: bool = True

# Ruta para registrar un nuevo curso
@app.post("/registrar_curso")
def registrar_curso(curso: RegistrarCurso, db: Session = Depends(get_db)):
    # Crea un nuevo curso
    nuevo_curso = models.Curso(
        nombre=curso.nombre,
        tipo_curso=curso.tipo_curso,
        descripcion=curso.descripcion,
        imagen=curso.imagen,
        activo=curso.activo
    )
    # Añade el nuevo curso a la sesión de la BD
    db.add(nuevo_curso) # Añade el nuevo curso a la sesion de la BD
    db.commit() # Guarda los cambios en la BD
    db.refresh(nuevo_curso)  #Actualiza el objeto nuevo_usuario con los datos de la BD
    return {"msg": "Curso registrado correctamente", "curso_id": nuevo_curso.id}



# Modelo para registrar un horario
class RegistrarHorario (BaseModel):
    curso_id: int
    dia: models.DiaSemana
    hora_inicio: time  # Formato "HH:MM:SS"
    hora_fin: time     # Formato "HH:MM:SS"
    profesor: str = None
    cupo_maximo: int
    activo: bool = True

# Ruta para registrar un nuevo horario
@app.post("/registrar_horario")
def registrar_horario(horario: RegistrarHorario, db: Session = Depends(get_db)):
    # Verifica que el curso exista
    curso = db.query(models.Curso).filter(models.Curso.id == horario.curso_id).first()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    
    # Crea un nuevo horario
    nuevo_horario = models.Horario(
        curso_id=horario.curso_id,
        dia=horario.dia,
        hora_inicio=horario.hora_inicio,
        hora_fin=horario.hora_fin,
        profesor=horario.profesor,
        cupo_maximo=horario.cupo_maximo,
        cupo_disponible=horario.cupo_maximo,  # Inicialmente el cupo disponible es igual al máximo
        activo=horario.activo
    )

    # Añade el nuevo horario a la sesión de la BD
    db.add(nuevo_horario) # Añade el nuevo horario a la sesion de la BD
    db.commit() # Guarda los cambios en la BD
    db.refresh(nuevo_horario)  #Actualiza el objeto nuevo_horario con los datos de la BD
    return {"msg": "Horario registrado correctamente", "horario_id": nuevo_horario.id}



# Ruta para eliminar un curso y sus horarios e inscripciones asociadas
@app.delete("/eliminar_curso/{curso_id}")
def eliminar_curso(curso_id: int, db: Session = Depends(get_db)):
    # Busca el curso por ID
    curso_existente = db.query(models.Curso).filter(models.Curso.id == curso_id).first()
    if not curso_existente:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    
    # Busca horarios asociados al curso
    horarios_asociados = db.query(models.Horario).filter(models.Horario.curso_id == curso_id).all()
    for horario in horarios_asociados:
        # Elimina inscripciones asociadas a cada horario
        db.query(models.Inscripcion).filter(models.Inscripcion.horario_id == horario.id).delete()
        # Elimina el horario
        db.delete(horario)

    # Elimina el curso
    db.delete(curso_existente)
    db.commit()  # Guarda los cambios en la BD
    return {"msg": "Curso eliminado correctamente", "curso_id": curso_id}



# Ruta para eliminar un horario y sus inscripciones asociadas
@app.delete("/eliminar_horario/{horario_id}") 
def eliminar_horario(horario_id: int, db: Session = Depends(get_db)):
    # Busca el horario por ID
    horario_existente = db.query(models.Horario).filter(models.Horario.id == horario_id).first()
    if not horario_existente:
        raise HTTPException(status_code=404, detail="Horario no encontrado")
    
    # Elimina inscripciones asociadas al horario
    db.query(models.Inscripcion).filter(models.Inscripcion.horario_id == horario_id).delete()
    
    # Elimina el horario
    db.delete(horario_existente)
    db.commit()  # Guarda los cambios en la BD
    return {"msg": "Horario eliminado correctamente", "horario_id": horario_id}



# Ruta para modificar un curso
@app.put("/modificar_curso/{curso_id}")
def modificar_curso(curso_id: int, curso: RegistrarCurso, db: Session = Depends(get_db)):
    # Busca el curso por ID
    curso_existente = db.query(models.Curso).filter(models.Curso.id == curso_id).first()
    if not curso_existente:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    
    # Actualiza los campos del curso
    curso_existente.nombre = curso.nombre
    curso_existente.tipo_curso = curso.tipo_curso
    curso_existente.descripcion = curso.descripcion
    curso_existente.imagen = str(curso.imagen)

    curso_existente.activo = curso.activo

    db.commit()  # Guarda los cambios en la BD
    db.refresh(curso_existente)  # Actualiza el objeto con los datos de la BD
    return {"msg": "Curso modificado correctamente", "curso_id": curso_existente.id}



# Ruta para modificar el rol de un usuario
@app.post("/modificar_rol/{identificacion}")
def modificar_rol(identificacion: int, nuevo_rol: str, nuevo_area: str, db: Session = Depends(get_db)):
    # Busca el usuario por identificación
    usuario_existente = db.query(models.Usuario).filter(models.Usuario.identificacion == identificacion).first()
    if not usuario_existente:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Verifica si usuario ya tiene el rol de administrativo
    administrativo_existente = db.query(models.Administrativo).filter(models.Administrativo.id == usuario_existente.id).first()
    
    # Si existe rol en administrativo eliminamos el rol
    if administrativo_existente:
        db.delete(administrativo_existente)
        db.commit()
        return {"msg": "Rol de administrativo eliminado correctamente", "usuario_id": usuario_existente.identificacion}
    else:
        # Si no existe, creamos el rol de administrativo
        nuevo_administrativo = models.Administrativo(
            id=usuario_existente.id,
            area=nuevo_area,
            rol=nuevo_rol
        )
        db.add(nuevo_administrativo)
        db.commit()
        db.refresh(nuevo_administrativo)
        return {"msg": "Rol de administrativo asignado correctamente", "usuario_id": usuario_existente.identificacion}
