from pathlib import Path
from fetch_data import get_cached_data
from models import VolnaMista

def main():
    json_data = get_cached_data("https://data.mpsv.cz/od/soubory/volna-mista/volna-mista.json", Path(__file__).parent / "data/raw/volna-mista.json")
    volna_mista = VolnaMista(**json_data)

    ids = set()
    typMzdy_ids = set()
    smennost_ids = set()
    minPozadovaneVzdelani_ids = set()
    profeseCzIsco_ids = set()
    zverejnovat_ids = set()
    pracovnePravniVztahy_ids = set()
    kraj_ids = set()

    for p in volna_mista.polozky:

        ids.add(p.id)

        if (typMzdy := p.typMzdy) is not None and typMzdy.id is not None:
            typMzdy_ids.add(p.typMzdy.id)

        if (smennost := p.smennost) is not None and smennost.id is not None:
            smennost_ids.add(p.smennost.id)

        if (minPozadovaneVzdelani := p.minPozadovaneVzdelani) is not None and minPozadovaneVzdelani.id is not None:
            minPozadovaneVzdelani_ids.add(p.minPozadovaneVzdelani.id)

        if (profeseCzIsco := p.profeseCzIsco) is not None and profeseCzIsco.id is not None:
            profeseCzIsco_ids.add(p.profeseCzIsco.id)

        if (zverejnovat := p.zverejnovat) is not None and zverejnovat.id is not None:
            zverejnovat_ids.add(p.zverejnovat.id)

        if (pracovnePravniVztahy := p.pracovnePravniVztahy) is not None:
            for pracovni_vztah in pracovnePravniVztahy:
                if pracovni_vztah.id is not None:
                    pracovnePravniVztahy_ids.add(pracovni_vztah.id)

        if p.mistoVykonuPrace and p.mistoVykonuPrace.pracoviste:
            for pracoviste in p.mistoVykonuPrace.pracoviste:
                if pracoviste.adresa and pracoviste.adresa.kraj:
                    kraj_ids.add(pracoviste.adresa.kraj.id)

    print(f"polozek: {len(volna_mista.polozky)}", f"ids: {len(ids)}")

    show_info("typMzdy_ids", typMzdy_ids)
    show_info("smennost_ids", smennost_ids)
    show_info("minPozadovaneVzdelani_ids", minPozadovaneVzdelani_ids)
    # show_info("profeseCzIsco_ids", profeseCzIsco_ids)
    show_info("zverejnovat_ids", zverejnovat_ids)
    show_info("pracovnePravniVztahy_ids", pracovnePravniVztahy_ids)
    show_info("kraj_ids", kraj_ids)

def show_info(name, ids):
    print(f"{name}: {len(ids)}")
    for item in sorted(ids):
        print(item)
    print()

if __name__ == "__main__":
    main()