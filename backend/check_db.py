#!/usr/bin/env python3
import psycopg2

try:
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host='localhost',
        dbname='backend_db',
        user='postgres',
        password='Raja@2005'  # Actual password (not URL-encoded)
    )
    
    cur = conn.cursor()
    
    # Get all tables
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema='public'
    """)
    
    tables = cur.fetchall()
    print("\n" + "="*50)
    print("TABLES IN DATABASE")
    print("="*50)
    
    if tables:
        for table in tables:
            print(f"✓ {table[0]}")
    else:
        print("❌ No tables found!")
    
    # Get users data
    print("\n" + "="*50)
    print("USERS TABLE DATA")
    print("="*50)
    
    try:
        cur.execute("SELECT id, username FROM users")
        users = cur.fetchall()
        if users:
            for user in users:
                print(f"ID: {user[0]}, Username: {user[1]}")
        else:
            print("No users found")
    except Exception as e:
        print(f"Error reading users: {e}")
    
    # Get courses data
    print("\n" + "="*50)
    print("COURSES TABLE DATA")
    print("="*50)
    
    try:
        cur.execute("SELECT id, title, description, owner_id FROM courses")
        courses = cur.fetchall()
        if courses:
            for course in courses:
                print(f"ID: {course[0]}, Title: {course[1]}, Owner: {course[3]}")
        else:
            print("No courses found")
    except Exception as e:
        print(f"Error reading courses: {e}")
    
    print("\n" + "="*50)
    
    cur.close()
    conn.close()
    
except psycopg2.Error as e:
    print(f"❌ Database connection error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
