# Guide de démarrage du projet

## Prérequis
- Python 3.x installé sur votre machine

## 1. Cloner le dépôt
```bash
git clone <url-du-depot>
cd <nom-du-dossier>
```

## 2. Créer un environnement virtuel
```bash
python -m venv venv
```
Si la commande ci-dessus ne fonctionne pas, essayez :
```bash
py -m venv venv
```

## 3. Activer l'environnement virtuel
- **Sous Windows :**
```bash
venv\Scripts\activate
```
- **Sous MacOS/Linux :**
```bash
source venv/bin/activate
```

## 4. Installer les dépendances
Ajoutez vos dépendances dans un fichier `requirements.txt`, puis :
```bash
pip install -r requirements.txt
```

## 5. Créer un fichier `.env`
Créez un fichier nommé `.env` à la racine du projet et ajoutez-y vos variables d'environnement, par exemple :
```
SECRET_KEY=ma_cle_secrete
DEBUG=True
```

## 6. Lancer le projet
Adaptez cette section selon votre projet (exemple pour un script Python) :
```bash
python main.py
```

---
N'oubliez pas d'ajouter/modifier les instructions selon les besoins spécifiques de votre projet. 
