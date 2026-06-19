# config.py

import os
from dotenv import load_dotenv, find_dotenv

# Load the .env file from the project folder
load_dotenv(find_dotenv(usecwd=True))

DB_CONFIG = {
    "host": os.getenv("PHASE_E_DB_HOST", "localhost"),
    "database": os.getenv("PHASE_E_DB_NAME", "unified_db"),
    "user": os.getenv("PHASE_E_DB_USER", "postgres"),
    "password": os.getenv("PHASE_E_DB_PASSWORD"),
    "port": int(os.getenv("PHASE_E_DB_PORT", "5432"))
}