# Documentation technique – Projet Poll’Air

## 1. Extraction des données depuis les bases de données

Dans Poll’Air, l’extraction des données s’effectue principalement via des scripts Python et des requêtes SQL/MongoDB. Les opérations réalisées sont :
- **Sélection et filtrage** : Les scripts appliquent des critères dynamiques (zone, polluant, date, etc.) pour ne récupérer que les données pertinentes, que ce soit via des requêtes SQL paramétrées ou des filtres MongoDB.
- **Jointures** : Les requêtes SQL croisent plusieurs tables (ex : indices, profils, recommandations) pour enrichir les résultats et fournir des réponses complètes aux besoins métiers.
- **Optimisations** : Des index sont créés sur les champs fréquemment interrogés, les requêtes sont limitées en volume (pagination, LIMIT), et la validation des entrées protège contre les injections et les ralentissements.

## 2. Agrégation

- **Dépendances** : Le projet repose sur Python 3.8+, PostgreSQL, MongoDB, et des bibliothèques comme pandas, psycopg2, pymongo, fastapi (voir `requirements.txt`).
- **Nettoyage** : Les scripts de nettoyage (`clean_csv.py`, `clean_api.py`) standardisent les formats de date, corrigent les incohérences de colonnes et suppriment les doublons pour garantir la qualité des données.
- **Homogénéisation** : Les données issues de différentes sources (API, CSV, scraping) sont transformées pour avoir des structures compatibles (codes INSEE, types, noms de colonnes), facilitant leur consolidation et leur exploitation croisée.

## 3. Création de la base

- **Dépendances** : PostgreSQL et MongoDB doivent être installés et configurés, ainsi que les variables d’environnement (`.env`).
- **Commandes d’exécution** :
  - Création des tables :
    ```bash
    python scripts/sql/table_created/create_table_profils-seuils-recos.py
    ```
  - Import des données CSV :
    ```bash
    python scripts/sql/import_csv_to_pg.py
    ```
- **Conformité RGPD** : Le projet intègre une documentation RGPD (`scripts/docs/registre_traitements_rgpd.md`), des procédures de tri/anonymisation (`scripts/docs/rgpd/procedures_tri_donnees.py`), la gestion des droits d’accès, et la possibilité de suppression sur demande.

## 4. API

- **Points de terminaison principaux** :
  - `/api/air_quality/...` : accès aux données de qualité de l’air
  - `/api/hybride/echantillon` : récupération croisée PGSQL/Mongo
  - `/auth/...` : authentification, gestion des profils
- **Règles d’authentification** :
  - Authentification JWT pour les endpoints privés
  - Rate limiting pour limiter les abus
  - Validation stricte des entrées pour éviter les injections

## Sécurité et gestion des accès (RGPD & bonnes pratiques)

Pour la connexion à la base de données, le projet utilise un utilisateur applicatif dédié, dont les identifiants sont stockés dans un fichier `.env` non versionné (présent dans le `.gitignore`).
**Bonnes pratiques appliquées et recommandations pour la production :**
- Utilisation d’un utilisateur avec des droits limités (lecture/écriture sur les seules tables nécessaires).
- Mot de passe fort, stocké dans le `.env` (jamais en dur dans le code).
- Le `.env` n’est jamais versionné ni partagé publiquement.
- Pour un vrai déploiement : privilégier un utilisateur par service ou par personne (traçabilité, révocation facile), rotation régulière des mots de passe, et gestion centralisée des secrets (Vault, Azure Key Vault, etc.).

**Exemple de code pour charger les identifiants de manière sécurisée :**

```python
import os
from dotenv import load_dotenv

load_dotenv()
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
```

> Pour la soutenance, un utilisateur unique est utilisé. En production, il est recommandé d’appliquer une gestion fine des accès et des secrets pour garantir la conformité RGPD et la sécurité.

## Perspectives et améliorations

### Déploiement et usage à venir de l’API développée

L’API Poll’Air a été pensée pour être déployée sur un serveur cloud ou local, et pour servir de socle à des applications web, mobiles ou des outils partenaires. Sa vocation première est de fournir des recommandations personnalisées aux utilisateurs en fonction de leur profil et de la qualité de l’air mesurée ou prédite.

### Finalité du projet

La finalité principale de ce projet est d’offrir un service de recommandations adaptées à chaque utilisateur, en croisant les données de pollution, les seuils personnalisés et les profils. L’objectif est d’accompagner chaque citoyen dans la gestion de son exposition à la pollution, grâce à des conseils contextualisés, automatisés et accessibles en temps réel.

### Points possibles d’amélioration

- Automatisation complète du pipeline (orchestrateur, planification) (ex : Airflow, cron)
- Développement d’une interface utilisateur web/mobile (ex : dashboard, notifications)
- Documentation API interactive et cas d’usage
- Renforcement des tests automatisés (ex : pytest, CI/CD)
- Passage à une architecture scalable (microservices, conteneurs)
- Sécurité avancée et monitoring (ex : audit, alertes)
- Intégration de nouvelles sources de données (IoT, open data, etc.)

Enfin, la suite logique de ce projet serait de développer un modèle d’intelligence artificielle pour affiner les recommandations, anticiper les épisodes de pollution et personnaliser encore davantage l’accompagnement des utilisateurs.

## Conclusion

La réalisation de ce projet a été très formatrice : il m’a permis de gérer un projet Data de bout en bout. J’ai pu mettre en pratique l’ensemble des compétences acquises depuis le début de ma formation et de développer une solution sur un sujet qui m’intéresse. Cette expérience m’a donné confiance pour aborder de nouveaux défis et m’a sensibilisé à l’importance de la rigueur et de l’organisation dans la conduite d’un travail abouti.

# ANNEXE – Exemples de requêtes SQL et ORM

## Exemple 1 : Requête SQL pure (PostgreSQL)

```sql
SELECT profil_cible, niveau_pollution, conseil
FROM recommandations_base
WHERE niveau_pollution = 'mauvais' AND profil_cible = 'sensible';
```

## Exemple 2 : Requête avec ORM (SQLAlchemy)

```python
from sqlalchemy.orm import Session
from models import RecommandationBase

session = Session()
resultats = session.query(RecommandationBase).filter_by(
    niveau_pollution='mauvais',
    profil_cible='sensible'
).all()
for reco in resultats:
    print(reco.profil_cible, reco.niveau_pollution, reco.conseil)
```

## Exemple 3 : Insertion avec ORM (SQLAlchemy)

```python
nouvelle_reco = RecommandationBase(
    profil_cible='parent',
    niveau_pollution='degrade',
    type_activite='sortie_enfant',
    conseil='Privilégier les activités en intérieur',
    niveau_urgence=3,
# ...suite du code...
```
