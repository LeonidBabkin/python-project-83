from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
import psycopg2
from datetime import datetime
from urllib.parse import urlparse
from psycopg2.extras import NamedTupleCursor


load_dotenv()
conn = psycopg2.connect('postgresql://leonid:babkin36@localhost:5432/page_analyzer')
SECRET_KEY = os.getenv("SECRET_KEY")
app = Flask(__name__)
app.secret_key = SECRET_KEY


# Open a cursor to perform database operations
cur = conn.cursor()
def check_uniqueness(url):
    with conn:
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as curs:
            curs.execute("SELECT * FROM urls WHERE name like %s ESCAPE ''", (url,))
            return curs.fetchone()
    conn.close()


def url_entry(datum):
    datum = request.form.to_dict()
    url = urlparse(datum['url'])
    name =  f'{url.scheme}://{url.hostname}'
    date = datetime.now().strftime("%Y-%m-%d")
    return name, date


@app.route("/")
def hello_template():
    data = {'url': ''}
    return render_template('index.html', data=data)


@app.route('/', methods=['POST'])
def hello_url():
    datum = request.form.to_dict()
    name, date = url_entry(datum)
    entry_tuple = check_uniqueness(name)
    if entry_tuple:
        pass
    else:
        with conn:
            with conn.cursor() as curs:
                cur.execute("INSERT INTO urls (name, created_at) VALUES (%s, %s)", (name, date))
        conn.close() # leaving contexts doesn't close the connection
    return render_template('page.html', url=entry_tuple[1])
