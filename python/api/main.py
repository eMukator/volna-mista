import json

from fastapi import FastAPI, HTTPException
from pathlib import Path
from contextlib import asynccontextmanager
from models import PolozkyItem
from api.schemas import VacancySummary
from db import prepare_sqlite, query
from tools import summarize

# vacancies: list[PolozkyItem] = []
db_path:str = Path(__file__).parent.parent / "data/db/volna-mista.db"

@asynccontextmanager
async def lifespan(app: FastAPI):
    prepare_sqlite("https://data.mpsv.cz/od/soubory/volna-mista/volna-mista.json", Path(__file__).parent.parent / "data/raw/volna-mista.json", db_path)
    yield
    

def get_filtered_vacancies(db_path: str, offset: int, limit: int, kraj: str | None, typ_mzdy: str | None, mzda_min: float | None, profese: str | None) -> list[VacancySummary]:
    query_str = "SELECT data FROM polozky"
    where_str = ""
    params = []
    if kraj is not None:
        where_str += "kraj = ?"
        params.append(kraj)
    if typ_mzdy is not None:
        if where_str:
            where_str += " AND "
        where_str += "typ_mzdy = ?"
        params.append(typ_mzdy)
    if mzda_min is not None:
        if where_str:
            where_str += " AND "
        where_str += "mesicni_mzda_od >= ?"
        params.append(mzda_min)
    if profese is not None:
        if where_str:
            where_str += " AND "
        where_str += "profese LIKE '%' || ? || '%'"
        params.append(profese.lower())

    if where_str:
        where_str = " WHERE " + where_str
    query_str += where_str
    query_str += f" LIMIT {limit} OFFSET {offset}"
    results = query(db_path, query_str, params)

    return [summarize(PolozkyItem(**json.loads(row[0]))) for row in results]

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
    return get_filtered_vacancies(db_path, offset, limit, kraj, typ_mzdy, mzda_min, profese)

@app.get("/vacancies/{id:path}", response_model=PolozkyItem)
def get_vacancy(id: str):
    results = query(db_path, "SELECT data FROM polozky WHERE id = ?", [id])
    if not results:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    return PolozkyItem(**json.loads(results[0][0]))