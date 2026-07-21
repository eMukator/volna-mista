import json
from pathlib import Path
from time import time
from typing import Dict
import httpx

def fetch_data(url: str, file_path: str):
    chunk_size: int = 8192
    if not Path(file_path).parent.exists():
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)    
    with httpx.stream("GET", url) as r:
        with open(file_path, "wb") as f:
            for data in r.iter_bytes(chunk_size):
                f.write(data)

def get_cached_data(url: str, file_path: str) -> Dict:
    max_age_hours: int = 24
    if not Path(file_path).exists() or Path(file_path).stat().st_mtime < time() - max_age_hours * 3600:
        fetch_data(url, file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    json_data = get_cached_data("https://data.mpsv.cz/od/soubory/volna-mista/volna-mista.json", Path(__file__).parent / "data/raw/volna-mista.json")
    print(len(json_data["polozky"]))

if __name__ == "__main__":
    main()