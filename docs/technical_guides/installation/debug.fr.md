# Dépannage et journaux

- Vérifiez que le backend répond à `/maelstro-backend/health`.
- Ouvrez `/maelstro-backend/docs` pour consulter l'interface interactive de
  l'API FastAPI.
- Consultez les journaux du conteneur backend avec
  `docker compose logs maelstro-back`.
- Vérifiez les URL et identifiants des sources et destinations dans le fichier
  YAML.

L'historique des synchronisations est stocké dans PostgreSQL lorsque
`db_logging` est configuré. L'API `/logs` renvoie une erreur si la
journalisation en base n'est pas configurée.
