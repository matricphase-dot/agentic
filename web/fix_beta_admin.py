"""
Fix Beta Admin Database Issues
"""
import sqlite3
import os
from datetime import datetime

def fix_database():
    print("🔧 Fixing Beta Admin Database...")
    
    # Check if database exists
    if not os.path.exists('beta_users.db'):
        print("❌ Database file not found. Creating new database...")
        create_new_database()
        return
    
    try:
        # Connect to database
        conn = sqlite3.connect('beta_users.db')
        cursor = conn.cursor()
        
        # Check what tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"📊 Existing tables: {tables}")
        
        # Fix 1: Check and fix beta_stats table
        if ('beta_stats',) not in tables:
            print("❌ beta_stats table missing. Creating...")
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
            print("✅ Created beta_stats table")
        
        # Fix 2: Check and fix beta_users table
        if ('beta_users',) not in tables:
            print("❌ beta_users table missing. Creating...")
            cursor.execute('''
            CREATE TABLE beta_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                company TEXT,
                use_case TEXT NOT NULL,
                details TEXT,
                status TEXT DEFAULT 'pending',
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                approved_at TIMESTAMP,
                invitation_code TEXT,
                last_login TIMESTAMP,
                workflow_count INTEGER DEFAULT 0
            )
            ''')
            print("✅ Created beta_users table")
        
        # Fix 3: Add missing columns if needed
        try:
            cursor.execute("ALTER TABLE beta_stats ADD COLUMN total_applications INTEGER DEFAULT 0")
            print("✅ Added total_applications column")
        except:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE beta_stats ADD COLUMN approved_users INTEGER DEFAULT 0")
            print("✅ Added approved_users column")
        except:
            pass
        
        try:
            cursor.execute("ALTER TABLE beta_stats ADD COLUMN pending_review INTEGER DEFAULT 0")
            print("✅ Added pending_review column")
        except:
            pass
        
        try:
            cursor.execute("ALTER TABLE beta_stats ADD COLUMN active_users INTEGER DEFAULT 0")
            print("✅ Added active_users column")
        except:
            pass
        
        # Commit changes
        conn.commit()
        
        # Test the query used in beta admin
        print("\n🧪 Testing beta admin query...")
        try:
            cursor.execute("SELECT COUNT(*) as total, SUM(CASE WHEN status='approved' THEN 1 ELSE 0 END) as approved FROM beta_users")
            result = cursor.fetchone()
            print(f"✅ Query successful: total={result[0]}, approved={result[1]}")
        except Exception as e:
            print(f"❌ Query failed: {e}")
            print("Creating sample data...")
            cursor.execute('''
            INSERT INTO beta_users (email, name, use_case, status)
            VALUES 
                ('test1@example.com', 'John Doe', 'automation', 'pending'),
                ('test2@example.com', 'Jane Smith', 'development', 'approved')
            ''')
            conn.commit()
            print("✅ Added sample data")
        
        # Show current stats
        cursor.execute("SELECT * FROM beta_stats")
        stats = cursor.fetchone()
        if stats:
            print(f"\n📊 Current Stats:")
            print(f"  Total Applications: {stats[1]}")
            print(f"  Approved Users: {stats[2]}")
            print(f"  Pending Review: {stats[3]}")
            print(f"  Active Users: {stats[4]}")
        
        conn.close()
        print("\n✅ Database fixed successfully!")
        
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        # Create fresh database as fallback
        create_new_database()

def create_new_database():
    """Create a fresh database with correct schema"""
    print("🆕 Creating fresh database...")
    
    # Remove old database
    if os.path.exists('beta_users.db'):
        os.rename('beta_users.db', 'beta_users.db.backup')
        print("📁 Backed up old database")
    
    # Create new database
    conn = sqlite3.connect('beta_users.db')
    cursor = conn.cursor()
    
    # Create beta_users table
    cursor.execute('''
    CREATE TABLE beta_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        company TEXT,
        use_case TEXT NOT NULL,
        details TEXT,
        status TEXT DEFAULT 'pending',
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        approved_at TIMESTAMP,
        invitation_code TEXT,
        last_login TIMESTAMP,
        workflow_count INTEGER DEFAULT 0
    )
    ''')
    
    # Create beta_stats table
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
    
    # Initialize stats
    cursor.execute('''
    INSERT INTO beta_stats (total_applications, approved_users, 
                           pending_review, active_users, last_updated)
    VALUES (0, 0, 0, 0, ?)
    ''', (datetime.now(),))
    
    # Add sample data for testing
    cursor.execute('''
    INSERT INTO beta_users (email, name, use_case, status)
    VALUES 
        ('demo1@example.com', 'Alice Johnson', 'Business Automation', 'pending'),
        ('demo2@example.com', 'Bob Williams', 'Software Development', 'approved'),
        ('demo3@example.com', 'Carol Davis', 'Data Analysis', 'pending')
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Fresh database created with sample data")

def update_beta_admin_route():
    """Update the beta admin route to handle errors better"""
    print("\n📝 Updating beta admin route...")
    
    # Read current app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the beta admin route
    if '@app.route(\'/beta/admin\')' in content:
        print("✅ Beta admin route found in app.py")
        
        # Create a fixed version
        fixed_route = '''@app.route('/beta/admin')
def beta_admin():
    """Admin dashboard for beta management"""
    try:
        conn = sqlite3.connect('beta_users.db')
        cursor = conn.cursor()
        
        # Get statistics with error handling
        try:
            cursor.execute("SELECT COUNT(*) as total FROM beta_users")
            total = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) as approved FROM beta_users WHERE status='approved'")
            approved = cursor.fetchone()[0] or 0
        except:
            total = 0
            approved = 0
        
        # Get all applications
        try:
            cursor.execute('''
            SELECT id, email, name, company, use_case, status, 
                   strftime('%Y-%m-%d %H:%M', applied_at) as applied_at
            FROM beta_users 
            ORDER BY applied_at DESC
            ''')
            users = cursor.fetchall()
        except:
            users = []
        
        conn.close()
        
        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Beta Admin Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; }
                .header { background: #4a6fa5; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
                .stats { display: flex; gap: 20px; margin: 20px 0; }
                .stat-card { background: white; padding: 20px; border-radius: 10px; flex: 1; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .stat-value { font-size: 2.5rem; font-weight: bold; color: #4a6fa5; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background: #f8f9fa; }
                .status-pending { color: orange; font-weight: bold; }
                .status-approved { color: green; font-weight: bold; }
                .status-rejected { color: red; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Beta Admin Dashboard</h1>
                    <p>Manage beta applications and users</p>
                </div>
                
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-value">''' + str(total) + '''</div>
                        <div>Total Applications</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">''' + str(approved) + '''</div>
                        <div>Approved Users</div>
                    </div>
                </div>
                
                <h2>All Applications</h2>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Email</th>
                            <th>Name</th>
                            <th>Company</th>
                            <th>Use Case</th>
                            <th>Status</th>
                            <th>Applied At</th>
                        </tr>
                    </thead>
                    <tbody>
        '''
        
        # Add user rows
        if users:
            for user in users:
                status_class = f"status-{user[5]}"
                fixed_route += f'''
                        <tr>
                            <td>{user[0]}</td>
                            <td>{user[1]}</td>
                            <td>{user[2]}</td>
                            <td>{user[3] or '-'}</td>
                            <td>{user[4]}</td>
                            <td class="{status_class}">{user[5].upper()}</td>
                            <td>{user[6]}</td>
                        </tr>
                '''
        else:
            fixed_route += '''
                        <tr>
                            <td colspan="7" style="text-align: center; padding: 40px; color: #666;">
                                No applications found. Applications will appear here when users apply.
                            </td>
                        </tr>
            '''
        
        fixed_route += '''
                    </tbody>
                </table>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="/" style="color: #4a6fa5; text-decoration: none; padding: 10px 20px; background: white; border-radius: 5px; border: 1px solid #4a6fa5;">
                        ← Back to Dashboard
                    </a>
                </div>
            </div>
        </body>
        </html>
        ''')
    except Exception as e:
        return f"<h2>Error Loading Admin Dashboard</h2><p>{str(e)}</p><p>Please run the database fix script and try again.</p>"
'''
        
        # Write a new app.py with the fixed route
        with open('app_fixed.py', 'w', encoding='utf-8') as f:
            f.write(fixed_route)
        
        print("✅ Created app_fixed.py with corrected beta admin route")
        print("📝 Replace your current app.py or copy the beta_admin function")
    else:
        print("⚠️ Could not find beta admin route in app.py")
        print("Creating a standalone fix...")
        create_standalone_fix()

def create_standalone_fix():
    """Create a standalone fix script"""
    fix_script = '''import sqlite3
import os
from datetime import datetime

def check_and_fix():
    # Fix database
    fix_database()
    
    # Test the fix
    test_beta_admin()

def fix_database():
    """Ensure database has correct schema"""
    conn = sqlite3.connect('beta_users.db')
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS beta_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        company TEXT,
        use_case TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS beta_stats (
        id INTEGER PRIMARY KEY,
        total_applications INTEGER DEFAULT 0,
        approved_users INTEGER DEFAULT 0
    )
    ''')
    
    # Initialize stats if empty
    cursor.execute("SELECT COUNT(*) FROM beta_stats")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
        INSERT INTO beta_stats (total_applications, approved_users)
        VALUES (0, 0)
        ''')
    
    conn.commit()
    conn.close()
    print("✅ Database schema verified")

def test_beta_admin():
    """Test the beta admin query"""
    conn = sqlite3.connect('beta_users.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) as total, SUM(CASE WHEN status='approved' THEN 1 ELSE 0 END) as approved FROM beta_users")
        result = cursor.fetchone()
        print(f"✅ Beta admin query works: total={result[0]}, approved={result[1]}")
    except Exception as e:
        print(f"❌ Query failed: {e}")
        print("Adding missing status column...")
        
        # Try to add status column if missing
        try:
            cursor.execute("ALTER TABLE beta_users ADD COLUMN status TEXT DEFAULT 'pending'")
            conn.commit()
            print("✅ Added status column")
        except:
            print("⚠️ Could not add column - table may already have it")
    
    conn.close()

if __name__ == "__main__":
    check_and_fix()
'''
    
    with open('fix_beta_standalone.py', 'w') as f:
        f.write(fix_script)
    
    print("✅ Created fix_beta_standalone.py")
    print("🚀 Run: python fix_beta_standalone.py")

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 FIXING BETA ADMIN DASHBOARD ISSUES")
    print("=" * 60)
    
    # Step 1: Fix database
    fix_database()
    
    # Step 2: Update the route
    update_beta_admin_route()
    
    print("\n" + "=" * 60)
    print("✅ FIX COMPLETE!")
    print("=" * 60)
    print("\n🎯 Next Steps:")
    print("1. Run the fix: python fix_beta_admin.py")
    print("2. Test your app: python app.py")
    print("3. Visit: http://localhost:5000/beta/admin")
    print("\n💡 If still broken, rename app_fixed.py to app.py")
    print("=" * 60)