# Architecture

Maelstro comprend une interface monopage Vue.js et un backend Python/FastAPI.
Le backend se connecte aux instances GeoNetwork et GeoServer source et
destination configurées. PostgreSQL peut être utilisé pour stocker l'historique
des synchronisations.

Utilisez le fichier Compose autonome pour un déploiement séparé, ou la
configuration Compose geOrchestra pour une intégration à geOrchestra.
