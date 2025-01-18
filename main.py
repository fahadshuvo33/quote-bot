# update_categories.py
from config.settings import DEFAULT_CATEGORIES, DATABASE_FILE
from quotes.manager import Database


def update_categories():
    # Initialize the database
    db = Database(db_file=DATABASE_FILE)

    # Add categories to the database
    for category in DEFAULT_CATEGORIES:
        db.add_category(category)

    # Fetch updated categories from the database
    categories = db.get_all_categories()
    return [
        category["name"] for category in categories
    ]  # Adjust structure based on how you store them


if __name__ == "__main__":
    updated_categories = update_categories()
    print(f"Updated categories: {updated_categories}")
