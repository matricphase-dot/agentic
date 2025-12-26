"""
Fix Beta Testing Database Schema
"""
import sqlite3
import os
from datetime import datetime

def fix_beta_database():
    db_path = "beta_users.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    print(f"🔧 Fixing database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current schema
        cursor.execute("PRAGMA table_info(beta_users);")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"Current columns: {column_names}")
        
        # Create a backup of the old table
        cursor.execute("CREATE TABLE IF NOT EXISTS beta_users_backup AS SELECT * FROM beta_users;")
        print("✅ Created backup table")
        
        # Check if we need to add status column
        if 'status' not in column_names:
            print("➕ Adding 'status' column...")
            cursor.execute("ALTER TABLE beta_users ADD COLUMN status TEXT DEFAULT 'active';")
            
            # Update existing records
            cursor.execute("UPDATE beta_users SET status = 'active' WHERE status IS NULL;")
            print("✅ Added 'status' column")
        
        # Check for other missing columns
        needed_columns = ['company', 'role', 'invitation_code', 'usage_count']
        for column in needed_columns:
            if column not in column_names:
                print(f"➕ Adding '{column}' column...")
                if column == 'usage_count':
                    cursor.execute(f"ALTER TABLE beta_users ADD COLUMN {column} INTEGER DEFAULT 0;")
                else:
                    cursor.execute(f"ALTER TABLE beta_users ADD COLUMN {column} TEXT DEFAULT '';")
        
        # Check for beta_metrics table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='beta_metrics';")
        if not cursor.fetchone():
            print("📊 Creating beta_metrics table...")
            cursor.execute('''
            CREATE TABLE beta_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                active_users INTEGER DEFAULT 0,
                workflows_created INTEGER DEFAULT 0,
                workflows_executed INTEGER DEFAULT 0
            )
            ''')
            
            # Insert initial metrics
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute(
                "INSERT INTO beta_metrics (date, active_users) VALUES (?, ?)",
                (today, 0)
            )
            print("✅ Created beta_metrics table")
        
        conn.commit()
        conn.close()
        
        print("✅ Database schema fixed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        return False

if __name__ == "__main__":
    fix_beta_database()
    print("\n📊 Database is now ready for the complete system!")