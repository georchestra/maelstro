export type SearchResult = {
  uuid: string
  resourceTitleObject: {
    default: string
  }
  resourceAbstractObject: {
    default: string
  }
}

interface GnSource {
  uuid: string
  resourceTitleObject: {
    default: string
  }
  resourceAbstractObject: {
    default: string
  }
}

interface GnHit {
  _source: GnSource
}

export const geonetworkSearchService = {
  async search(
    sourceName: string,
    query: string,
    includeHarvested: boolean,
  ): Promise<SearchResult[]> {
    // const url =
    //   'https://demo.georchestra.org/geonetwork/srv/api/search/records/_search?bucket=bucket'

    const url = `/maelstro-backend/search/${sourceName}`

    const searchResponse = await fetch(url, {
      method: 'POST',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: {
          bool: {
            must: [
              { terms: { isTemplate: ['n'] } },
              {
                multi_match: {
                  query: query,
                  type: 'bool_prefix',
                  fields: [
                    'resourceTitleObject.*',
                    'resourceAbstractObject.*',
                    'tag',
                    'resourceIdentifier',
                  ],
                },
              },
            ],
            must_not: [
              {
                terms: {
                  resourceType: ['service', 'map', 'map/static', 'mapDigital'],
                },
              },
              ...(includeHarvested ? [] : [{ term: { isHarvested: true } }]),
            ],
          },
        },
        _source: ['resourceTitleObject', 'resourceAbstractObject', 'uuid'],
        from: 0,
        size: 20,
      }),
    })

    const hits = (await searchResponse.json()).hits.hits
    if (!hits) return []

    return hits.map((hit: GnHit) => ({
      uuid: hit._source.uuid,
      resourceTitleObject: hit._source.resourceTitleObject,
      resourceAbstractObject: hit._source.resourceAbstractObject,
    }))
  },
}
