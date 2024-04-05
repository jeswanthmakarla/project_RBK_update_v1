import sqlite3

db_path = './database.db'

with sqlite3.connect(db_path) as conn:
    with open('output.sql', 'w') as f:
        for line in conn.iterdump():
            f.write(f'{line}\n')
