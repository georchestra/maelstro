# Lancer Maelstro

Pour un déploiement autonome, sélectionnez le fichier Compose et démarrez les
services :

```sh
ln -s docker-compose-solo.yml docker-compose.yml
docker compose up -d
```

Ouvrez [http://127.0.0.1:8080/maelstro/](http://127.0.0.1:8080/maelstro/).
Pour utiliser geOrchestra, suivez la procédure dans
[`config/HOWTO.md`](../../../config/HOWTO.md) et la section geOrchestra du
[README du projet](../../../README.md).
