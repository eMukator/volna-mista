import type { components } from './types/api'
export type VacancySummary = components['schemas']['VacancySummary']

export async function fetchVacancies(): Promise<VacancySummary[]> {
  const response = await fetch('/api/vacancies')
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  const data = await response.json()
  return data as VacancySummary[]
}
