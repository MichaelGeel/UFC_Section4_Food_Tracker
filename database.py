import sqlite3
from flask import g

def connect_db():
    sql = sqlite3.connect('D:/Learning/The Ultimate Flask Course/Section4_Food_Tracker/food_log.db')
    sql.row_factory = sqlite3.Row
    return sql

def get_db():
    if not hasattr(g, 'sqlite3_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db