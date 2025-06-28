# Documentation RGPD – Projet Poll’Air

1. Introduction
Le projet Poll’Air vise à collecter, agréger, analyser et exposer des données de qualité de l’air issues de sources multiples (API, scraping, fichiers CSV, bases SQL/NoSQL), dans le respect du Règlement Général sur la Protection des Données (RGPD).
2. Principes de conformité RGPD
•	Licéité, loyauté, transparence : Aucune donnée à caractère personnel n’est collectée ni traitée. Les données sont exclusivement environnementales et anonymes.
•	Minimisation des données : Seules les données strictement nécessaires à l’analyse de la qualité de l’air sont conservées.
•	Exactitude et mise à jour : Les données sont régulièrement mises à jour via des scripts automatisés.
•	Limitation de la conservation : Les données sont conservées uniquement pour la durée nécessaire à l’analyse et à la valorisation scientifique.
•	Sécurité : Des mesures techniques (anonymisation, contrôle d’accès, logs) sont mises en place.
3. Description des traitements
•	Nature des données :
o	Données environnementales (concentrations de polluants, indices de qualité de l’air, recommandations, seuils)
o	Aucune donnée personnelle, aucune géolocalisation individuelle
•	Sources : API publiques (ATMO, Geodair), fichiers CSV, bases PostgreSQL/MongoDB
•	Finalité :
o	Analyse, visualisation et exposition de la qualité de l’air
o	Production d’indicateurs et de recommandations
•	Base légale : Intérêt légitime, mission d’intérêt public, absence de données personnelles
4. Mesures de sécurité et d’anonymisation
•	Aucune collecte d’identifiants, d’adresses IP, ou de données personnelles
•	Suppression automatique des colonnes inutiles ou sensibles lors de l’import
•	Contrôle d’accès à l’API (authentification, rate limiting)
•	Logs techniques sans données personnelles
•	Scripts de tri et de nettoyage (voir procedures_tri_donnees.py)
5. Gestion des droits des personnes
•	Droit d’accès, de rectification, d’opposition, d’effacement : Non applicable (aucune donnée personnelle)
•	Transparence : Documentation publique sur la nature et l’usage des données
6. Procédures internes
•	Tri et minimisation : Scripts dédiés pour filtrer et nettoyer les données (voir scripts/docs/rgpd/procedures_tri_donnees.py)
•	Suppression des doublons et des colonnes inutiles
•	Vérification régulière de la conformité
•	Documentation des traitements (registre RGPD dans scripts/docs/registre_traitements_rgpd.md)
7. Responsabilités et contacts
•	Responsable de traitement : Équipe projet Poll’Air
•	Contact : Arnaud Rambourg
8. Annexes et références
•	Registre des traitements RGPD (scripts/docs/registre_traitements_rgpd.md)
•	Procédures de tri et de nettoyage (scripts/docs/rgpd/procedures_tri_donnees.py)
•	Documentation technique et schémas de données
•	Références : RGPD (UE 2016/679), guides CNIL, documentation ATMO/Geodair
