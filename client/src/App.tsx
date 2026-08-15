import { useEffect, useState } from 'react'
import { fetchVacancies, fetchVacancyById, type Vacancy, type VacancySummary } from './api';

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

  return (
    <>
      <h1>Seznam volných pracovních míst</h1>
      <div>
        filtry:
        <form onSubmit={(e) => { e.preventDefault(); setOffset(0); getVacancies(0); }}>
          <input type="text" placeholder="profese" value={profese} onChange={(e) => setProfese(e.target.value)} />
          <input type="text" placeholder="kraj" value={kraj} onChange={(e) => setKraj(e.target.value)} />
          <input type="text" placeholder="typ mzdy" value={typMzdy} onChange={(e) => setTypMzdy(e.target.value)} />
          <input type="number" placeholder="min mzda" value={mzdaMin} onChange={(e) => setMzdaMin(e.target.value)} />
          <button type="submit">Hledat</button>
        </form>
      </div>
      {error && <p>{error}</p>}
      <div>
        <ul>
          {vacancies.map((vacancy) => (
            <li key={vacancy.id}>
              <a href="#" onClick={(e) => { e.preventDefault(); getVacancy(vacancy.id); }}>
                {vacancy.profese} / {vacancy.zamestnavatel} / {vacancy.mesicni_mzda_od} - {vacancy.mesicni_mzda_do} / {vacancy.kraj}
              </a>
            </li>
          ))}
        </ul>
        <button onClick={() => { setOffset(offset - limit); getVacancies(offset - limit); }} disabled={offset === 0}>Předchozí</button>
        <span>Aktuální offset: {offset}</span>
        <button onClick={() => { setOffset(offset + limit); getVacancies(offset + limit); }} disabled={vacancies.length < limit}>Další</button>
      </div>
      {vacancy && (
        <div>
          <h2>Detail volného pracovního místa</h2>
          <dl>
            <dt>Profese:</dt>
              <dd>{vacancy.pozadovanaProfese?.cs}</dd>
            <dt>Zaměstnavatel:</dt>
              <dd>{vacancy.zamestnavatel?.nazev}</dd>
            <dt>Typ mzdy:</dt>
              <dd>{vacancy.typMzdy?.id}</dd>
            <dt>Měsíční mzda od:</dt>
              <dd>{vacancy.mesicniMzdaOd}</dd>
            <dt>Měsíční mzda do:</dt>
              <dd>{vacancy.mesicniMzdaDo}</dd>
          </dl>
          <button onClick={() => setVacancy(null)}>Zavřít detail</button>
        </div>
      )}
    </>
  )
}

export default App
