# Synchronisation des jeux de données Datafeeder

Maelstro peut synchroniser un jeu de données géré par Datafeeder en complément
de sa métadonnée GeoNetwork. Le jeu Datafeeder est identifié par l'UUID de la
métadonnée sélectionnée dans le formulaire de synchronisation.

## Configuration

Datafeeder se configure à côté des services GeoNetwork et GeoServer existants.
Le nom de la source Datafeeder doit correspondre à celui de la source
GeoNetwork associée.

```yaml
sources:
  geonetwork_instances:
    - name: sourcePlatform
      api_url: "${SOURCE_GEONETWORK_URL}"
  geoserver_instances:
    - url: "${SOURCE_GEOSERVER_URL}"
  datafeeder_instances:
    - name: sourcePlatform
      url: "${SOURCE_DATAFEEDER_URL}"
      login: "${SOURCE_LOGIN}"
      password: "${SOURCE_PASSWORD}"

destinations:
  destinationPlatform:
    geonetwork:
      api_url: "${DESTINATION_GEONETWORK_URL}"
    geoserver:
      url: "${DESTINATION_GEOSERVER_URL}"
    datafeeder:
      url: "${DESTINATION_DATAFEEDER_URL}"
      login: "${DESTINATION_LOGIN}"
      password: "${DESTINATION_PASSWORD}"
```

Les valeurs `url`, `api_url`, `login` et `password` peuvent être résolues à
partir de variables d'environnement. Les identifiants ne doivent pas être
commités dans le dépôt.

## Comportement du formulaire

Le bouton **Import with Datafeeder** contrôle l'option `copy_data` envoyée au
backend.

- Le choix d'une autre métadonnée efface le résultat Datafeeder précédent et
  désactive `copy_data`.
- Pendant la vérification de disponibilité, le bouton est désactivé.
- Il reste désactivé si l'UUID sélectionné n'est pas trouvé dans Datafeeder.
- Son activation force **Metadata** et verrouille ce bouton, car l'import
  Datafeeder nécessite la métadonnée.
- Son activation positionne initialement **Layers** et **Styles** à off. Ces
  deux boutons restent modifiables afin de permettre explicitement la copie
  historique de ces ressources.
- Sa désactivation rend **Metadata** de nouveau modifiable. Les valeurs de
  Layers et Styles sont conservées.

Le frontend utilise actuellement un mock temporaire pour la découverte initiale
de Datafeeder et le message de disponibilité. La validation de référence est
réalisée par le backend pendant le preview et la copie. Ce mock devra être
remplacé par la découverte de configuration du backend avant de considérer
l'intégration UI comme finalisée.

## Preview

Le bouton **Synchronize** construit uniquement un preview et ne modifie pas la
destination. Quand `copy_data` est actif, le preview interroge les API
d'administration Datafeeder source et destination et présente :

- la présence du jeu de données source ;
- l'identifiant de l'integrity link ;
- le type d'import source ;
- le nom de la table finale ;
- la présence de la table sur la destination ;
- le jeu utilisant déjà cette table, le cas échéant ;
- l'action prévue.

| Action | Signification |
| --- | --- |
| `no_dataset` | L'UUID n'est pas enregistré dans le Datafeeder source. |
| `no_table` | Le type d'import ne nécessite pas de table, ou aucune table finale n'est définie. |
| `copy_table` | La table doit être transférée vers la destination. |
| `reuse_table` | La table existe et n'est associée à aucun autre jeu. |
| `conflict` | La table est utilisée par un autre jeu ; la copie est refusée. |
| `already_imported` | L'UUID possède déjà un integrity link sur la destination. |

## Synchronisation confirmée

Le bouton **Confirm** exécute les écritures. Avec l'état par défaut des boutons,
Maelstro respecte cet ordre :

1. copie de la métadonnée dans le GeoNetwork destination ;
2. réutilisation ou transfert de la table Datafeeder ;
3. appel de l'import Datafeeder destination avec `copy_recurrence: true`.

La table est transmise par blocs à travers Maelstro sans être chargée
entièrement en mémoire. L'envoi utilise un timeout étendu, car Datafeeder répond
après le chargement et l'indexation de la table.

L'opération est reprenable : une table libre est réutilisée, un UUID déjà
importé n'est pas traité une seconde fois, et une table appartenant à un autre
jeu produit un conflit au lieu d'être écrasée.

Layers et Styles sont désactivés par défaut, car l'import Datafeeder destination
est responsable de l'association des ressources produites. Si l'utilisateur
les active manuellement, Maelstro exécute aussi la copie GeoServer existante.

## Journaux d'opération

Les appels HTTP Datafeeder et leurs résultats sont enregistrés dans le contexte
`Datafeeder`. L'écran de confirmation les affiche avec les opérations de
métadonnées, couches et styles.

## Périmètre actuel

Cette version prend en charge le transfert direct et la réutilisation de table.
**Reprocess from source** n'est volontairement pas implémenté. Une évolution
pourra demander au Datafeeder destination de relancer l'ingestion originale
depuis une base, une API, une URL ou un FTP, au lieu de transférer une table
volumineuse à travers Maelstro.

Les endpoints d'administration Datafeeder utilisés sont des API internes. Les
déploiements source et destination doivent fournir des versions compatibles.
