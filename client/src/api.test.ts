import { describe, it, expect, vi, beforeEach } from 'vitest'
import { fetchVacancies, fetchVacancyById } from './api'

describe('fetchVacancies', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })


  it('builds query string from filters', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => [],
    } as Response)

    await fetchVacancies({ profese: 'kuchař', mzda_min: 20000 })

    const calledUrl = vi.mocked(fetch).mock.calls[0][0] as string
    expect(calledUrl).toContain('profese=ku')
    expect(calledUrl).toContain('mzda_min=20000')
  })


  it('undefined filters are not included in query string', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => [],
    } as Response)

    await fetchVacancies({ profese: undefined, mzda_min: undefined })

    const calledUrl = vi.mocked(fetch).mock.calls[0][0] as string
    expect(calledUrl).not.toContain('profese=')
    expect(calledUrl).not.toContain('mzda_min')
  })


  it('fetchVacancies throws error on non-ok response', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: false,
      status: 500,
      json: async () => ({}),
    } as Response)

    await expect(fetchVacancies({})).rejects.toThrow('500')
  })

  it('fetchVacancyById not change id with slash', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => ({}),
    } as Response)

    await fetchVacancyById('VolnaMista/123')

    const calledUrl = vi.mocked(fetch).mock.calls[0][0] as string
    expect(calledUrl).toContain('VolnaMista/123')
  })

})