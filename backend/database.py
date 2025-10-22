from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

URL_DATABASE = "postgresql://uscadminpostgres:08zzxdsCMmBiu0sAShmtkLUOFK08WQ5B@dpg-d3s4omer433s73chi2s0-a/cursos_usc_bienestar_db" # URL para conexion en la nube Render

"""URL_DATABASE = "postgresql://postgres:postgres123@localhost:5432/cursos_USC_Bienestar_db" """ # URL para conexion local

engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()