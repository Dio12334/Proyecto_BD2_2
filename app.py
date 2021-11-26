from flask import Flask, render_template, request, redirect
import json
from inverted_index import *
import configparser



app = Flask(__name__)
app.secret_key = ".."
config = configparser.ConfigParser()
config.read('config/TwitterSearch.INI')



@app.route('/')
def home():
    return render_template('home.html')

@app.route('/search', methods=['GET'])
def search():
    number_of_pages = 1
    page = 1
    query = request.args['query']
    number_of_pages = do_query(query, int(config['results']['NumberOfReturnedTweets']))/int(config['results']['NumberOfTweetsDisplayedPerPage'])
    if 'page' in request.args:
        page = request.args['page']
    return render_template("results.html", page=page, number_of_pages=number_of_pages)

@app.route('/requestjson', methods=['GET'])
def jsonreturn():
    file = open("static/data/rpta.json", "r", encoding='UTF-8')
    jsondata = file.read()
    return jsondata

@app.route('/config', methods=['GET'])
def config_page():
    return render_template('config.html')


@app.route('/change_config', methods=['POST'])
def setnumberofreturnedtweets():
    ns = request.form['number_of_tweets_searched']
    nr = request.form['number_of_tweets_per_page']
    config['results']['NumberOfReturnedTweets'] = ns
    config['results']['numberoftweetsdisplayedperpage'] = nr
    with open('config/TwitterSearch.INI', 'w') as configfile:
        config.write(configfile)
    return redirect('/')



if __name__ == '__main__':
    app.secret_key = ".."
    app.run(host='192.168.1.18',port=5000)