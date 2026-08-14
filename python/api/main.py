from fastapi import FastAPI, HTTPException
from pathlib import Path
from contextlib import asynccontextmanager
from fetch_data import get_cached_data
from models import PolozkyItem, VolnaMista
from api.schemas import VacancySummary

vacancies: list[PolozkyItem] = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    json_data = get_cached_data("https://data.mpsv.cz/od/soubory/volna-mista/volna-mista.json", Path(__file__).parent.parent / "data/raw/volna-mista.json")
    volna_mista = VolnaMista(**json_data)
    vacancies.extend(volna_mista.polozky)
    yield

def get_kraj(item: PolozkyItem) -> str | None:
    if item.mistoVykonuPrace and item.mistoVykonuPrace.pracoviste:
        pracoviste = item.mistoVykonuPrace.pracoviste[0]
        if pracoviste.adresa and pracoviste.adresa.kraj:
            return pracoviste.adresa.kraj.id
    return None

def summarize(item: PolozkyItem) -> VacancySummary:
    kraj = get_kraj(item)
    return VacancySummary(
        id = item.id,
        profese = item.pozadovanaProfese.cs,
        zamestnavatel = item.zamestnavatel.nazev if item.zamestnavatel else None,
        mesicni_mzda_od = item.mesicniMzdaOd,
        mesicni_mzda_do = item.mesicniMzdaDo,
        typ_mzdy = item.typMzdy.id if item.typMzdy else None,
        kraj = kraj,
        pocet_mist = item.pocetMist,
        datum_vlozeni = item.datumVlozeni,
    )
    
app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/vacancies", response_model=list[VacancySummary])
def get_vacancies(
    offset: int = 0,
    limit: int = 20,
    kraj: str | None = None,
    typ_mzdy: str | None = None,
    mzda_min: float | None = None,
    profese: str | None = None,    
):
    filtered_vacancies = vacancies
    if kraj is not None:
        filtered_vacancies = [v for v in filtered_vacancies if get_kraj(v) == kraj]
    if typ_mzdy is not None:
        filtered_vacancies = [v for v in filtered_vacancies if v.typMzdy and v.typMzdy.id == typ_mzdy]
    if mzda_min is not None:
        filtered_vacancies = [v for v in filtered_vacancies if v.mesicniMzdaOd is not None and v.mesicniMzdaOd >= mzda_min]
    if profese is not None:
        filtered_vacancies = [v for v in filtered_vacancies if v.pozadovanaProfese and profese.lower() in v.pozadovanaProfese.cs.lower()]
    filtered_vacancies = filtered_vacancies[offset:offset+limit]
    return [summarize(v) for v in filtered_vacancies]

@app.get("/vacancies/{id:path}", response_model=PolozkyItem)
def get_vacancy(id: str):
    vacancy = next((v for v in vacancies if v.id == id), None)
    if vacancy is None:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    return vacancy