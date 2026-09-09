# volna-mista

[![CI](https://github.com/eMukator/volna-mista/actions/workflows/ci.yml/badge.svg)](https://github.com/eMukator/volna-mista/actions/workflows/ci.yml)
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/eMukator/volna-mista)

> **Cvičný projekt.** Vznikl jako praktické osvojení Pythonu a TypeScriptu na reálném příkladu (ne jako produkční aplikace) — backend v Pythonu stahuje a servíruje otevřená data MPSV o volných místech, frontend v TypeScriptu/Reactu nad tím dělá jednoduchý vyhledávač. Kód je záměrně jednoduchý a bez zbytečných abstrakcí; níže jsou ale přesné instrukce, pokud si ho chceš spustit, prozkoumat nebo v něm pokračovat.

Zdroj dat: [Volná místa za celou ČR](https://data.mpsv.cz/web/data/volna-mista-za-celou-cr) (otevřená data MPSV/Úřadu práce ČR, aktualizace 1×/den).

## Stack

- **Backend:** Python, FastAPI, pydantic (modely vygenerované z oficiálního JSON Schema)
- **Frontend:** TypeScript, React, Vite; typy API klienta generované z FastAPI OpenAPI schématu
- **Testy:** pytest (backend), vitest (frontend)
- **Prostředí:** Docker Compose + VS Code Dev Containers

## Vyzkoušet bez instalace

Klikni na odznak **"Open in GitHub Codespaces"** nahoře — otevře se prohlížečové VS Code se stejným devcontainerem, jaký používáme pro vývoj (viz níže "Vývoj"). Nic není potřeba instalovat lokálně.

## Požadavky (lokální spuštění)

- Docker Desktop
- VS Code + rozšíření **Dev Containers**

## Vývoj

1. Otevři složku projektu ve VS Code.
2. `Ctrl+Shift+P` → **"Dev Containers: Reopen in Container"**. Při prvním spuštění to chvíli trvá (staví se image, instaluje se Node feature, `pip install`). Tím se zároveň nastartuje i `web` kontejner (viz níže).
3. **API** si spouštíš ručně, v terminálu devcontaineru (v `python/`): `uvicorn api.main:app --reload --host 0.0.0.0 --port 8000`. Poslouchá na `localhost:8000`.
4. **Web/frontend** už běží — je to samostatná `web` služba z `docker-compose.yml` (`vite --host`, port 5173), startuje se automaticky s celým stackem a hot-reloaduje se sama. Neřeš ji v devcontaineru — `api` kontejner port 5173 ven vůbec nepublikuje, takže ruční `npm run dev` tam by nebylo z prohlížeče dostupné. Prostě edituj soubory v `client/`, změny se ti promítnou na `localhost:5173` samy.

API kontejner sám o sobě nic nespouští — jen má připravené závislosti a čeká, server si spouštíš ty ručně nebo přes debugger (viz níže). Nikdy nespouštěj dvě instance stejného serveru najednou — druhá spadne na "address already in use".

Změna v `requirements.txt`? Ručně `pip install -r requirements.txt` v terminálu API. Změna v `package.json`? `docker compose restart web` (přeinstaluje závislosti a restartuje Vite) — `web` container si `npm install` spouští jen při vlastním startu, ne za běhu.

### Bez VS Code (ověření mimo devcontainer)

```
docker compose up -d
```

Připraví oba kontejnery (nainstaluje závislosti) a nechá je čekat. Web (`localhost:5173`) se spustí automaticky. API je potřeba nastartovat ručně:

```
docker compose exec api uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Nepoužívej tenhle způsob současně s připojeným devcontainerem — obě cesty ovládají stejné kontejnery a navzájem si překáží.

## Debug (breakpointy)

1. Breakpoint nastavíš kliknutím do okraje vedle řádku nebo `F9`.
2. **Run and Debug** (`Ctrl+Shift+D`) → vyber konfiguraci → `F5`:
   - **"Python: aktuální soubor"** — pro samostatné skripty (`fetch_data.py`, `inventory.py`).
   - **"Python: FastAPI (bez reloadu)"** — spustí `uvicorn` pod debuggerem na portu 8000. Nesmí přitom běžet žádná jiná instance API serveru.
3. Request na endpoint (prohlížeč/curl) se zastaví na breakpointu, proměnné vidíš v panelu Variables.

## Testy

```
# backend, z python/
pytest tests/

# frontend, z client/
npm test
```

Testy neběží proti reálným MPSV datům — backend testy si data vyrábí ručně (`make_vacancy` factory v `python/tests/test_main.py`), frontend testy mockují `fetch`. Běží i v CI (viz badge nahoře) bez závislosti na síti.

## Data

- `python/fetch_data.py` — stáhne `volna-mista.json` z MPSV a nakešuje do `python/data/raw/` (podle stáří souboru, znovu stahuje jen když je cache starší než 24 h).
- `python/inventory.py` — projede stažená data a vypíše inventář číselníkových hodnot (kraje, typ mzdy, směnnost, ...).

Spouští se jako běžný Python skript v terminálu devcontaineru (`python fetch_data.py`).

## Struktura

```
python/
  api/main.py         FastAPI endpointy (/health, /vacancies, /vacancies/{id})
  models.py            pydantic modely vygenerované z JSON Schema
  fetch_data.py         stažení + cache dat
  inventory.py           inventář číselníkových hodnot
  tests/                  pytest testy
client/
  src/App.tsx          hlavní React komponenta (seznam, filtry, detail)
  src/api.ts             typovaný fetch klient
  src/codelists.ts         čitelné popisky pro kraje / typ mzdy
  src/types/api.d.ts        typy vygenerované z OpenAPI schématu
  src/api.test.ts          vitest testy
```

## Nasazení (produkce)

Produkční stack je oddělený od vývojového `docker-compose.yml` (ten zůstává jen pro devcontainer) a žije v [`deploy/`](deploy/):

- `python/Dockerfile` — produkční image API (bez `--reload`, `pip install` napevno v image).
- `client/Dockerfile` — vícefázový build: `npm run build` → statické soubory servíruje `nginx` na portu 5000 a `/api/*` proxuje na `api:8000` (stejné mapování jako Vite dev proxy v `vite.config.ts`).
- `deploy/docker-compose.yml` — dvě služby, `api` (interní) a `web` (veřejná, jediná s publikovaným portem 5000).
- `deploy/compose.miget.yaml` — overlay pro [Miget](https://miget.com/) (`x-miget: private: true` u `api`, aby nedostala vlastní veřejnou URL).

Ověřeno lokálně (`docker compose -f deploy/docker-compose.yml up`): `web` servíruje SPA i fallback na `index.html` pro deep-linky, `/api/health` a `/api/vacancies` fungují přes proxy.

### Nasazení na Miget + vlastní doména

1. Na [miget.com](https://miget.com/) založ účet/projekt a připoj tenhle GitHub repozitář jako **Compose Stack**. Jako cestu k souboru zadej `deploy` (podadresář, ne kořen repa) — Miget si v něm najde `docker-compose.yml` a automaticky přiloží `compose.miget.yaml`.
2. Miget nasadí obě služby; veřejně dostupná bude jen `web` (poslouchá na portu 5000, jak vyžaduje Migetův ingress), `api` zůstane interní a `web` se na ni doptává přes DNS jméno služby (`api:8000`) — stejně jako v devu.
3. V nastavení aplikace (**Settings → Domains**) přidej `volnamista.mago.cz`, u DNS providera pro `mago.cz` vytvoř TXT záznam pro ověření vlastnictví (hodnotu ukáže dashboard) a po ověření CNAME záznam `volnamista.mago.cz` → cílová hodnota z dashboardu. Miget pak sám vystaví TLS certifikát.
4. Každý push do `main` spustí nový produkční deploy.

Poznámka: `api` po každém startu znovu stahuje `volna-mista.json` z MPSV (~180 MB, řádově desítky sekund) — po dobu startu vrací `web` na `/api/*` 502, než kontejner naběhne. Trvalé úložiště cache není zavedené (viz níže).

## Co chybí / kam dál

- Filtry na `kraj`/`typ mzdy` mají popisky natvrdo (14 krajů, 2 typy mzdy — stabilní, oficiální číselníky z data.mpsv.cz). Ostatní číselníky (CZ-ISCO profese, vzdělání...) čitelné popisky nemají.
- Žádné trvalé úložiště — data se validují a drží v paměti procesu, po restartu API se načtou znovu (viz startup cena výše).
