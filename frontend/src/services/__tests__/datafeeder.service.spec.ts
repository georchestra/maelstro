import { beforeEach, describe, expect, it, vi } from 'vitest'
import { datafeederService } from '../datafeeder.service'

describe('datafeederService', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('returns the real Datafeeder availability for the selected source and UUID', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(
        JSON.stringify({
          configured: true,
          found: true,
          integrity_link_id: 'integrity-link-id',
        }),
        { status: 200 },
      ),
    )

    await expect(
      datafeederService.findByMetadataUuid('local source', 'metadata uuid'),
    ).resolves.toEqual({
      configured: true,
      found: true,
      integrity_link_id: 'integrity-link-id',
    })
    expect(fetchMock).toHaveBeenCalledWith(
      '/maelstro-backend/sources/local%20source/datafeeder/metadata%20uuid',
    )
  })

  it('returns null when the dataset is not managed by Datafeeder', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(
        JSON.stringify({ configured: true, found: false, integrity_link_id: null }),
        { status: 200 },
      ),
    )

    await expect(
      datafeederService.findByMetadataUuid('source', 'missing-metadata-uuid'),
    ).resolves.toBeNull()
  })

  it('rejects failed backend lookups', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(null, { status: 502 }))

    await expect(datafeederService.findByMetadataUuid('source', 'metadata-uuid')).rejects.toThrow(
      'Datafeeder lookup failed with HTTP 502',
    )
  })
})
