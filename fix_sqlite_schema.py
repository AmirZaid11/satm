import sqlite3
import os

db_path = 'db.sqlite3'
if not os.path.exists(db_path):
    print(f"Error: {db_path} not found")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get current table info
cursor.execute('PRAGMA table_info(users_user)')
columns = cursor.fetchall()
col_names = [c[1] for c in columns if c[1] != 'course_id']

if len(col_names) == len(columns):
    print("Column course_id not found, nothing to do.")
    conn.close()
    exit(0)

# Create new table without course_id
col_defs = []
for c in columns:
    if c[1] == 'course_id':
        continue
    name = f'"{c[1]}"'
    dtype = c[2]
    notnull = ' NOT NULL' if c[3] else ''
    pk = ' PRIMARY KEY' if c[5] else ''
    # Default values can be tricky to reconstruct perfectly from PRAGMA
    # but for most Django standard fields it's manageable.
    col_defs.append(f'{name} {dtype}{notnull}{pk}')

col_defs_str = ', '.join(col_defs)
cursor.execute(f'CREATE TABLE users_user_new ({col_defs_str})')

# Copy data
col_names_quoted = ', '.join([f'"{n}"' for n in col_names])
cursor.execute(f'INSERT INTO users_user_new ({col_names_quoted}) SELECT {col_names_quoted} FROM users_user')

# Swap tables
cursor.execute('DROP TABLE users_user')
cursor.execute('ALTER TABLE users_user_new RENAME TO users_user')

conn.commit()
conn.close()
print("Successfully dropped course_id column.")
