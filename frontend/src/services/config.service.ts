export type Source = {
  name: string
  url: string
}

export type Destination = {
  name: string
  gn_url: string
  gs_url: string
}

export const configService = {
  async getSources(): Promise<Source[]> {
    const response = await fetch('/maelstro-backend/sources')
    return await response.json()
  },

  async getDestinations(): Promise<Destination[]> {
    const response = await fetch('/maelstro-backend/destinations')
    return await response.json()
  },
}
