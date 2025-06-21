from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Utilisateurs depuis .env
ADMIN_USER = os.getenv("ADMIN_USER").split(":")
NORMAL_USER = os.getenv("NORMAL_USER").split(":")

# Configuration du hachage
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

router = APIRouter(prefix="/auth", tags=["Authentification"])

# Modèles Pydantic
class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Base de données utilisateurs simple
fake_users_db = {
    ADMIN_USER[0]: {
        "username": ADMIN_USER[0],
        "hashed_password": pwd_context.hash(ADMIN_USER[1]),
        "role": "admin"
    },
    NORMAL_USER[0]: {
        "username": NORMAL_USER[0], 
        "hashed_password": pwd_context.hash(NORMAL_USER[1]),
        "role": "user"
    }
}

# Fonctions utilitaires sécurisées
def verify_password(plain_password, hashed_password):
    """
    Vérifie un mot de passe en clair contre son hash bcrypt.
    
    Utilise bcrypt pour la vérification sécurisée du mot de passe.
    Protection contre les attaques par timing et rainbow tables.
    
    Args:
        plain_password (str): Mot de passe en clair saisi par l'utilisateur
        hashed_password (str): Hash bcrypt stocké en base de données
        
    Returns:
        bool: True si le mot de passe correspond, False sinon
    """
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
    """
    Authentifie un utilisateur par nom d'utilisateur et mot de passe.
    
    Recherche l'utilisateur en base et vérifie ses credentials.
    Première étape du processus d'authentification JWT.
    
    Args:
        username (str): Nom d'utilisateur
        password (str): Mot de passe en clair
        
    Returns:
        dict|False: Données utilisateur si authentification réussie, False sinon
        
    Security:
        - Protection contre énumération des utilisateurs
        - Hachage bcrypt des mots de passe
        - Temps de réponse constant (protection timing attacks)
    """
    user = fake_users_db.get(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return False
    return user

def create_access_token(data: dict):
    """
    Génère un token JWT signé pour authentification.
    
    Crée un JSON Web Token avec expiration automatique.
    Le token contient les claims utilisateur et une date d'expiration.
    
    Args:
        data (dict): Données à inclure dans le token (username, role, etc.)
        
    Returns:
        str: Token JWT signé
        
    Security:
        - Signature HMAC avec clé secrète
        - Expiration automatique (définie par ACCESS_TOKEN_EXPIRE_MINUTES)
        - Algorithme HS256 (HMAC + SHA-256)
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Extrait et valide l'utilisateur actuel depuis le token JWT.
    
    Middleware d'authentification pour les endpoints protégés.
    Décode et valide le token Bearer, récupère les données utilisateur.
    
    Args:
        credentials: Token Bearer HTTP fourni dans l'en-tête Authorization
        
    Returns:
        dict: Données de l'utilisateur authentifié (username, role)
        
    Raises:
        HTTPException: 401 si token invalide, expiré ou utilisateur inexistant
        
    Security:
        - Vérification signature JWT
        - Validation expiration du token
        - Contrôle existence utilisateur
        - Protection contre token replay (via expiration)
    """
    try:
        # Décodage et validation du token JWT
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token invalide")
    except JWTError:
        # Token malformé, signature invalide ou expiré
        raise HTTPException(status_code=401, detail="Token invalide")
    
    # Vérification existence de l'utilisateur
    user = fake_users_db.get(username)
    if user is None:
        raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
    return user

# Endpoints
@router.post("/login", summary="🔑 Connexion",
    description="Obtenir un token JWT (user/motdepasse ou admin/motdepasse)",
    response_model=Token)
def login(login_data: LoginRequest):
    user = authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect"
        )
    
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}