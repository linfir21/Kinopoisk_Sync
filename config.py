import os
from dotenv import load_dotenv

load_dotenv()

USERS = {
    "user1": {
        "kp_id": os.getenv("KP_USER1_ID"),
        "name": os.getenv("KP_USER1_NAME", "Пользователь 1")
    },
    "user2": {
        "kp_id": os.getenv("KP_USER2_ID"),
        "name": os.getenv("KP_USER2_NAME", "Пользователь 2")
    }
}

DB_PATH = "movies.db"
OUTPUT_DIR = "output"

KP_API_KEY = os.getenv("KP_API_KEY", "")