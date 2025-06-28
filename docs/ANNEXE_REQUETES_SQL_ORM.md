# ANNEXE – Exemples de requêtes SQL et ORM

# Requêtes SQL et Big Data : exemples d’instructions et commentaires associés

## Exemple 1 : Requête SQL pure (PostgreSQL)

```sql
-- Sélectionne les recommandations pour les profils sensibles en cas de pollution mauvaise
SELECT profil_cible, niveau_pollution, conseil
FROM recommandations_base
WHERE niveau_pollution = 'mauvais' AND profil_cible = 'sensible';
```

## Exemple 2 : Requête avec ORM (SQLAlchemy)

```python
# Récupère toutes les recommandations pour les profils sensibles et pollution mauvaise
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
# Ajoute une nouvelle recommandation pour les parents en cas de pollution dégradée
nouvelle_reco = RecommandationBase(
    profil_cible='parent',
    niveau_pollution='degrade',
    type_activite='sortie_enfant',
    conseil='Privilégier les activités en intérieur',
    niveau_urgence=3,
    icone='warning',
    actif=True
)
session.add(nouvelle_reco)
session.commit()
```
