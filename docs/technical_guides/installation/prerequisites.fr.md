## Prérequis

- Configurer tous les utilisateurs/mots de passes sur toutes les plateformes (lecture/écriture) avec les rôles :  **ADMINISTRATOR** et **GN_EDITOR**
- Configurer les URL et identifiants des sources et destinations.
- Vérifier l'existence des espaces de travail et entrepôts nécessaires sur les
  GeoServer de destination.
- Configurer PostgreSQL si l'historique des synchronisations est nécessaire.
- Avec geOrchestra, configurer la passerelle et attribuer le rôle `MAELSTRO`
  comme indiqué dans [`config/HOWTO.md`](../../../config/HOWTO.md).


Maelstro ne possède pas de console distincte d'administration des données. Les
administrateurs maintiennent la configuration YAML côté serveur, vérifient que
les espaces de travail et entrepôts GeoServer requis existent et gèrent les
accès avec le système d'authentification du déploiement.

Pour les rôles geOrchestra, les routes du proxy et l'en-tête, consultez
[`config/HOWTO.md`](../../../config/HOWTO.md).
