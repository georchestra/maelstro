import type { LogDetail } from './logs.service'

export type SynchronizeParams = {
  src_name: string
  dst_name: string
  metadataUuid: string
  copy_meta: boolean
  copy_layers: boolean
  copy_styles: boolean
  dry_run: boolean
}

export type InvolvedMetadata = {
  title: string
}

export type InvolvedGeonetwork = {
  src: string
  dst: string
  metadata: InvolvedMetadata[]
}

export type InvolvedGeoserver = {
  src: string
  dst: string
  layers: string[]
  styles: string[]
}

export type InvolvedResources = {
  metadata: InvolvedGeonetwork[]
  data: InvolvedGeoserver[]
}

function toSynchronizeParams(params: SynchronizeParams): URLSearchParams {
  const stringParams: Record<string, string> = Object.fromEntries(
    Object.entries(params).map(([key, value]) => [key, String(value)]),
  )
  return new URLSearchParams(stringParams)
}

export const synchronizeService = {
  async getInvolvedResources(params: SynchronizeParams): Promise<InvolvedResources> {
    const response = await fetch(
      '/maelstro-backend/involved_resources?' + toSynchronizeParams(params),
      {
        method: 'GET',
      },
    )
    return await response.json()
  },

  async synchronize(params: SynchronizeParams): Promise<LogDetail[]> {
    const response = await fetch('/maelstro-backend/copy?' + toSynchronizeParams(params), {
      method: 'PUT',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
    })
    return await response.json()
  },
}
