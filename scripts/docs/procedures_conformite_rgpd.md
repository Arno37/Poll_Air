# PROCÉDURES DE CONFORMITÉ RGPD

## 1. PRÉSENTATION GÉNÉRALE

### 1.1 Objectif du document
Ce document définit les procédures opérationnelles pour assurer la conformité RGPD du système de traitement des données de qualité de l'air. Il détaille les processus d'anonymisation, de purge, de sécurisation et de contrôle des données personnelles.

### 1.2 Champ d'application
- Données collectées via l'API ATMO Nouvelle-Aquitaine
- Données récupérées par scraping du site Geodair
- Données CSV des indices de qualité de l'air
- Bases de données PostgreSQL et MongoDB

### 1.3 Références légales
- Règlement Général sur la Protection des Données (RGPD) - UE 2016/679
- Loi Informatique et Libertés modifiée (LIL) - Loi n°78-17 du 6 janvier 1978

## 2. RESPONSABILITÉS ET ORGANISATION

### 2.1 Responsable de traitement
- **Nom** : [À PERSONNALISER - Votre nom]
- **Email** : [À PERSONNALISER - Votre email]
- **Organisme** : [À PERSONNALISER - Votre organisme/école]
- **Responsabilités** : Décisions sur les finalités et moyens du traitement

### 2.2 Responsable technique
- **Nom** : [À PERSONNALISER - Votre nom]
- **Email** : [À PERSONNALISER - Votre email]
- **Responsabilités** : Mise en œuvre technique des mesures RGPD

### 2.3 Délégué à la Protection des Données (DPO)
- **Statut** : [À DÉFINIR - Interne/Externe/Non requis pour ce projet]
- **Contact** : [À PERSONNALISER si applicable]

## 3. FRÉQUENCES D'EXÉCUTION

### 3.1 Traitement automatisé
- **Anonymisation immédiate** : À chaque import de nouvelles données
- **Contrôle qualité** : Quotidien (via logs automatiques)
- **Sauvegarde sécurisée** : Quotidienne

### 3.2 Traitement périodique
- **Purge des données** : Trimestrielle (tous les 3 mois)
- **Audit de conformité** : Mensuel
- **Rapport de conformité** : Mensuel
- **Mise à jour documentation** : Semestrielle

### 3.3 Traitement exceptionnel
- **Gestion des incidents** : Immédiate (< 24h)
- **Demandes d'exercice des droits** : Sous 1 mois
- **Audit externe** : Annuel (si requis)

## 4. PROCÉDURES TECHNIQUES

### 4.1 Commandes d'exécution principale
```bash
# Navigation vers le répertoire RGPD
cd scripts/rgpd

# Exécution du script principal de conformité
python procedures_tri_donnees.py

# Vérification des logs
type logs\rgpd_compliance.log
```

### 4.2 Procédures d'anonymisation
```bash
# Anonymisation des données API
python procedures_tri_donnees.py --mode anonymize --source api

# Anonymisation des données scraping
python procedures_tri_donnees.py --mode anonymize --source scraping

# Anonymisation complète
python procedures_tri_donnees.py --mode anonymize --source all
```

### 4.3 Procédures de purge
```bash
# Purge des données expirées
python procedures_tri_donnees.py --mode purge --days 90

# Purge sélective par source
python procedures_tri_donnees.py --mode purge --source api --days 90

# Purge complète (ATTENTION: Irréversible)
python procedures_tri_donnees.py --mode purge --confirm --all
```

### 4.4 Génération de rapports
```bash
# Rapport de conformité mensuel
python procedures_tri_donnees.py --mode report --period monthly

# Rapport détaillé
python procedures_tri_donnees.py --mode report --detailed

# Export du rapport
python procedures_tri_donnees.py --mode report --export csv
```

## 5. MESURES DE SÉCURITÉ TECHNIQUES

### 5.1 Chiffrement
- **Base de données** : Chiffrement AES-256 au repos
- **Transmission** : HTTPS/TLS 1.3 pour l'API
- **Mots de passe** : Hachage bcrypt avec salt

### 5.2 Contrôle d'accès
- **Authentification** : JWT avec expiration 24h
- **Autorisation** : Rôles user/admin différenciés
- **API** : Rate limiting et monitoring des accès

### 5.3 Monitoring et logs
- **Accès aux données** : Log de tous les accès
- **Modifications** : Traçabilité complète
- **Incidents** : Alertes automatiques

## 6. CRITÈRES DE CONSERVATION ET SUPPRESSION

### 6.1 Durées de conservation
- **Données brutes collectées** : 12 mois maximum
- **Données anonymisées** : Conservation illimitée
- **Logs d'accès** : 6 mois
- **Rapports de conformité** : 3 ans

### 6.2 Critères de suppression automatique
- **Âge des données** : > 12 mois
- **Données redondantes** : Doublons identifiés
- **Données corrompues** : Non récupérables
- **Données non conformes** : Ne respectant pas le format attendu

### 6.3 Procédure de suppression sécurisée
- **Suppression logique** : Marquage pour suppression
- **Suppression physique** : Écrasement sécurisé
- **Vérification** : Contrôle post-suppression
- **Documentation** : Traçabilité des suppressions

## 7. GESTION DES INCIDENTS

### 7.1 Types d'incidents
- **Accès non autorisé** : Tentative d'intrusion
- **Fuite de données** : Exposition accidentelle
- **Corruption de données** : Altération des données
- **Panne système** : Indisponibilité des services

### 7.2 Procédure d'urgence
1. **Détection** : Identification de l'incident (< 1h)
2. **Évaluation** : Analyse de l'impact (< 4h)
3. **Containment** : Limitation des dégâts (< 12h)
4. **Notification** : Information des autorités si requis (< 72h)
5. **Résolution** : Correction du problème
6. **Documentation** : Rapport d'incident complet

### 7.3 Contacts d'urgence
- **Responsable technique** : [À PERSONNALISER - Votre numéro]
- **CNIL** : https://www.cnil.fr/fr/notifier-une-violation-de-donnees-personnelles
- **Support technique** : [À PERSONNALISER si applicable]

## 8. EXERCICE DES DROITS DES PERSONNES

### 8.1 Droits supportés
- **Droit d'accès** : Consultation des données personnelles
- **Droit de rectification** : Correction des données inexactes
- **Droit à l'effacement** : Suppression des données
- **Droit à la portabilité** : Export des données dans un format structuré

### 8.2 Procédure de traitement des demandes
1. **Réception** : Accusé de réception sous 48h
2. **Vérification** : Contrôle de l'identité du demandeur
3. **Traitement** : Exécution de la demande
4. **Réponse** : Notification au demandeur sous 1 mois

### 8.3 Outils techniques
```bash
# Recherche des données d'une personne
python procedures_tri_donnees.py --mode search --person "identifiant"

# Export des données personnelles
python procedures_tri_donnees.py --mode export --person "identifiant"

# Suppression des données personnelles
python procedures_tri_donnees.py --mode delete --person "identifiant" --confirm
```

## 9. INDICATEURS DE CONFORMITÉ

### 9.1 Métriques techniques
- **Taux d'anonymisation** : 100% des données personnelles
- **Temps de purge** : < 24h pour les données expirées
- **Disponibilité API** : > 99.5%
- **Temps de réponse** : < 500ms en moyenne

### 9.2 Métriques de processus
- **Délai de traitement des demandes** : < 1 mois
- **Taux de résolution des incidents** : 100%
- **Fréquence des audits** : Mensuelle
- **Conformité documentaire** : 100%

### 9.3 Tableaux de bord
- **Dashboard technique** : Monitoring en temps réel
- **Rapport mensuel** : Synthèse de conformité
- **Audit trimestriel** : Évaluation approfondie

## 10. FORMATION ET SENSIBILISATION

### 10.1 Formation initiale
- **RGPD général** : Principes et obligations
- **Procédures techniques** : Utilisation des scripts
- **Gestion des incidents** : Procédures d'urgence

### 10.2 Formation continue
- **Veille réglementaire** : Évolution du RGPD
- **Mise à jour technique** : Nouveaux outils
- **Retour d'expérience** : Analyse des incidents

## 11. CONTRÔLE ET AUDIT

### 11.1 Auto-évaluation
- **Check-list mensuelle** : Vérification des procédures
- **Tests techniques** : Validation des scripts
- **Révision documentaire** : Mise à jour des procédures

### 11.2 Audit externe
- **Fréquence** : Annuelle (si requis)
- **Périmètre** : Ensemble du dispositif RGPD
- **Suivi** : Plan d'action correctif

## 12. DOCUMENTATION ET ARCHIVAGE

### 12.1 Documents obligatoires
- **Registre des traitements** : Tenu à jour en permanence
- **Analyse d'impact** : Pour les traitements à risque
- **Procédures techniques** : Documentation des scripts
- **Rapports de conformité** : Conservation 3 ans

### 12.2 Versioning et sauvegarde
- **Contrôle de version** : Git pour tous les scripts
- **Sauvegarde documentation** : Quotidienne
- **Archivage** : Conservation sécurisée

---

## ANNEXES

### Annexe A : Planning d'exécution mensuel
```
Semaine 1 : Purge des données expirées
Semaine 2 : Audit de conformité
Semaine 3 : Génération du rapport mensuel
Semaine 4 : Mise à jour documentation
```

### Annexe B : Contacts utiles
- **CNIL** : 01 53 73 22 22 - https://www.cnil.fr
- **Support technique** : [À PERSONNALISER]
- **Responsable RGPD** : [À PERSONNALISER]

### Annexe C : Templates de rapports
Voir répertoire `scripts/rgpd/templates/` pour les modèles de rapports.

---

**Document créé le** : 18 juin 2025  
**Version** : 1.0  
**Prochaine révision** : 18 décembre 2025