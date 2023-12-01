import os
import sqlite3
import sqlparse

# SQLite
INIT_SQL: str = 'init.sql'
MAIN_DB: str = 'protein_turnover.db'
SQLITE_PATH: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), MAIN_DB)
INIT_SQL_PATH: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), INIT_SQL)

class ProteinTurnoverDataClass:
    def __init__(self) -> None:
        self.conn = None
        if not os.path.exists(SQLITE_PATH):
            self.initialize()
        
    def initialize(self) -> None:
        conn = sqlite3.connect(SQLITE_PATH)
        with open(INIT_SQL_PATH) as f:
            sql_text = f.read()
        for sql in sqlparse.split(sql_text):
            conn.execute(sql)
        conn.commit()
        conn.close()
        
    def create_clickhouse_information(self, data: list) -> None:
        conn = sqlite3.connect(SQLITE_PATH)
        insert_data_query = """
INSERT INTO clickhouse_connections (name, host, port, username, password)
VALUES (?, ?, ?, ?, ?);
"""
        conn.execute(insert_data_query, data)
        conn.commit()
        conn.close()
        
    def read_all_clickhouse_information(self) -> list:
        conn = sqlite3.connect(SQLITE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clickhouse_connections")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
        
    def delete_clickhouse_information(self, id: int) -> None:
        conn = sqlite3.connect(SQLITE_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM clickhouse_connections WHERE id = ?", (id,))
        conn.commit()
        cursor.close()
        conn.close()
    
    def __del__(self) -> None:
        if self.conn is not None:
            self.conn.close()
    