import sqlite3
from datetime import datetime

# Connect to database
conn = sqlite3.connect('beta_users.db')
cursor = conn.cursor()

# Drop old beta_stats table if exists
cursor.execute("DROP TABLE IF EXISTS beta_stats")

# Create new beta_stats table with correct schema
cursor.execute('''
CREATE TABLE beta_stats (
    id INTEGER PRIMARY KEY,
    total_applications INTEGER DEFAULT 0,
    approved_users INTEGER DEFAULT 0,
    pending_review INTEGER DEFAULT 0,
    active_users INTEGER DEFAULT 0,
    last_updated TIMESTAMP
)
''')

# Initialize with default values
cursor.execute('''
INSERT INTO beta_stats (total_applications, approved_users, 
                       pending_review, active_users, last_updated)
VALUES (0, 0, 0, 0, ?)
''', (datetime.now(),))

conn.commit()
conn.close()
print("✅ Database schema updated successfully!")