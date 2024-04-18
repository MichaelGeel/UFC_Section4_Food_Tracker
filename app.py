from flask import Flask, url_for, redirect, g, session, render_template, request, jsonify
import sqlite3
from datetime import datetime


app = Flask(__name__)


def connect_db():
    sql = sqlite3.connect('D:/Learning/The Ultimate Flask Course/Section4_Food_Tracker/food_log.db')
    sql.row_factory = sqlite3.Row
    return sql

def get_db():
    if not hasattr(g, 'sqlite3_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/', methods=['POST', 'GET'])
def index():
    db = get_db()

    if request.method == 'POST':
        date = request.form['date']
        parse_date = datetime.strptime(date, '%Y-%m-%d')
        database_date = datetime.strftime(parse_date, '%Y%m%d')

        db.execute('insert into log_date (entry_date) VALUES (?)', [database_date])
        db.commit()

    cursor = db.execute('select entry_date from log_date')
    results = cursor.fetchall()

    #dates = [datetime.strftime()]

    return results#render_template('home.html', results=results)

@app.route('/food', methods=['GET', 'POST'])
def food():
    db = get_db()

    if request.method == "POST":
        
        # Retreiving the form data entered via the POST method.
        name = request.form['food-name']
        carbs = int(request.form['carbohydrates'])
        protein = int(request.form['protein'])
        fat = int(request.form['fat'])

        calories = (protein*4) + (carbs*4) + (fat*9)

        # Inserting the values into the database as a new food item.
        db.execute('insert into food (name, protein, carbohydrates, fat, calories) VALUES (?, ?, ?, ?, ?)', \
                   [name, protein, carbs, fat, calories])
        db.commit()

        # Fetching all items from the database.
    cur = db.execute('select name, protein, carbohydrates, fat, calories from food;')
    results = cur.fetchall()
        
    # Returning the form with the food items from the database.
    return render_template('add_food.html', results=results)

@app.route('/view')
def view():
    return render_template('day.html')


if __name__ == '__main__':
    app.run(debug=True)