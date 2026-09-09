import json
from pathlib import Path
from time import time
from typing import Dict
import sqlite3
from fetch_data import fetch_data
from models import PolozkyItem
from tools import summarize

def prepare_sqlite(url: str, file_path: str, db_path: str):
    max_age_hours: int = 24
    if not Path(db_path).exists() or not Path(file_path).exists() or Path(file_path).stat().st_mtime < time() - max_age_hours * 3600:
        fetch_data(url, file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            fill_sqlite_from_json(json.load(f), db_path)

def fill_sqlite_from_json(json_data: Dict, db_path: str):
    if not Path(db_path).parent.exists():
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)    

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS polozky")
    cursor.execute("CREATE TABLE IF NOT EXISTS polozky (id TEXT PRIMARY KEY, data TEXT, kraj TEXT, typ_mzdy TEXT, mesicni_mzda_od REAL, profese TEXT, zamestnavatel TEXT, datum_vlozeni TEXT, pocet_mist INTEGER)")
    for item in json_data.get("polozky", []):
        summarized_item = summarize(PolozkyItem(**item))
        profese_lower = summarized_item.profese.lower() if summarized_item.profese else None
        zamestnavatel_lower = summarized_item.zamestnavatel.lower() if summarized_item.zamestnavatel else None
        cursor.execute("INSERT OR REPLACE INTO polozky (id, data, kraj, typ_mzdy, mesicni_mzda_od, profese, zamestnavatel, datum_vlozeni, pocet_mist) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (item["id"], json.dumps(item), summarized_item.kraj, summarized_item.typ_mzdy, summarized_item.mesicni_mzda_od, profese_lower, zamestnavatel_lower, summarized_item.datum_vlozeni.isoformat(), summarized_item.pocet_mist))
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_kraj ON polozky (kraj)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_typ_mzdy ON polozky (typ_mzdy)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_mesicni_mzda_od ON polozky (mesicni_mzda_od)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_profese ON polozky (profese)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_zamestnavatel ON polozky (zamestnavatel)")
    conn.commit()
    conn.close()

def query(db_path: str, sql, params=()):
    with sqlite3.connect(db_path) as con:
        cur = con.execute(sql, params)
        return cur.fetchall()