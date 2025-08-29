---
hide:
  - navigation
  - toc
---

# Home

## What is Maelstro?

Maelstro is a software tool that synchronizes:

* Metadata (managed by GeoNetwork)
* Layers and styles (managed by GeoServer)
* From a source platform to a destination platform:
  dev → preprod, preprod → prod


## Features

* Integrates alongside a geOrchestra setup or as a standalone tool
* Single source: Search within the GeoNetwork catalog
* Search for harvested or non-harvested metadata
* Select destination(s) (multiple options possible)
* Independent synchronization of metadata, GeoServer layers, and GeoServer styles
* Apply XSL transformations (v1 only) based on source and/or destination
* View log files and synchronization history
* Highly scriptable via its API


## Technologies

* A "front-end" built with VueJS, providing a simple interface for selecting datasets to synchronize
* A "back-end" in Python/FastAPI, offering an API

