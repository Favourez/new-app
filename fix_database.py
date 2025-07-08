#!/usr/bin/env python3
"""
Database Fix Script for JobSync
==============================

This script fixes SQLite database lock issues and ensures proper database setup.
"""

import sqlite3
import os
import time

def fix_database_lock():
    """Fix database lock issues"""
    print("🔧 Fixing SQLite database lock issues...")
    
    # Close any existing connections
    try:
        # Force close any lingering connections
        import gc
        gc.collect()
        
        # Wait a moment for any connections to close
        time.sleep(2)
        
        # Check if database file exists and is accessible
        if os.path.exists('jobportal.db'):
            print("✅ Database file exists")
            
            # Try to open and immediately close a connection to test
            test_conn = sqlite3.connect('jobportal.db', timeout=30)
            test_conn.execute('SELECT 1')
            test_conn.close()
            print("✅ Database is accessible")
            
        else:
            print("❌ Database file not found - will be created")
            
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            print("❌ Database is locked - attempting to fix...")
            
            # Try to unlock by creating a new connection with timeout
            try:
                unlock_conn = sqlite3.connect('jobportal.db', timeout=60)
                unlock_conn.execute('BEGIN IMMEDIATE;')
                unlock_conn.rollback()
                unlock_conn.close()
                print("✅ Database unlocked successfully")
            except Exception as unlock_error:
                print(f"❌ Failed to unlock database: {unlock_error}")
                
                # Last resort: backup and recreate
                if os.path.exists('jobportal.db'):
                    backup_name = f'jobportal_backup_{int(time.time())}.db'
                    os.rename('jobportal.db', backup_name)
                    print(f"📦 Database backed up as {backup_name}")
                    print("🔄 Will create new database")
        else:
            print(f"❌ Database error: {e}")

def recreate_database():
    """Recreate the database with proper settings"""
    print("🔄 Recreating database with proper settings...")
    
    # Remove existing database if it exists
    if os.path.exists('jobportal.db'):
        backup_name = f'jobportal_backup_{int(time.time())}.db'
        os.rename('jobportal.db', backup_name)
        print(f"📦 Old database backed up as {backup_name}")
    
    # Create new database with proper settings
    conn = sqlite3.connect('jobportal.db', timeout=30)
    conn.execute('PRAGMA journal_mode=WAL;')  # Use WAL mode for better concurrency
    conn.execute('PRAGMA synchronous=NORMAL;')  # Faster but still safe
    conn.execute('PRAGMA cache_size=10000;')  # Larger cache
    conn.execute('PRAGMA temp_store=memory;')  # Use memory for temp storage
    
    # Create tables
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            user_type TEXT NOT NULL,
            company_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            skills TEXT,
            experience TEXT,
            education TEXT,
            resume_filename TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );

        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employer_id INTEGER,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            requirements TEXT,
            skills TEXT,
            salary TEXT,
            location TEXT,
            job_type TEXT,
            posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employer_id) REFERENCES users (id)
        );

        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER,
            applicant_id INTEGER,
            employer_id INTEGER,
            compatibility_score INTEGER,
            status TEXT DEFAULT 'pending',
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES jobs (id),
            FOREIGN KEY (applicant_id) REFERENCES users (id),
            FOREIGN KEY (employer_id) REFERENCES users (id)
        );

        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database recreated successfully")

def create_demo_accounts():
    """Create demo accounts"""
    print("👥 Creating demo accounts...")
    
    conn = sqlite3.connect('jobportal.db', timeout=30)
    
    # Hash function (same as in app.py)
    import hashlib
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    # Create demo jobseeker
    try:
        jobseeker_password = hash_password('demo123')
        cursor = conn.execute('''
            INSERT OR IGNORE INTO users (username, email, password, user_type, company_name)
            VALUES (?, ?, ?, ?, ?)
        ''', ('Demo Jobseeker', 'jobseeker@demo.com', jobseeker_password, 'jobseeker', ''))
        
        if cursor.rowcount > 0:
            user_id = cursor.lastrowid
            conn.execute('''
                INSERT OR IGNORE INTO user_profiles (user_id, skills, experience, education)
                VALUES (?, ?, ?, ?)
            ''', (user_id, 'Python, JavaScript, React, SQL', '2+ years experience', 'Computer Science Degree'))
            print("✅ Demo jobseeker created")
        else:
            print("ℹ️ Demo jobseeker already exists")
            
    except Exception as e:
        print(f"❌ Error creating jobseeker: {e}")
    
    # Create demo employer
    try:
        employer_password = hash_password('demo123')
        cursor = conn.execute('''
            INSERT OR IGNORE INTO users (username, email, password, user_type, company_name)
            VALUES (?, ?, ?, ?, ?)
        ''', ('Demo Employer', 'employer@demo.com', employer_password, 'employer', 'Tech Innovations Inc.'))
        
        if cursor.rowcount > 0:
            print("✅ Demo employer created")
        else:
            print("ℹ️ Demo employer already exists")
            
    except Exception as e:
        print(f"❌ Error creating employer: {e}")
    
    conn.commit()
    conn.close()

def main():
    """Main function to fix database issues"""
    print("🚀 JobSync Database Fix Tool")
    print("=" * 40)
    
    try:
        # Step 1: Fix any lock issues
        fix_database_lock()
        
        # Step 2: Recreate database if needed
        recreate_database()
        
        # Step 3: Create demo accounts
        create_demo_accounts()
        
        print("\n🎉 Database fix completed successfully!")
        print("✅ Database is ready for use")
        print("✅ Demo accounts are available:")
        print("   - Jobseeker: jobseeker@demo.com / demo123")
        print("   - Employer: employer@demo.com / demo123")
        
    except Exception as e:
        print(f"\n❌ Database fix failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
