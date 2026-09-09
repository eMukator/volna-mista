from models import PolozkyItem
from api.main import get_filtered_vacancies
from db import fill_sqlite_from_json
from tools import get_kraj

def make_vacancy(**overrides) -> PolozkyItem:
    data = {
        "id": "VolneMisto/1",
        "referencniCislo": "123",
        "azylant": False,
        "cizinecMimoEu": False,
        "datumVlozeni": "2026-01-01T00:00:00Z",
        "datumZmeny": "2026-01-01T00:00:00Z",
        "pocetMist": 1,
        "pozadovanaProfese": {"cs": "Test"},
        "statniSpravaSamosprava": False,
        "terminZahajeniPracovnihoPomeru": "2026-01-01",
        "souhlasAgenturyAgentura": False,
        "souhlasAgenturyUzivatel": False,
        "zverejnovat": {"id": "ZverejnovatVpm/ano"},
        "mistoVykonuPrace": None,
        "zamestnavatel": None,
        "profeseCzIsco": {"id": "CzIsco/1"},
        "pracovnePravniVztahy": [],
        "kontaktniPracoviste": {"id": "KontaktniPracoviste/X"},
        "portalId": 1,
        "modraKarta": False,
        "zamestnaneckaKarta": False,        
    }
    data.update(overrides)
    return PolozkyItem(**data)

def test_get_kraj_returns_none_when_misto_vykonu_prace_missing():
    vacancy = make_vacancy(mistoVykonuPrace=None)
    assert get_kraj(vacancy) is None

def test_get_kraj_returns_none_when_no_pracoviste():
    vacancy = make_vacancy(mistoVykonuPrace={"pracoviste": []})
    assert get_kraj(vacancy) is None

def test_get_kraj_returns_kraj_id_when_present():
    vacancy = make_vacancy(mistoVykonuPrace={"pracoviste": [{"adresa": {"kraj": {"id": "Kraj/1"}}, "nazev": "Test"}]})
    assert get_kraj(vacancy) == "Kraj/1"

def test_get_filtered_vacancies_filters_by_kraj(tmp_path):
    filtered_vacancies: list[PolozkyItem] = []
    vacancy1 = make_vacancy(id="1", mistoVykonuPrace={"pracoviste": [{"adresa": {"kraj": {"id": "Kraj/1"}}, "nazev": "Test1"}]})
    vacancy2 = make_vacancy(id="2", mistoVykonuPrace={"pracoviste": [{"adresa": {"kraj": {"id": "Kraj/2"}}, "nazev": "Test2"}]})
    fill_sqlite_from_json({"polozky": [vacancy1.model_dump(mode="json"), vacancy2.model_dump(mode="json")]}, tmp_path / "test.db")
    filtered_vacancies.extend([vacancy1, vacancy2])
    filtered = get_filtered_vacancies(tmp_path / "test.db", offset=0, limit=10, kraj="Kraj/1", typ_mzdy=None, mzda_min=None, profese=None)
    assert len(filtered) == 1
    assert filtered[0].id == "1"

def test_get_filtered_vacancies_filters_by_typ_mzdy(tmp_path):
    vacancy1 = make_vacancy(id="1", typMzdy={"id": "TypMzdy/mesic"})
    vacancy2 = make_vacancy(id="2", typMzdy={"id": "TypMzdy/hod"})
    fill_sqlite_from_json({"polozky": [vacancy1.model_dump(mode="json"), vacancy2.model_dump(mode="json")]}, tmp_path / "test.db")
    filtered = get_filtered_vacancies(tmp_path / "test.db", offset=0, limit=10, kraj=None, typ_mzdy="TypMzdy/mesic", mzda_min=None, profese=None)
    assert len(filtered) == 1
    assert filtered[0].id == "1"

def test_get_filtered_vacancies_filters_by_mzda_min_and_ignores_none(tmp_path):
    vacancy1 = make_vacancy(id="1", mesicniMzdaOd=30000)
    vacancy2 = make_vacancy(id="2", mesicniMzdaOd=20000)
    vacancy3 = make_vacancy(id="3", mesicniMzdaOd=None)
    fill_sqlite_from_json({"polozky": [vacancy1.model_dump(mode="json"), vacancy2.model_dump(mode="json"), vacancy3.model_dump(mode="json")]}, tmp_path / "test.db")
    filtered = get_filtered_vacancies(tmp_path / "test.db", offset=0, limit=10, kraj=None, typ_mzdy=None, mzda_min=25000, profese=None)
    assert len(filtered) == 1
    assert filtered[0].id == "1"

def test_get_filtered_vacancies_filters_by_profese_case_insensitive_substring(tmp_path):
    vacancy1 = make_vacancy(id="1", pozadovanaProfese={"cs": "Pomocný kuchař".lower()})
    vacancy2 = make_vacancy(id="2", pozadovanaProfese={"cs": "Prodavač".lower()})
    fill_sqlite_from_json({"polozky": [vacancy1.model_dump(mode="json"), vacancy2.model_dump(mode="json")]}, tmp_path / "test.db")
    filtered = get_filtered_vacancies(tmp_path / "test.db", offset=0, limit=10, kraj=None, typ_mzdy=None, mzda_min=None, profese="KUCHAŘ")
    assert len(filtered) == 1
    assert filtered[0].id == "1"

def test_get_filtered_vacancies_paginates_with_offset_and_limit(tmp_path):
    vacancies = [make_vacancy(id=str(i)) for i in range(5)]
    fill_sqlite_from_json({"polozky": [vacancy.model_dump(mode="json") for vacancy in vacancies]}, tmp_path / "test.db")
    filtered = get_filtered_vacancies(tmp_path / "test.db", offset=2, limit=2, kraj=None, typ_mzdy=None, mzda_min=None, profese=None)
    assert [v.id for v in filtered] == ["2", "3"]

def test_get_filtered_vacancies_combines_filters_with_and(tmp_path):
    vacancy1 = make_vacancy(id="1", typMzdy={"id": "TypMzdy/mesic"}, mesicniMzdaOd=30000)
    vacancy2 = make_vacancy(id="2", typMzdy={"id": "TypMzdy/mesic"}, mesicniMzdaOd=10000)
    vacancy3 = make_vacancy(id="3", typMzdy={"id": "TypMzdy/hod"}, mesicniMzdaOd=30000)
    fill_sqlite_from_json({"polozky": [vacancy1.model_dump(mode="json"), vacancy2.model_dump(mode="json"), vacancy3.model_dump(mode="json")]}, tmp_path / "test.db")
    filtered = get_filtered_vacancies(tmp_path / "test.db", offset=0, limit=10, kraj=None, typ_mzdy="TypMzdy/mesic", mzda_min=20000, profese=None)
    assert len(filtered) == 1
    assert filtered[0].id == "1"

def test_get_filtered_vacancies_returns_all_when_no_filters(tmp_path):
    vacancies = [make_vacancy(id=str(i)) for i in range(3)]
    fill_sqlite_from_json({"polozky": [vacancy.model_dump(mode="json") for vacancy in vacancies]}, tmp_path / "test.db")
    filtered = get_filtered_vacancies(tmp_path / "test.db", offset=0, limit=10, kraj=None, typ_mzdy=None, mzda_min=None, profese=None)
    assert len(filtered) == 3