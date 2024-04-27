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
        parse_date = datetime.strptime(date, '%Y-%m-%d') # Parses the time into the specified format.
        database_date = datetime.strftime(parse_date, '%Y%m%d') # Formats the parsed time into the specified format.

        db.execute('insert into log_date (entry_date) VALUES (?)', [database_date])
        db.commit()

    totals_cursor = db.execute('''select l.entry_date, sum(f.protein) as protein, sum(f.carbohydrates) as carbohydrates, \
                                    sum(f.fat) as fat, sum(f.calories) as calories \
                                    from log_date as l \
                                    join food_date as d on d.log_date_id = l.id \
                                    join food as f on d.food_id = f.id \
                                    group by l.entry_date
                                    order by l.entry_date desc;''')
    totals_results = totals_cursor.fetchall()

    results = []

    for i in totals_results:
        single_date = {}
        single_date['formatted_date'] = datetime.strftime(datetime.strptime(str(i['entry_date']), '%Y%m%d'), '%B %d, %Y')
        single_date['database_date'] = i['entry_date']
        single_date['protein'] = i['protein']
        single_date['carbohydrates'] = i['carbohydrates']
        single_date['fat'] = i['fat']
        single_date['calories'] = i['calories']

        results.append(single_date)

    dates_cursor = db.execute('select entry_date from log_date order by entry_date desc;')
    dates_results = dates_cursor.fetchall()

    dates_in_list = [x['database_date'] for x in results]
    for date in dates_results:
        if date['entry_date'] not in dates_in_list:
            single_date = {}
            single_date['formatted_date'] = datetime.strftime(datetime.strptime(str(date['entry_date']), '%Y%m%d'), '%B %d, %Y')
            single_date['database_date'] = date['entry_date']
            single_date['protein'] = 0
            single_date['carbohydrates'] = 0
            single_date['fat'] = 0
            single_date['calories'] = 0

            results.append(single_date)

    return render_template('home.html', results=results)

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

@app.route('/view/<date>', methods=['POST', 'GET'])
def view(date):
    db = get_db()

    # Fetching and formatting the entered date for display in the template.
    cursor = db.execute('select id, entry_date from log_date where entry_date = ?;', [date])
    database_date = cursor.fetchone()

    if request.method == "POST":
        db.execute('insert into food_date (food_id, log_date_id) VALUES (?, ?)', \
                   [request.form['food-select'], database_date['id']])
        db.commit() 

    formatted_date = datetime.strftime(datetime.strptime(str(database_date['entry_date']), '%Y%m%d'), '%B %d, %Y')

    # Getting a list of all food items in the database.
    food_cursor = db.execute('select id, name from food;')
    food_results = food_cursor.fetchall()

    food_list_cursor = db.execute('''select f.name, f.protein, f.carbohydrates, f.fat, f.calories \
                                  from log_date as l \
                                  join food_date as d on d.log_date_id = l.id \
                                  join food as f on d.food_id = f.id \
                                  where l.entry_date = ?;''', [date])
    food_list_results = food_list_cursor.fetchall()

    totals_dict = {
        "protein": 0,
        "carbohydrates": 0,
        "fat": 0,
        "calories": 0
    }

    for item in food_list_results:
        totals_dict["protein"] += int(item['protein'])
        totals_dict["carbohydrates"] += int(item['carbohydrates'])
        totals_dict["fat"] += int(item['fat'])
        totals_dict["calories"] += int(item['calories'])

    return render_template('day.html', formatted_date=formatted_date, database_date=database_date['entry_date'], \
                           food_results=food_results, food_list=food_list_results, totals_dict=totals_dict)


if __name__ == '__main__':
    app.run(debug=True)