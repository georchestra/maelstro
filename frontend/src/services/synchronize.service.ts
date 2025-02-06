export type SynchronizeParams = {
  src_name: string
  dst_name: string
  metadataUuid: string
  copy_meta: boolean
  copy_layers: boolean
  copy_styles: boolean
  dry_run: boolean
}

export type Log = {
  operation: string
  url: string
  context: string
  service_type: string
}

function toSearchParams(params: SynchronizeParams): URLSearchParams {
  const stringParams: Record<string, string> = Object.fromEntries(
    Object.entries(params).map(([key, value]) => [key, String(value)]),
  )
  return new URLSearchParams(stringParams)
}

export const synchronizeService = {
  async synchronize(params: SynchronizeParams): Promise<Log[]> {
    const response = await fetch('/maelstro-backend/copy?' + toSearchParams(params), {
      method: 'PUT',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
    })
    return await response.json()
  },
}
