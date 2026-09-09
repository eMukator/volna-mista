from api.schemas import VacancySummary
from models import PolozkyItem

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