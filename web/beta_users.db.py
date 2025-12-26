python -c 
import sqlite3
conn = sqlite3.connect('beta_users.db')
cursor = conn.cursor()
cursor.execute('CREATE TABLE beta_users (id INTEGER PRIMARY KEY, email TEXT, name TEXT, use_case TEXT, status TEXT)')
cursor.execute('CREATE TABLE beta_stats (id INTEGER PRIMARY KEY, total INTEGER, approved INTEGER)')
cursor.execute('INSERT INTO beta_stats (total, approved) VALUES (2, 1)')
cursor.execute('INSERT INTO beta_users (email, name, use_case, status) VALUES (\"test@example.com\", \"Test User\", \"automation\", \"pending\")')
conn.commit()
conn.close()
print('✅ Fresh database created')