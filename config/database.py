import sqlite3
from typing import List, Dict, Optional
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_file: str = os.getenv("DATABASE_FILE", "quotes.db")):
        self.db_file = db_file
        self.QUOTES_PER_CATEGORY = 10  # Maximum number of quotes per category
        self.create_tables()

    def connect(self):
        try:
            return sqlite3.connect(self.db_file)
        except sqlite3.Error as e:
            logger.error(f"Error connecting to database: {e}")
            return None

    def create_tables(self):
        sql_create_categories = """
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );"""

        sql_create_quotes = """
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quote TEXT NOT NULL UNIQUE,
            author TEXT NOT NULL,
            category_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        );"""

        try:
            with self.connect() as conn:
                c = conn.cursor()
                c.execute(sql_create_categories)
                c.execute(sql_create_quotes)
                conn.commit()
                logger.info("Tables created successfully.")
        except sqlite3.Error as e:
            logger.error(f"Error creating tables: {e}")

    def count_quotes_in_category(self, category_id: int) -> int:
        sql = "SELECT COUNT(*) FROM quotes WHERE category_id = ?"
        try:
            with self.connect() as conn:
                c = conn.cursor()
                c.execute(sql, (category_id,))
                return c.fetchone()[0]
        except sqlite3.Error as e:
            logger.error(f"Error counting quotes in category: {e}")
            return 0

    def remove_oldest_quote_from_category(self, category_id: int):
        sql = """
        DELETE FROM quotes 
        WHERE id IN (
            SELECT id FROM quotes 
            WHERE category_id = ? 
            ORDER BY timestamp ASC 
            LIMIT 1
        )"""
        try:
            with self.connect() as conn:
                c = conn.cursor()
                c.execute(sql, (category_id,))
                conn.commit()
                logger.info(f"Oldest quote removed from category ID {category_id}.")
        except sqlite3.Error as e:
            logger.error(f"Error removing oldest quote from category: {e}")

    def add_category(self, category_name: str) -> bool:
        try:
            with self.connect() as conn:
                c = conn.cursor()
                c.execute(
                    "INSERT OR IGNORE INTO categories (name) VALUES (?)",
                    (category_name,),
                )
                conn.commit()
                logger.info(f"Category '{category_name}' added successfully.")
                return True
        except sqlite3.Error as e:
            logger.error(f"Error adding category: {e}")
            return False

    def add_quote(self, quote: str, author: str, category: str) -> bool:
        try:
            with self.connect() as conn:
                c = conn.cursor()

                # Check if quote already exists
                c.execute("SELECT 1 FROM quotes WHERE quote = ?", (quote,))
                if c.fetchone():
                    logger.warning("Quote already exists.")
                    return False

                # Get category id or create new category
                c.execute(
                    "INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,)
                )
                c.execute("SELECT id FROM categories WHERE name = ?", (category,))
                category_id = c.fetchone()[0]

                # Check if we need to remove an old quote from this category
                if (
                    self.count_quotes_in_category(category_id)
                    >= self.QUOTES_PER_CATEGORY
                ):
                    self.remove_oldest_quote_from_category(category_id)

                # Add the new quote
                sql = "INSERT INTO quotes (quote, author, category_id) VALUES (?, ?, ?)"
                c.execute(sql, (quote, author, category_id))
                conn.commit()
                logger.info(f"Quote added to category '{category}'.")
                return True
        except sqlite3.Error as e:
            logger.error(f"Error adding quote: {e}")
            return False

    def get_all_quotes(self) -> List[Dict]:
        sql = """
        SELECT q.quote, q.author, c.name as category, q.timestamp
        FROM quotes q
        JOIN categories c ON q.category_id = c.id
        ORDER BY c.name, q.timestamp DESC
        """
        try:
            with self.connect() as conn:
                c = conn.cursor()
                c.execute(sql)
                return [
                    {
                        "quote": row[0],
                        "author": row[1],
                        "category": row[2],
                        "timestamp": row[3],
                    }
                    for row in c.fetchall()
                ]
        except sqlite3.Error as e:
            logger.error(f"Error getting quotes: {e}")
            return []

    def get_random_quote(self, category: Optional[str] = None) -> Optional[Dict]:
        if category:
            sql = """
            SELECT q.quote, q.author, c.name as category
            FROM quotes q
            JOIN categories c ON q.category_id = c.id
            WHERE c.name = ?
            ORDER BY RANDOM()
            LIMIT 1
            """
            params = (category,)
        else:
            sql = """
            SELECT q.quote, q.author, c.name as category
            FROM quotes q
            JOIN categories c ON q.category_id = c.id
            ORDER BY RANDOM()
            LIMIT 1
            """
            params = ()

        try:
            with self.connect() as conn:
                c = conn.cursor()
                c.execute(sql, params)
                row = c.fetchone()
                if row:
                    return {"quote": row[0], "author": row[1], "category": row[2]}
                return None
        except sqlite3.Error as e:
            logger.error(f"Error getting random quote: {e}")
            return None

    def get_quotes_by_category(self, category: str) -> List[Dict]:
        sql = """
        SELECT q.quote, q.author, q.timestamp
        FROM quotes q
        JOIN categories c ON q.category_id = c.id
        WHERE c.name = ?
        ORDER BY q.timestamp DESC
        """
        try:
            with self.connect() as conn:
                c = conn.cursor()
                c.execute(sql, (category,))
                return [
                    {"quote": row[0], "author": row[1], "timestamp": row[2]}
                    for row in c.fetchall()
                ]
        except sqlite3.Error as e:
            logger.error(f"Error getting quotes by category: {e}")
            return []

    def initialize_default_data(self, categories: Optional[List[str]] = None):
        """Initialize the database with default categories."""
        if categories is None:
            categories = [
                "inspiration",
                "motivation",
                "wisdom",
                "success",
                "leadership",
                "life",
                "love",
                "happiness",
            ]

        for category in categories:
            self.add_category(category)
