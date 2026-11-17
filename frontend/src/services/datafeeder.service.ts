export type DatafeederInstance = {
  name: string
  url: string
}

export type DatafeederIntegrityLink = {
  metadataUuid: string
  datafeederId: string
  instance: string
  status: string
}

// Temporary frontend mock for the API contract planned in GSMEL-1349.
// Replace these methods with Maelstro backend calls once they are available.
const mockInstances: DatafeederInstance[] = [
  {
    name: 'Local Datafeeder',
    url: '/datafeeder-backend',
  },
]

export const datafeederService = {
  async getInstances(): Promise<DatafeederInstance[]> {
    return Promise.resolve(mockInstances)
  },

  async findByMetadataUuid(metadataUuid: string): Promise<DatafeederIntegrityLink | null> {
    if (!metadataUuid || metadataUuid.startsWith('missing-')) {
      return Promise.resolve(null)
    }

    return Promise.resolve({
      metadataUuid,
      datafeederId: `mock-${metadataUuid}`,
      instance: mockInstances[0].name,
      status: 'available',
    })
  },
}
