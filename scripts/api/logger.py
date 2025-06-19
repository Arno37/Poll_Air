import logging
import json
from datetime import datetime
import os


os.makedirs("logs", exist_ok=True)

# Configuration simple du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/api.log'),  # Fichier
        logging.StreamHandler()               # Console
    ]
)

logger = logging.getLogger("API")

def log_api_call(endpoint: str, user: str = "anonymous", params: dict = None, success: bool = True):
    """Log simple des appels API"""
    log_data = {
        "endpoint": endpoint,
        "user": user,
        "params": params or {},
        "success": success,
        "timestamp": datetime.now().isoformat()
    }
    
    if success:
        logger.info(f"API_CALL: {json.dumps(log_data)}")
    else:
        logger.error(f"API_ERROR: {json.dumps(log_data)}")

def log_login(username: str, success: bool, ip: str = "unknown"):
    """Log simple des connexions"""
    log_data = {
        "username": username,
        "success": success,
        "ip": ip,
        "timestamp": datetime.now().isoformat()
    }
    
    if success:
        logger.info(f"LOGIN_SUCCESS: {json.dumps(log_data)}")
    else:
        logger.warning(f"LOGIN_FAILED: {json.dumps(log_data)}")