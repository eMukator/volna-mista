import { useEffect, useState } from 'react'
import { fetchVacancies, type VacancySummary } from './api';

function App() {

  const [error, setError] = useState<string | null>(null)
  const [vacancies, setVacancies] = useState<VacancySummary[]>([]);

  const getVacancies = async() => {
    try {
      const response = await fetchVacancies();
      setVacancies(response);
    }
    catch (error) {
      setError(error instanceof Error ? error.message : 'Nepodařilo se načíst data')
    }
  }

  useEffect(() => {
    getVacancies();
  }, []);

  return (
    <>
      {error && <p>{error}</p>}
      <ul>
        {vacancies.map((vacancy) => (
          <li key={vacancy.id}>{vacancy.profese} / {vacancy.zamestnavatel} / {vacancy.mesicni_mzda_od} - {vacancy.mesicni_mzda_do} / {vacancy.kraj}</li>
        ))}
      </ul>
    </>
  )
}

export default App
