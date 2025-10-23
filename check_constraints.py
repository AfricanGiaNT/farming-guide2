#!/usr/bin/env python3
"""Check database constraints"""

import sqlite3

def check_constraints():
    conn = sqlite3.connect('data/agricultural_documents.db')
    cursor = conn.cursor()
    
    # Get table creation SQL
    cursor.execute('SELECT sql FROM sqlite_master WHERE type="table" AND name="varieties"')
    result = cursor.fetchone()
    
    if result:
        print("Varieties table creation SQL:")
        print(result[0])
    else:
        print("Table not found")
    
    conn.close()

if __name__ == "__main__":
    check_constraints()
