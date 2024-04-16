from flask import Flask, url_for, redirect, g, session, render_template, request, jsonify
import sqlite3


app = Flask(__name__)


def connect_db():
    sql = sqlite3.connect('D:\Learning\The Ultimate Flask Course\Section4_Food_Tracker/food_log.db')
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

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/food', methods=['GET', 'POST'])
def food():
    if request.method == "POST":

        name = request.form['food-name']
        carbs = request.form['carbohydrates']
        protein = request.form['protein']
        fat = request.form['fat']
        calories = (protein*4) + (carbs*4) + (fat*9)

        db = get_db()
        
        return "<h1>{}{}{}{}</h1>".format(request.form['food-name'], request.form['protein'], request.form['carbohydrates'], request.form['fat'])
    else:
        return render_template('add_food.html')

@app.route('/view')
def view():
    return render_template('day.html')


if __name__ == '__main__':
    app.run(debug=True)