from datetime import datetime
from zoneinfo import ZoneInfo


def hora_colombia():
    return datetime.now(ZoneInfo("America/Bogota"))
