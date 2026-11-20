import { beforeEach, describe, expect, it, vi } from 'vitest'
import { synchronizeService, type SynchronizeParams } from '../synchronize.service'

const params: SynchronizeParams = {
  src_name: 'source',
  dst_name: 'destination',
  metadataUuid: 'metadata-uuid',
  copy_meta: true,
  copy_layers: true,
  copy_styles: true,
  copy_data: true,
  dry_run: false,
}

describe('synchronizeService', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('marks a successful synchronization response', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ summary: 'done', operations: [] }), { status: 200 }),
    )

    await expect(synchronizeService.synchronize(params)).resolves.toMatchObject({
      summary: 'done',
      successful: true,
      status_code: 200,
    })
  })

  it('preserves backend details for a failed synchronization', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(
        JSON.stringify({
          summary: 'MaelstroException',
          info: { err: 'Target table is already used' },
          operations: [],
        }),
        { status: 400 },
      ),
    )

    await expect(synchronizeService.synchronize(params)).resolves.toMatchObject({
      summary: 'MaelstroException',
      info: { err: 'Target table is already used' },
      successful: false,
      status_code: 400,
    })
  })
})
