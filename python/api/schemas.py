from datetime import date
from pydantic import BaseModel, Field

from models import PolozkyItem

class VacancySummary(BaseModel):
    id: str
    profese: str
    zamestnavatel: str | None
    mesicni_mzda_od: float | None
    mesicni_mzda_do: float | None
    typ_mzdy: str | None
    kraj: str | None
    pocet_mist: int
    datum_vlozeni: date
