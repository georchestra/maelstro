# API

L'interface interactive de l'API est disponible à
`/maelstro-backend/docs` sur un déploiement en cours d'exécution.

| Point d'accès | Fonction |
|---|---|
| `GET /sources` | Lister les sources GeoNetwork configurées |
| `GET /destinations` | Lister les plateformes de destination |
| `GET /transformations` | Lister les transformations XSL configurées |
| `POST /search/{src_name}` | Rechercher dans un catalogue source |
| `GET /copy_preview` | Prévisualiser la copie d'un jeu de données |
| `PUT /copy` | Copier les métadonnées, couches et styles sélectionnés |
| `GET /logs` | Consulter l'historique des synchronisations |
| `GET /health` | Vérifier la disponibilité du backend |
