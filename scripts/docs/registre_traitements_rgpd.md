# REGISTRE DES TRAITEMENTS DE DONNÉES PERSONNELLES
## Conformité RGPD - Projet Qualité de l'Air

### IDENTIFICATION DU RESPONSABLE DE TRAITEMENT
- **Organisme** : GRETA CENTRE-VAL-DE-LOIRE
- **Responsable** : Arnaud Rambourg
- **Contact** : arnaudrambourg@gmail.com

### SOURCES DES DONNÉES

#### DONNÉES PUBLIQUES COLLECTÉES
1. **API ATMO France**
   - **URL** : https://admindata.atmo-france.org/api/v2/
   - **Type** : Données publiques officielles
   - **Finalité** : Episodes de pollution historiques
   - **Base légale** : Art. 6.1.e RGPD (mission d'intérêt public)

2. **Géod'Air - Données de surveillance**
   - **URL** : https://www.geodair.fr/donnees/consultation
   - **Type** : Données publiques de qualité de l'air
   - **Finalité** : Moyennes journalières par station
   - **Base légale** : Art. 6.1.e RGPD (mission d'intérêt public)

3. **Fichiers AASQA publics**
   - **Source** : Organismes régionaux de surveillance
   - **Type** : Historiques consolidés publics
   - **Finalité** : Données de référence qualité air

#### TRAITEMENT DES COORDONNÉES GPS
- **Origine** : Localisation stations de mesure publiques
- **Précision initiale** : 6 décimales (~10cm)
- **Traitement appliqué** : Arrondi à 3 décimales (~100m)
- **Justification** : Pseudonymisation conforme RGPD

### TRAITEMENT 1 : GÉOLOCALISATION STATIONS DE MESURE
- **Finalité** : Analyse géospatiale de la pollution atmosphérique
- **Base légale** : Intérêt légitime (Art. 6.1.f RGPD)
- **Données traitées** :
  - Coordonnées GPS précises (latitude/longitude)
  - Codes INSEE des communes
  - Noms des stations de mesure
- **Durée conservation** : 24 mois maximum
- **Destinataires** : Équipes de recherche interne
- **Mesures sécurité** : 
  - Pseudonymisation par arrondi géographique
  - Accès restreint par authentification
  - Stockage sécurisé base de données

### TRAITEMENT 2 : HORODATAGE DES MESURES
- **Finalité** : Analyse temporelle de la pollution
- **Base légale** : Intérêt légitime (Art. 6.1.f RGPD)
- **Données traitées** :
  - Timestamps précis des mesures
  - Dates de mise à jour
- **Durée conservation** : 12 mois maximum
- **Mesures sécurité** : Agrégation par tranches horaires

### MESURES DE PROTECTION APPLIQUÉES
1. **Pseudonymisation** : Arrondi coordonnées à 100m près
2. **Limitation d'accès** : Authentification JWT obligatoire
3. **Minimisation** : Seules données nécessaires conservées
4. **Purge automatique** : Suppression après 24 mois