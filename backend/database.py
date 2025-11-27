from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

URL_DATABASE = "postgresql://uscadminpostgres:P7D2niA4WGkiVUA8ocPMea8ezErcv2qu@dpg-d4kcj0i4d50c73de0s0g-a/cursos_usc_bienestar_db_2frf" # URL para conexion en la nube Render


"""URL_DATABASE = "postgresql://postgres:postgres123@localhost:5432/cursos_USC_Bienestar_db" # URL para conexion local"""

engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
