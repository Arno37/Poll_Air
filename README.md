# Poll’Air

Poll’Air est un projet data complet visant à collecter, nettoyer, stocker, analyser et exposer des données sur la qualité de l’air en France, avec une attention particulière à la conformité RGPD, la sécurité, et la documentation technique.

## Sommaire
- [Présentation](#présentation)
- [Architecture du projet](#architecture-du-projet)
- [Installation et configuration](#installation-et-configuration)
- [Utilisation](#utilisation)
- [Sécurité & RGPD](#sécurité--rgpd)
- [Organisation des fichiers](#organisation-des-fichiers)
- [Tests](#tests)
- [Auteurs](#auteurs)

## Présentation
Poll’Air centralise des données issues de sources publiques (API, scraping, CSV) sur la pollution de l’air, les traite, les stocke dans PostgreSQL et MongoDB, et expose des API sécurisées pour la consultation et la gestion des recommandations santé.

## Architecture du projet
- **scripts/** : Scripts Python pour l’ETL, l’import/export, la gestion des utilisateurs, etc.
- **data/** : Données brutes et nettoyées (JSON, CSV).
- **docs/** : Documentation technique, RGPD, annexes SQL.
- **tests/** : Scripts de tests unitaires et d’intégration.
- **.env** : Variables d’environnement (non versionné, à protéger).

## Installation et configuration
1. **Cloner le dépôt**
2. **Créer un environnement virtuel Python**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Configurer le fichier `.env`**
   - Renseigner les accès PostgreSQL/MongoDB, clés secrètes, etc.
   - Exemple :
     ```env
     PG_USER=postgres
     PG_PASSWORD=motdepasse
     PG_HOST=localhost
     PG_PORT=5432
     PG_DATABASE=qualite_air
     MONGO_CONNECTION_STRING=mongodb://localhost:27017/
     MONGO_DATABASE=pollution
     SECRET_KEY=secret
     ```
4. **Initialiser la base de données**
   - Utiliser les scripts SQL dans `scripts/sql/` pour créer les tables.
   - Importer les données avec `import_csv_to_pg.py`.

## Utilisation
- **Lancer l’API** :
  ```bash
  python scripts/api/main.py
  ```
- **Importer des données** :
  ```bash
  python scripts/sql/import_csv_to_pg.py
  ```
- **Nettoyer les données** :
  ```bash
  python scripts/data cleaning+standardization/clean_api.py
  ```
- **Consulter la documentation technique** :
  Voir `docs/DOCUMENTATION_TECHNIQUE_JURY.md`.

## Sécurité & RGPD
- Les identifiants techniques sont stockés dans `.env` (jamais en base, ni en dur dans le code).
- Les mots de passe utilisateurs API sont hashés en base.
- Accès restreint au `.env` (non versionné, droits limités).
- Conformité RGPD documentée dans `docs/DOCUMENTATION_RGPD.md` et `docs/registre_traitements_rgpd.md`.
- Suppression sécurisée des utilisateurs PostgreSQL via scripts dédiés.

## Organisation des fichiers
- `scripts/` : Scripts Python (API, ETL, sécurité, etc.)
- `data/` : Données sources et nettoyées
- `docs/` : Documentation technique, RGPD, annexes
- `tests/` : Scripts de tests
- `.env` : Variables d’environnement (à protéger)

## Tests
- Scripts de tests dans `tests/`.
- Exécution :
  ```bash
  python -m unittest discover tests
  ```

## Auteurs
- Projet réalisé par Arnaud Rambourg  / 1er Bloc du titre Développeur Data en IA
- Encadrement : [Nom du tuteur, jury, etc.]

---
Pour toute question, consulter la documentation technique ou contacter l’équipe projet.
