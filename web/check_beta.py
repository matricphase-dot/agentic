"""
Check Beta Testing Database
"""
import sqlite3
import os

def check_beta_database():
    print("🔍 Checking Beta Testing Database...")
    
    db_path = "beta_users.db"
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"✅ Database found: {db_path}")
        print(f"📊 Tables: {[table[0] for table in tables]}")
        
        # Check for users table
        for table in tables:
            table_name = table[0]
            print(f"\n📋 Table: {table_name}")
            
            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            print(f"  Columns: {[col[1] for col in columns]}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"  Rows: {count}")
            
            # Show sample data
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
                sample = cursor.fetchall()
                print(f"  Sample (first 3):")
                for row in sample:
                    print(f"    {row}")
        
        conn.close()
        return tables
        
    except Exception as e:
        print(f"❌ Error reading database: {e}")
        return None

if __name__ == "__main__":
    check_beta_database()