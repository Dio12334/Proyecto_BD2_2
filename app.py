from flask import Flask, render_template, request
import json
from inverted_index import *



app = Flask(__name__)
app.secret_key = ".."


file = open("static/data/rpta.json", "r", encoding='UTF-8')
jsondata = file.read()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    do_query(query, 10)
    return render_template("results.html")

@app.route('/requestjson', methods=['GET'])
def jsonreturn():
    file = open("static/data/rpta.json", "r", encoding='UTF-8')
    jsondata = file.read()
    return jsondata

if __name__ == '__main__':
    app.secret_key = ".."
    app.run(host='192.168.1.18',port=5000)