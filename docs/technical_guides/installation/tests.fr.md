# Vérifications et tests

Le point de contrôle du backend est `/maelstro-backend/health`. Pour lancer les
tests et vérifications localement, le README du projet présente les commandes
Docker utilisées par la CI :

```sh
docker compose -f docker-compose-dev.yml run --rm check pytest --cov=maelstro tests/
```

Le frontend possède également des tests unitaires (`npm run test:unit` depuis
`frontend/`).
