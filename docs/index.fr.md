---
hide:
  - navigation
  - toc
---

# Accueil

## Qu'est-ce que Maelstro ?

Maelstro est un logiciel qui permet de synchroniser :

* des Métadonnées (gérées par GeoNetwork)
* des couches et des styles (gérés par GeoServer)
* depuis une plateforme source vers une plateforme destination
: dev → preprod, preprod → prod


## Fonctionnalités

* Sʼintègre à côté dʼun geOrchestra ou seul
* Source unique : recherche dans le catalogue de GeoNetwork
* Recherche des métadonnées moissonnées ou non
* Sélection de la destination (plusieurs possibles)
* Synchronisation indépendante métadonnée / couche GeoServer / styles GeoServer
* Application de transformation XSL (v1 uniquement) en fonction dʼune source ou/et dʼune destination
* Consultation des journaux de logs et historique des synchronisations
* Hautement scriptable via son API


## Technologies

Un "front" en vuJS qui offre une interface simple pour choisir les jeux de données à synchroniser.

Un "backend" en python / FastAPI qui offre une API.

