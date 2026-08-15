import type { components } from './types/api'
export type VacancySummary = components['schemas']['VacancySummary']
export type Vacancy = components['schemas']['PolozkyItem']

export type VacancyFilters = {
  profese?: string
  kraj?: string
  typ_mzdy?: string
  mzda_min?: number,
  offset?: number,
  limit?: number
}

export async function fetchVacancies(filters: VacancyFilters = {}): Promise<VacancySummary[]> {
  const params = new URLSearchParams()
  if (filters.profese)
    params.set('profese', filters.profese)
  if (filters.kraj)
    params.set('kraj', filters.kraj)
  if (filters.typ_mzdy)
    params.set('typ_mzdy', filters.typ_mzdy)
  if (filters.mzda_min != null)
    params.set('mzda_min', filters.mzda_min.toString())

  if (filters.offset != null)
    params.set('offset', filters.offset.toString())
  if (filters.limit != null)
    params.set('limit', filters.limit.toString())

  const response = await fetch(`/api/vacancies?${params}`)
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  const data = await response.json()
  return data as VacancySummary[]
}

export async function fetchVacancyById(id: string): Promise<Vacancy> {
  const response = await fetch(`/api/vacancies/${id}`)
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  const data = await response.json()
  return data as Vacancy
}