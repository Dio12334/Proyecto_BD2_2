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
    page = 0
    query = request.args['query']
    number_of_pages = do_query(query, int(config['results']['NumberOfReturnedTweets']))/int(config['results']['NumberOfTweetsDisplayedPerPage'])
    content_per_page = config['results']['NumberOfTweetsDisplayedPerPage']
    if 'page' in request.args:
        page = request.args['page']
    return render_template("results.html", page=page, number_of_pages=number_of_pages, content_per_page=content_per_page)

@app.route('/requestjson', methods=['GET'])
def jsonreturn():
    file = open("static/data/rpta.json", "r", encoding='UTF-8')
    jsondata = file.read()
    return jsondata

@app.route('/config', methods=['GET'])
def config_page():
    number_of_tweets_searched = config['results']['NumberOfReturnedTweets']
    number_of_tweets_per_page = config['results']['numberoftweetsdisplayedperpage']
    theme = config['search']['theme']
    numberoftweetsindatabase = config['search']['numberoftweetsindatabase']

    return render_template('config.html', number_of_tweets_per_page = number_of_tweets_per_page
                                        , number_of_tweets_searched = number_of_tweets_searched
                                        , theme = theme
                                        , numberoftweetsindatabase = numberoftweetsindatabase)


@app.route('/change_config', methods=['POST'])
def setnumberofreturnedtweets():
    ns = request.form['number_of_tweets_searched']
    nr = request.form['number_of_tweets_per_page']
    th = request.form['theme']
    mtweets = request.form['max_tweets']

    if (mtweets != config['search']['numberoftweetsindatabase'] or th != config['search']['theme']):
        change_index_theme(th, int(mtweets))

    config['results']['NumberOfReturnedTweets'] = ns
    config['results']['numberoftweetsdisplayedperpage'] = nr
    config['search']['theme'] = th 
    config['search']['numberoftweetsindatabase'] = mtweets
    with open('config/TwitterSearch.INI', 'w') as configfile:
        config.write(configfile)
    
    
    return redirect('/')



if __name__ == '__main__':
    app.secret_key = ".."
    app.run(host='192.168.1.18',port=5000)