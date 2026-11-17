import { describe, expect, it } from 'vitest'
import { datafeederService } from '../datafeeder.service'

describe('datafeederService mock', () => {
  it('returns a configured mock instance', async () => {
    await expect(datafeederService.getInstances()).resolves.toEqual([
      {
        name: 'Local Datafeeder',
        url: '/datafeeder-backend',
      },
    ])
  })

  it('returns a preview link for a known metadata UUID', async () => {
    await expect(datafeederService.findByMetadataUuid('metadata-uuid')).resolves.toMatchObject({
      metadataUuid: 'metadata-uuid',
      instance: 'Local Datafeeder',
      status: 'available',
    })
  })

  it('simulates a missing Datafeeder entry', async () => {
    await expect(datafeederService.findByMetadataUuid('missing-metadata-uuid')).resolves.toBeNull()
  })
})
