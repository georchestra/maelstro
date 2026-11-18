export type DatafeederIntegrityLink = {
  configured: boolean
  found: boolean
  integrity_link_id: string | null
}

export const datafeederService = {
  async findByMetadataUuid(
    sourceName: string,
    metadataUuid: string,
  ): Promise<DatafeederIntegrityLink | null> {
    const response = await fetch(
      `/maelstro-backend/sources/${encodeURIComponent(sourceName)}/datafeeder/${encodeURIComponent(metadataUuid)}`,
    )
    if (!response.ok) {
      throw new Error(`Datafeeder lookup failed with HTTP ${response.status}`)
    }

    const availability = (await response.json()) as DatafeederIntegrityLink
    return availability.found ? availability : null
  },
}
