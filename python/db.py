import json
import ijson
from pathlib import Path
from time import time
from typing import Callable, Dict
import sqlite3
from fetch_data import fetch_data
from models import PolozkyItem
from tools import summarize

def prepare_sqlite(url: str, file_path: str, db_path: str, on_status: Callable[[str], None] | None = None):
    max_age_hours: int = 24
    if not Path(db_path).exists() or not Path(file_path).exists() or Path(file_path).stat().st_mtime < time() - max_age_hours * 3600:
        if on_status:
            on_status("downloading")
        fetch_data(url, file_path)
        fill_sqlite_from_json(file_path, db_path, on_status=on_status)

def fill_sqlite_from_json(file_path: str, db_path: str, on_status: Callable[[str], None] | None = None):
    if not Path(db_path).parent.exists():
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)    
    file_size = Path(file_path).stat().st_size
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS polozky")
    cursor.execute("CREATE TABLE IF NOT EXISTS polozky (id TEXT PRIMARY KEY, data TEXT, kraj TEXT, typ_mzdy TEXT, mesicni_mzda_od REAL, profese TEXT, zamestnavatel TEXT, datum_vlozeni TEXT, pocet_mist INTEGER)")
    with open(file_path, "rb") as f:
        for item in ijson.items(f, "polozky.item", use_float=True):
            pos = f.tell()
            if on_status:
                on_status(f"importing data into SQLite: {pos / file_size * 100:.2f}%")
            summarized_item = summarize(PolozkyItem(**item))
            profese_lower = summarized_item.profese.lower() if summarized_item.profese else None
            zamestnavatel_lower = summarized_item.zamestnavatel.lower() if summarized_item.zamestnavatel else None
            cursor.execute("INSERT OR REPLACE INTO polozky (id, data, kraj, typ_mzdy, mesicni_mzda_od, profese, zamestnavatel, datum_vlozeni, pocet_mist) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (item["id"], json.dumps(item), summarized_item.kraj, summarized_item.typ_mzdy, summarized_item.mesicni_mzda_od, profese_lower, zamestnavatel_lower, summarized_item.datum_vlozeni.isoformat(), summarized_item.pocet_mist))
    if on_status:
        on_status("creating indexes")
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