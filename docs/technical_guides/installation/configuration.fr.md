# Configuration

Le serveur lit le fichier YAML indiqué par `MAELSTRO_CONFIG`. Les fichiers
Compose fournis montent `config/` et utilisent `/etc/maelstro/config.yaml` ;
modifiez [`config/config.yaml`](../../../config/config.yaml) pour votre
déploiement.

Ce fichier définit les sources GeoNetwork et GeoServer, les destinations, les
transformations XSL facultatives et la journalisation PostgreSQL facultative.
Les identifiants peuvent être fournis via des variables d'environnement, par
exemple `"${SERVER_PASSWORD}"`. Ne stockez pas de vrais identifiants dans le
dépôt.

Pour les détails des champs et un exemple, consultez le
[README](../../../README.md) et
[`backend/tests/test_config.yaml`](../../../backend/tests/test_config.yaml).
