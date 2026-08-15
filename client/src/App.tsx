import { useEffect, useRef, useState } from 'react'
import { fetchVacancies, fetchVacancyById, type Vacancy, type VacancySummary } from './api';
import { KRAJ_LABELS, TYP_MZDY_LABELS } from './codelists'

function VacancyDetail({ vacancy, onClose }: { vacancy: Vacancy; onClose: () => void }) {
  const krajId = vacancy.mistoVykonuPrace?.pracoviste?.[0]?.adresa?.kraj?.id
  const kontakt = vacancy.prvniKontaktSeZamestnavatelem?.komuSeHlasit
  const kontaktJmeno = [kontakt?.jmeno, kontakt?.prijmeni].filter(Boolean).join(' ')

  return (
    <>
      <h2>{vacancy.pozadovanaProfese?.cs}</h2>
      <dl>
        <dt>Zaměstnavatel:</dt>
          <dd>{vacancy.zamestnavatel?.nazev ?? '—'}</dd>
        <dt>Pracoviště:</dt>
          <dd>{vacancy.mistoVykonuPrace?.pracoviste?.[0]?.nazev ?? '—'}</dd>
        <dt>Kraj:</dt>
          <dd>{krajId ? (KRAJ_LABELS[krajId] ?? krajId) : '—'}</dd>
        <dt>Typ mzdy:</dt>
          <dd>{vacancy.typMzdy ? (TYP_MZDY_LABELS[vacancy.typMzdy.id] ?? vacancy.typMzdy.id) : '—'}</dd>
        <dt>Měsíční mzda od:</dt>
          <dd>{vacancy.mesicniMzdaOd ?? '—'}</dd>
        <dt>Měsíční mzda do:</dt>
          <dd>{vacancy.mesicniMzdaDo ?? '—'}</dd>
        <dt>Počet míst:</dt>
          <dd>{vacancy.pocetMist}</dd>
        <dt>Nástup od:</dt>
          <dd>{new Date(vacancy.terminZahajeniPracovnihoPomeru).toLocaleDateString('cs-CZ')}</dd>
        <dt>Vloženo:</dt>
          <dd>{new Date(vacancy.datumVlozeni).toLocaleDateString('cs-CZ')}</dd>
        <dt>Typ úvazku:</dt>
          <dd>{vacancy.pracovnePravniVztahy?.map((v) => v.id).join(', ') || '—'}</dd>
        {vacancy.upresnujiciInformace?.cs && (
          <>
            <dt>Popis:</dt>
              <dd className="detail-description">{vacancy.upresnujiciInformace.cs}</dd>
          </>
        )}
        {kontakt && (
          <>
            <dt>Kontakt:</dt>
              <dd>
                {kontaktJmeno}
                {kontakt.email && <> · {kontakt.email}</>}
                {kontakt.telefon && <> · {kontakt.telefon}</>}
              </dd>
          </>
        )}
      </dl>
      <button type="button" onClick={onClose}>Zavřít</button>
    </>
  )
}

function App() {

  const [error, setError] = useState<string | null>(null)
  const [vacancies, setVacancies] = useState<VacancySummary[]>([]);
  const [vacancy, setVacancy] = useState<Vacancy | null>(null);

  const [profese, setProfese] = useState('')
  const [kraj, setKraj] = useState('')
  const [typMzdy, setTypMzdy] = useState('')
  const [mzdaMin, setMzdaMin] = useState('')
  const [offset, setOffset] = useState(0)
  const limit = 20

  const dialogRef = useRef<HTMLDialogElement>(null)

  const getVacancies = async(currentOffset?: number) => {
    try {
      const response = await fetchVacancies({ profese, kraj, typ_mzdy: typMzdy, mzda_min: mzdaMin ? parseFloat(mzdaMin) : undefined, offset: currentOffset ?? offset, limit });
      setVacancies(response);
      setError(null);
    }
    catch (error) {
      setError(error instanceof Error ? error.message : 'Nepodařilo se načíst data')
    }
  }

  const getVacancy = async (id: string) => {
    try {
      const response = await fetchVacancyById(id);
      setVacancy(response);
      setError(null);
      return response;
    }
    catch (error) {
      setVacancy(null);
      setError(error instanceof Error ? error.message : 'Nepodařilo se načíst detail');
      return null;
    }
  }

  useEffect(() => {
    getVacancies(0);
  }, []);

  useEffect(() => {
    if (vacancy)
      dialogRef.current?.showModal()
    else
      dialogRef.current?.close()
  }, [vacancy]);

  return (
    <div className="page">
      <h1>Seznam volných pracovních míst</h1>

      <form className="filters" onSubmit={(e) => { e.preventDefault(); setOffset(0); getVacancies(0); }}>
        <input type="text" placeholder="profese" value={profese} onChange={(e) => setProfese(e.target.value)} />
        <select value={kraj} onChange={(e) => setKraj(e.target.value)}>
          <option value="">Všechny kraje</option>
          {Object.entries(KRAJ_LABELS).map(([id, label]) => (
            <option key={id} value={id}>{label}</option>
          ))}
        </select>
        <select value={typMzdy} onChange={(e) => setTypMzdy(e.target.value)}>
          <option value="">Všechny typy mzdy</option>
          {Object.entries(TYP_MZDY_LABELS).map(([id, label]) => (
            <option key={id} value={id}>{label}</option>
          ))}
        </select>
        <input type="number" placeholder="min mzda" value={mzdaMin} onChange={(e) => setMzdaMin(e.target.value)} />
        <button type="submit">Hledat</button>
      </form>

      {error && <p className="error">{error}</p>}

      <ul className="vacancy-list">
        {vacancies.map((vacancy) => (
          <li key={vacancy.id}>
            <button type="button" className="vacancy-card" onClick={() => getVacancy(vacancy.id)}>
              <span className="vacancy-profese">{vacancy.profese}</span>
              <span className="vacancy-meta">{vacancy.zamestnavatel ?? 'Zaměstnavatel neuveden'} {vacancy.kraj && (' — ' + (KRAJ_LABELS[vacancy.kraj] ?? vacancy.kraj))}</span>
              <span className="vacancy-mzda">{vacancy.mesicni_mzda_od ?? '?'} – {vacancy.mesicni_mzda_do ?? '?'} Kč</span>
            </button>
          </li>
        ))}
      </ul>

      <div className="pagination">
        <button type="button" onClick={() => { setOffset(offset - limit); getVacancies(offset - limit); }} disabled={offset === 0}>Předchozí</button>
        <span>Stránka {offset / limit + 1}</span>
        <button type="button" onClick={() => { setOffset(offset + limit); getVacancies(offset + limit); }} disabled={vacancies.length < limit}>Další</button>
      </div>

      <dialog ref={dialogRef} className="detail" onClose={() => setVacancy(null)}>
        {vacancy && <VacancyDetail vacancy={vacancy} onClose={() => dialogRef.current?.close()} />}
      </dialog>
    </div>
  )
}

export default App
