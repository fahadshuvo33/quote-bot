# import os
# from dotenv import load_dotenv

# load_dotenv()

# # Bot tokens
# TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
# DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
# DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")

# # API settings
# QUOTES_API_URL = "https://api.api-ninjas.com/v1/quotes"
# API_NINJA_KEY = os.getenv("API_NINJA_KEY")  # Add API Ninja key in .env
# API_TIMEOUT = 5  # Timeout for API requests in seconds

# # Scheduler settings
# DEFAULT_QUOTE_TIME = "06:00"  # Default time for daily quotes
# TIMEZONE = "UTC"  # Default timezone for scheduling

# # Quote categories
# CATEGORIES = [
#     "age",
#     "alone",
#     "amazing",
#     "anger",
#     "architecture",
#     "art",
#     "attitude",
#     "beauty",
#     "best",
#     "birthday",
#     "business",
#     "car",
#     "change",
#     "communication",
#     "computers",
#     "cool",
#     "courage",
#     "dad",
#     "dating",
#     "death",
#     "design",
#     "dreams",
#     "education",
#     "environmental",
#     "equality",
#     "experience",
#     "failure",
#     "faith",
#     "family",
#     "famous",
#     "fear",
#     "fitness",
#     "food",
#     "forgiveness",
#     "freedom",
#     "friendship",
#     "funny",
#     "future",
#     "god",
#     "good",
#     "government",
#     "graduation",
#     "great",
#     "happiness",
#     "health",
#     "history",
#     "home",
#     "hope",
#     "humor",
#     "imagination",
#     "inspirational",
#     "intelligence",
#     "jealousy",
#     "knowledge",
#     "leadership",
#     "learning",
#     "legal",
#     "life",
#     "love",
#     "marriage",
#     "medical",
#     "men",
#     "mom",
#     "money",
#     "morning",
#     "movies",
#     "success",
# ]

# # User preferences defaults
# DEFAULT_PREFERENCES = {
#     "category": "inspirational",  # Default category
#     "notification_time": DEFAULT_QUOTE_TIME,  # Default daily quote time
#     "timezone": TIMEZONE,  # Default timezone
# }

# # Logging settings
# LOG_LEVEL = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL


import os
from dotenv import load_dotenv
from .database import Database  # Update the path as per your project structure
from typing import List
import sqlite3
from logging import Logger

load_dotenv()

# Bot tokens
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")

# API settings
QUOTES_API_URL = "https://api.api-ninjas.com/v1/quotes"
API_NINJA_KEY = os.getenv("API_NINJA_KEY")
API_TIMEOUT = 5

# Scheduler settings
DEFAULT_QUOTE_TIME = "06:00"
TIMEZONE = "Asia/Dhaka"


# Initialize the database connection
db = Database()

# Fetch categories dynamically
CATEGORIES = db.get_all_categories()

# User preferences defaults
DEFAULT_PREFERENCES = {
    "category": "inspirational" if "inspirational" in CATEGORIES else CATEGORIES[0],
    "notification_time": DEFAULT_QUOTE_TIME,
    "timezone": TIMEZONE,
}

# Logging settings
LOG_LEVEL = "INFO"


def get_all_categories(self) -> List[str]:
    """Fetch all category names from the database."""
    sql = "SELECT name FROM categories ORDER BY name"
    try:
        with self.connect() as conn:
            c = conn.cursor()
            c.execute(sql)
            return [row[0] for row in c.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Error fetching categories: {e}")
        return []
