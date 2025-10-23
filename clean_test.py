#!/usr/bin/env python3
"""Clean test data"""

import sqlite3

conn = sqlite3.connect('data/agricultural_documents.db')
cursor = conn.cursor()
cursor.execute('DELETE FROM varieties WHERE variety_name = "TEST"')
conn.commit()
conn.close()
print('Test data cleaned')
