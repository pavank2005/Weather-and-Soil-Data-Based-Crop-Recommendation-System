import sqlite3

def init_db():
    # Connect to database (it will create the file if it doesn't exist)
    conn = sqlite3.connect('farm.db')
    cursor = conn.cursor()
    
    # 1. Create USERS Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT
        )
    ''')
    
    # 2. Create HISTORY Table (With N, P, K, pH columns)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            soil_type TEXT,
            n REAL,
            p REAL,
            k REAL,
            ph REAL,
            temperature REAL,
            humidity REAL,
            rainfall REAL,
            predicted_crop TEXT,
            date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database 'farm.db' created successfully with new columns!")

if __name__ == '__main__':
    init_db()