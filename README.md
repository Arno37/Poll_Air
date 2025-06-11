# 🌬️ Monitoring Qualité de l'Air France

Système de monitoring et d'analyse de la qualité de l'air basé sur les données AASQA françaises.

## ✨ Fonctionnalités

- 🔄 **Import automatisé** CSV → PostgreSQL
- 🗄️ **Base relationnelle** optimisée (6 tables)
- 🧪 **5 polluants** avec seuils réglementaires
- 🏘️ **11,055 communes** couvertes
- 📊 **1.8M+ mesures** consolidées

## 🚀 Installation Rapide

```bash
# 1. Cloner
git clone https://github.com/username/PM.git && cd PM

# 2. Installer
pip install -r requirements.txt

# 3. Configurer
cp .env.example .env
# Éditer .env avec vos paramètres PostgreSQL

# 4. Lancer
cd scripts/sql && python initialisation_complete.py
```

## 📊 Données

| AASQA | Région | Mesures | Communes |
|-------|--------|---------|----------|
| 44 | Loire-Atlantique | 1,002,792 | 4,670 |
| 27 | Normandie | 747,198 | 3,699 |
| 28 | Eure-et-Loir | 60,996 | 2,652 |
| 2 | Martinique | 6,256 | 34 |

## 🛠️ Utilisation

```bash
# Import des données
python import_SQL.py

# Création des relations
python create_simple_relations.py
python create_polluants_table.py

# Vérification
python verification_donnees.py
```

## 🗄️ Architecture

```sql
indices_qualite_air_consolides (1.8M lignes)
├── aasqa_regions (4 organismes)
├── communes (11,055 communes)
├── polluants (5 polluants + seuils)
├── niveaux_qualite (5 niveaux)
└── sources_donnees (4 fichiers)
```

## 🧪 Polluants Surveillés

- **NO2** (Dioxyde d'azote) - Seuil alerte: 240μg/m³
- **O3** (Ozone) - Seuil alerte: 240μg/m³
- **PM10** (Particules <10μm) - Seuil alerte: 80μg/m³
- **PM2.5** (Particules <2.5μm) - Limite annuelle: 25μg/m³
- **SO2** (Dioxyde de soufre) - Seuil alerte: 500μg/m³

## 🎯 Technologies

- **Python 3.8+** | **PostgreSQL 12+**
- **SQLAlchemy** | **Pandas** | **psycopg2**

## 📄 Licence

MIT - Utilisation libre pour recherche et développement