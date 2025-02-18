export type LogDetail = {
  method?: string
  status_code?: number
  url?: string
  operation?: string
  message?: string
}

export type RawLog = {
  id: number
  start_time: string
  end_time: string
  first_name: string
  last_name: string
  status_code: number
  dataset_uuid: string
  src_name: string
  dst_name: string
  src_title: string
  dst_title: string
  copy_meta: boolean
  copy_layers: boolean
  copy_styles: boolean
  details: LogDetail[]
}

export type Log = {
  id: number
  start_time: Date
  end_time: Date
  first_name: string
  last_name: string
  status_code: number
  dataset_uuid: string
  src_name: string
  dst_name: string
  src_title: string
  dst_title: string
  copy_meta: boolean
  copy_layers: boolean
  copy_styles: boolean
  details: LogDetail[]
}

export const logsService = {
  async getLogs(): Promise<Log[]> {
    const response = await fetch('/maelstro-backend/logs?size=20&get_details=true', {
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
    })
    return ((await response.json()) as RawLog[]).map(this.toLog)
  },

  toLog(rawLog: RawLog): Log {
    return {
      ...rawLog,
      start_time: new Date(rawLog.start_time),
      end_time: new Date(rawLog.end_time),
    }
  },
}
