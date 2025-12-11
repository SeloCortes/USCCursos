from datetime import datetime
import pytz

def hora_colombia():
    return datetime.now(pytz.timezone("America/Bogota"))
