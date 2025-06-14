# 🌟 **PROJET PM - MONITORING QUALITÉ DE L'AIR**

**Système complet de collecte, traitement et analyse des données de qualité de l'air**

---

## 🎯 **VUE D'ENSEMBLE**

### **Objectif**
Analyser la qualité de l'air en France via les données AASQA (Associations Agréées de Surveillance de la Qualité de l'Air).

### **Données traitées**
- **814,242 mesures** de pollution atmosphérique
- **3 régions AASQA** : Martinique (2), Normandie (27), Eure-et-Loir (28)
- **2 polluants principaux** : NO₂ et PM10
- **Période** : Juin 2024 - Juin 2025

---

## 📁 **STRUCTURE DU PROJET**

```
PM/
├── 📊 data/                           # Données sources
│   ├── file-indices_qualite_air-*    # CSV nettoyés (3 fichiers AASQA)
│   └── scraping-moy_journaliere/      # Données JSON scrappées
├── 🔧 scripts/
│   ├── sql/                          # Scripts base de données
│   ├── data recovery/                # Extraction données
│   ├── data cleaning+standardization/ # Nettoyage
│   └── nosql/                        # MongoDB
├── 🛠️ tests/                          # Scripts de maintenance
├── 🎮 gestion_projet.py              # MENU PRINCIPAL
├── ⚡ check_status.py                # Vérification rapide
└── 📚 README_SCRIPTS.md              # Ce guide
```

---

## 🚀 **DÉMARRAGE RAPIDE**

### **1. Gestion quotidienne (recommandé)**
```cmd
python gestion_projet.py
```
**Menu interactif pour toutes les opérations courantes**

### **2. Vérification rapide**
```cmd
python check_status.py
```
**État du projet en 5 secondes**

---

## 🗄️ **BASE DE DONNÉES POSTGRESQL**

### **Tables principales**
| Table | Description | Lignes |
|-------|-------------|---------|
| `mesures_qualite_air` | **Données principales** | 814,242 |
| `aasqa_regions` | Organismes de surveillance | 3 |
| `communes` | Communes surveillées | ~11,000 |
| `indice` | Niveaux de qualité (Bon, Moyen...) | 5 |
| `polluants` | Polluants et seuils | 5 |
| `sources_donnees` | Métadonnées des imports | 3 |

### **Relations**
```
aasqa_regions ──┬── communes ──── mesures_qualite_air
               └── sources_donnees
indice ──── mesures_qualite_air
polluants ──── mesures_qualite_air
```

---

## 📋 **SCRIPTS PAR CATÉGORIE**

### 🔧 **Scripts SQL (Base de données)**

#### **Import et initialisation**
```cmd
cd scripts/sql
python import_SQL.py              # Import CSV → PostgreSQL
python create_simple_relations.py # Création tables de référence
```

#### **Maintenance avancée**
```cmd
python initialisation_complete.py # Reset + import complet
```

### 📊 **Scripts Data Recovery (Extraction)**

#### **Extraction nouvelles données**
```cmd
cd scripts/data recovery
python extract_from_api.py        # Extraction API officielle
python scraping_geodair.py        # Scraping données complémentaires
```

### 🧹 **Scripts Data Cleaning (Nettoyage)**

#### **Nettoyage données**
```cmd
cd scripts/data cleaning+standardization
python clean_api.py               # Nettoyage données API
python clean_csv.py               # Nettoyage fichiers CSV
python clean_scraping.py          # Nettoyage données scrappées
```

### 🛠️ **Scripts Tests (Maintenance)**

#### **Diagnostic et maintenance**
```cmd
cd tests
python diagnostic_donnees.py      # Diagnostic complet
python verification_post_import.py # Vérification après import
python menu_principal.py          # Menu interactif avancé
python nettoyage_complet.py       # Reset base de données
```

### 🗄️ **Scripts NoSQL (MongoDB)**

#### **Import MongoDB**
```cmd
cd scripts/nosql
python import_api&scrap_mongodb.py # Import vers MongoDB
```

---

## 🎯 **WORKFLOWS TYPIQUES**

### **🔄 Import initial des données**
```cmd
# 1. Import données principales
cd scripts/sql
python import_SQL.py

# 2. Création tables de référence  
python create_simple_relations.py

# 3. Vérification
cd ../..
python check_status.py
```

### **📈 Ajout nouvelles données**
```cmd
# 1. Extraction
cd scripts/data recovery
python extract_from_api.py

# 2. Nettoyage
cd ../data cleaning+standardization
python clean_api.py

# 3. Import
cd ../sql
python import_SQL.py
```

### **🧹 Maintenance complète**
```cmd
# Via menu interactif
python gestion_projet.py

# Ou manuellement
cd tests
python diagnostic_donnees.py
python nettoyage_complet.py  # Si nécessaire
```

---

## 💾 **CONFIGURATION**

### **Variables d'environnement (.env)**
```env
# PostgreSQL
PG_HOST=localhost
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD=votre_mot_de_passe
PG_DATABASE=postgres

# MongoDB (optionnel)
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=qualite_air
```

### **Dépendances Python**
```cmd
pip install -r requirements.txt
```
**Packages principaux :** pandas, sqlalchemy, psycopg2, requests, beautifulsoup4

---

## 📊 **DONNÉES ET PERFORMANCE**

### **Volume de données**
- **814,242 mesures** importées
- **~11,000 communes** référencées
- **3 régions AASQA** couvertes
- **Période** : 12 mois de données

### **Performance**
- **Import CSV** : ~2-3 minutes pour 814k lignes
- **Requêtes courantes** : < 100ms (avec index)
- **Espace disque** : ~200 MB (PostgreSQL)

---

## 🔍 **REQUÊTES UTILES**

### **Statistiques générales**
```sql
-- Vue d'ensemble
SELECT 
    COUNT(*) as total_mesures,
    COUNT(DISTINCT code_zone) as nb_communes,
    AVG(no2) as no2_moyen,
    AVG(pm10) as pm10_moyen
FROM mesures_qualite_air;

-- Par région AASQA
SELECT 
    a.nom_region,
    COUNT(m.*) as nb_mesures,
    ROUND(AVG(m.no2), 2) as no2_moyen
FROM mesures_qualite_air m
JOIN aasqa_regions a ON m.aasqa::text = a.aasqa_code
GROUP BY a.nom_region
ORDER BY nb_mesures DESC;
```

### **Qualité de l'air**
```sql
-- Répartition par niveau de qualité
SELECT 
    qualite_air,
    COUNT(*) as nb_mesures,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as pourcentage
FROM mesures_qualite_air 
WHERE qualite_air IS NOT NULL
GROUP BY qualite_air
ORDER BY nb_mesures DESC;
```

---

## 🎮 **UTILISATION RECOMMANDÉE**

### **Pour les tâches courantes**
```cmd
python gestion_projet.py
```
**Menu avec toutes les options principales**

### **Pour un contrôle rapide**
```cmd
python check_status.py
```
**Statut en quelques secondes**

### **Pour les opérations avancées**
Utilisez directement les scripts dans leurs dossiers respectifs selon le workflow souhaité.

---

## 🆘 **RÉSOLUTION DE PROBLÈMES**

### **Table vide après import**
```cmd
cd tests
python diagnostic_donnees.py    # Identifier le problème
python reimport_donnees.py      # Réimporter si nécessaire
```

### **Erreurs de connexion base**
1. Vérifier le fichier `.env`
2. Vérifier que PostgreSQL est démarré
3. Tester : `python check_status.py`

### **Données corrompues**
```cmd
cd tests
python nettoyage_complet.py     # Reset complet
cd ../scripts/sql
python import_SQL.py            # Réimport
```

---

## 📈 **ÉVOLUTIONS POSSIBLES**

- ✅ **Actuellement** : 3 régions AASQA (Martinique, Normandie, Eure-et-Loir)
- 🎯 **Extension** : Autres régions françaises
- 🔮 **Améliorations** : 
  - Automatisation imports quotidiens
  - Alertes qualité air
  - Interface web de visualisation
  - API REST pour applications tierces

---

## 🏆 **PROJET COMPLET ET FONCTIONNEL**

**✅ Extraction automatisée**  
**✅ Nettoyage et standardisation**  
**✅ Base de données optimisée**  
**✅ Scripts de maintenance**  
**✅ Documentation complète**

**Votre système de monitoring de la qualité de l'air est opérationnel ! 🌟**