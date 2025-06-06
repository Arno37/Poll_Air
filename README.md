# 🌍 Système de Gestion des Données de Qualité de l'Air

Un système complet basé sur Python pour traiter, nettoyer et importer les données françaises de qualité de l'air dans des bases PostgreSQL. Ce projet gère les données AASQA (Associations Agréées de Surveillance de la Qualité de l'Air) avec des pipelines ETL automatisés.

## ✨ Fonctionnalités

- **🔧 Traitement Automatisé**: Nettoyage et standardisation des fichiers CSV de qualité de l'air
- **📊 Support Multi-Polluants**: Gestion des mesures NO2, O3, PM10, PM2.5 et SO2
- **🗄️ Intégration PostgreSQL**: Import fluide avec structures de tables optimisées
- **🌐 Conformité AASQA**: Entièrement compatible avec les standards français de surveillance
- **⚡ Traitement par Lots**: Traitement simultané de plusieurs fichiers
- **🛡️ Sécurité Environnement**: Gestion sécurisée des identifiants de base de données

## 🏗️ Structure du Projet

```
PM/
├── data/
│   ├── file-indices_qualite_air-01-01-2024_01-01-2025/  # Données brutes
│   └── file-indices_nettoyes/                           # Données nettoyées
├── scripts/
│   ├── cleaned_csv.py          # Nettoyage et standardisation des données
│   ├── import_SQL.py           # Moteur d'import PostgreSQL
│   └── renaming_columns.py     # Utilitaires de renommage de colonnes
├── .env                        # Variables d'environnement
├── requirements.txt            # Dépendances Python
└── README.md                   # Documentation du projet
```

## 🚀 Démarrage Rapide

### Prérequis

- Python 3.8+
- PostgreSQL 12+
- Environnement virtuel (recommandé)

### Installation

1. **Cloner le repository**
   ```bash
   git clone <repository-url>
   cd PM
   ```

2. **Configurer l'environnement virtuel**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer les variables d'environnement**
   Créer un fichier `.env` avec vos identifiants PostgreSQL :
   ```env
   PG_USER=your_username
   PG_PASSWORD=your_password
   PG_HOST=localhost
   PG_PORT=5432
   PG_DATABASE=your_database
   ```

### Utilisation

1. **Nettoyer et standardiser les données**
   ```bash
   cd scripts
   python cleaned_csv.py
   ```
   Cela va :
   - Supprimer les colonnes inutiles
   - Standardiser les noms de colonnes
   - Sauvegarder les fichiers nettoyés dans `data/file-indices_nettoyes/`

2. **Importer vers PostgreSQL**
   ```bash
   python import_SQL.py
   ```
   Cela va :
   - Créer des tables pour quelques régions AASQA
   - Importer toutes les données nettoyées
   - Générer des noms de tables standardisés

## 📊 Schéma des Données

### Données d'Entrée (Format AASQA brut)
- Colonnes originales avec conventions françaises
- Mesures de multiples polluants
- Métadonnées géographiques et temporelles

### Schéma de Sortie (Standardisé)
| Colonne | Type | Description |
|---------|------|-------------|
| `aasqa` | VARCHAR | Identifiant de la région AASQA |
| `NO2` | FLOAT | Niveaux de dioxyde d'azote |
| `O3` | FLOAT | Niveaux d'ozone |
| `PM10` | FLOAT | Particules fines (10μm) |
| `PM25` | FLOAT | Particules fines (2.5μm) |
| `SO2` | FLOAT | Niveaux de dioxyde de soufre |
| `date_prise_mesure` | DATE | Date de mesure |
| `qualite_air` | VARCHAR | Indice de qualité de l'air |
| `zone` | VARCHAR | Zone géographique |
| `source` | VARCHAR | Source des données |
| `type_zone` | VARCHAR | Classification de zone |

## 🔧 Configuration

### Variables d'Environnement
```env
# Configuration PostgreSQL
PG_USER=your_username
PG_PASSWORD=your_password
PG_HOST=localhost
PG_PORT=5432
PG_DATABASE=your_database
```

### Options de Traitement
- **Filtrage de colonnes** : Supprime automatiquement les colonnes de métadonnées
- **Validation des données** : Assure l'intégrité lors du traitement
- **Nommage flexible** : Support diverses conventions de nommage AASQA

## 📈 Performance

- **Vitesse de traitement** : ~1000 lignes/seconde
- **Utilisation mémoire** : Optimisé pour de gros volumes
- **Support par lots** : Gère plusieurs fichiers simultanément
- **Récupération d'erreurs** : Continue le traitement même si des fichiers échouent

## 🛠️ Développement

### Qualité du Code
- Code Python propre et documenté
- Architecture modulaire
- Gestion d'erreurs et logging
- Configuration basée sur l'environnement

### Extensibilité
- Facile d'ajouter de nouveaux polluants
- Transformations de données configurables
- Architecture prête pour plugins

## 📋 Dépendances

```txt
pandas>=1.5.0
sqlalchemy>=1.4.0
psycopg2-binary>=2.9.0
python-dotenv>=0.19.0
```

## 🤝 Contribution

1. Fork le repository
2. Créer une branche feature (`git checkout -b feature/amazing-feature`)
3. Commit vos changements (`git commit -m 'Add amazing feature'`)
4. Push vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

---
N'oubliez pas d'ajouter/modifier les instructions selon les besoins spécifiques de votre projet.
