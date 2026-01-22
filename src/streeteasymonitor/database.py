import os
import sqlite3


class Database:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.base_dir, '../..', 'data')
        self.db_path = os.path.join(self.data_dir, 'db.sqlite3')

        os.makedirs(self.data_dir, exist_ok=True)
        self.create_table()

    def create_table(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS listings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    listing_id TEXT UNIQUE,
                    url TEXT,
                    price REAL,
                    address TEXT,
                    neighborhood TEXT,
                    listed_by TEXT
                )
            """)
            conn.commit()

    def get_existing_ids(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT listing_id FROM listings')
            return set(row[0] for row in cursor.fetchall())

    def get_listings_sorted(self, limit=None):
        """Get all listings sorted by created_at descending.

        Args:
            limit (int, optional): Maximum number of results to return. Defaults to None (all results).

        Returns:
            list[dict]: List of listing dictionaries.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if limit:
                cursor.execute('SELECT * FROM listings ORDER BY created_at DESC LIMIT ?', (limit,))
            else:
                cursor.execute('SELECT * FROM listings ORDER BY created_at DESC')
            return [dict(row) for row in cursor.fetchall()]

    def get_statistics(self):
        """Get database statistics.

        Returns:
            dict: Statistics including total count, average price, etc.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Total count
            cursor.execute('SELECT COUNT(*) FROM listings')
            total = cursor.fetchone()[0]

            # Average price
            cursor.execute('SELECT AVG(price) FROM listings')
            avg_price = cursor.fetchone()[0] or 0

            # Unique neighborhoods count
            cursor.execute('SELECT COUNT(DISTINCT neighborhood) FROM listings WHERE neighborhood IS NOT NULL')
            neighborhoods = cursor.fetchone()[0]

            return {
                'total_listings': total,
                'avg_price': avg_price,
                'neighborhoods_count': neighborhoods
            }

    def insert_new_listing(self, listing):
        # Whitelist allowed columns to prevent SQL injection
        ALLOWED_COLUMNS = {'listing_id', 'url', 'price', 'address', 'neighborhood', 'listed_by'}

        # Remove is_featured field and any other non-whitelisted fields
        listing_to_insert = {
            k: v for k, v in listing.items()
            if k in ALLOWED_COLUMNS
        }

        if not listing_to_insert:
            raise ValueError('No valid columns to insert')

        # Build query with whitelisted columns
        columns = ', '.join(listing_to_insert.keys())
        placeholders = ', '.join('?' * len(listing_to_insert))
        sql = f'INSERT OR IGNORE INTO listings ({columns}) VALUES ({placeholders})'

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(sql, tuple(listing_to_insert.values()))
            conn.commit()

            # Check if insert was successful (rowcount > 0)
            if cursor.rowcount > 0:
                from .utils import get_datetime
                print(f'{get_datetime()} ✓ Saved listing: {listing.get("listing_id")} ({listing.get("address")})')
            # If rowcount == 0, it means IGNORE was triggered (duplicate key)
