import os
import sqlite3
from pathlib import Path

# database configuration
def databaseConfig():
    db_path = Path(__file__).resolve().parent / 'carting.db'
    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(str(db_path), check_same_thread=False)
    connection.row_factory = sqlite3.Row  # Enable dict-like row access
    connection.execute('PRAGMA foreign_keys = ON')
    return connection

def dict_from_row(row):
    """Convert sqlite3.Row to dictionary"""
    if row is None:
        return None
    return dict(row)
