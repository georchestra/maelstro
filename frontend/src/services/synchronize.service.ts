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

export type CopyPreviewMetadata = {
  title: string
}

export type CopyPreviewGeonetwork = {
  src: string
  dst: string
  metadata: CopyPreviewMetadata[]
}

export type CopyPreviewGeoserver = {
  src: string
  dst: string
  layers: string[]
  styles: string[]
}

export type CopyPreview = {
  geonetwork_resources?: CopyPreviewGeonetwork[]
  geoserver_resources?: CopyPreviewGeoserver[]
  info?: {[k: string]: string}
  operations?: LogDetail[]
}

export type CopyResponse = {
  info:  {[k: string]: string}
  operations: LogDetail[]
}

function toSynchronizeParams(params: SynchronizeParams): URLSearchParams {
  const stringParams: Record<string, string> = Object.fromEntries(
    Object.entries(params).map(([key, value]) => [key, String(value)]),
  )
  return new URLSearchParams(stringParams)
}

export const synchronizeService = {
  async getCopyPreview(params: SynchronizeParams): Promise<CopyPreview> {
    const response = await fetch('/maelstro-backend/copy_preview?' + toSynchronizeParams(params), {
      method: 'GET',
    })
    return await response.json()
  },

  async synchronize(params: SynchronizeParams): Promise<CopyResponse> {
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
