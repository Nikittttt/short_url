from flask import Flask, redirect, abort, render_template, request
import argparse
import sqlite3
import shortuuid

app = Flask(__name__)


class DB:
    def __init__(self):
        self.conn = sqlite3.connect("short_url.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS urls
                                  (id INTEGER PRIMARY KEY, 
                                  url TEXT UNIQUE, 
                                  is_short INTEGER)""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS url_url
                                  (id INTEGER PRIMARY KEY, 
                                  url_main_id INTEGER NOT NULL, 
                                  url_short_id INTEGER NOT NULL,
                                  FOREIGN KEY (url_main_id) REFERENCES urls(id), 
                                  FOREIGN KEY (url_short_id) REFERENCES urls(id))""")

    def get_or_create_id_url(self, url, is_short):
        self.cursor.execute('SELECT id FROM urls WHERE url=?', (url,))
        id_ = self.cursor.fetchone()
        is_create = 0
        if not id_:
            is_create = 1
            self.cursor.execute('INSERT INTO urls(url, is_short) VALUES (?, ?)', (url, is_short))
            self.conn.commit()
            id_ = self.cursor.lastrowid
        else:
            id_ = id_[0]
        return {'is_create': is_create, 'id': id_}

    def get_info_url(self, url):
        self.cursor.execute('SELECT id, is_short FROM urls WHERE url=?', (url,))
        return self.cursor.fetchone()

    def get_or_create_connect(self, url, is_short, id_l):
        id_ = self.get_or_create_id_url(url, is_short)
        if id_['is_create']:
            id_s = id_['id']
            self.cursor.execute('INSERT INTO url_url(url_main_id, url_short_id) VALUES (?, ?)', (id_l, id_s))
            self.conn.commit()
        return {'is_create': id_['is_create']}

    def get_url_from_connect(self, is_short, id_):
        if is_short:
            self.cursor.execute('SELECT url FROM urls INNER JOIN url_url on urls.id = url_url.url_main_id'
                                ' WHERE url_url.url_short_id=?', (id_,))
        else:
            self.cursor.execute('SELECT url FROM urls INNER JOIN url_url on urls.id = url_url.url_short_id'
                                ' WHERE url_url.url_main_id=?', (id_,))
        return self.cursor.fetchone()
        
        
@app.route('/', methods=['post', 'get'])
def index():
    db = DB()
    message = ''
    if request.method == 'POST':
        url = request.form['url']
        short_url = request.form['short_url']

        if not short_url:
            id_l = db.get_or_create_id_url(url, 0)['id']

            short = shortuuid.uuid(name=url)

            id_info = db.get_or_create_connect(short, 1, id_l)
            if not id_info['is_create']:
                return abort(404)
        elif short_url:
            id_l = db.get_or_create_id_url(url, 0)['id']

            short = short_url

            id_info = db.get_or_create_connect(short, 1, id_l)
        
        message = 'Короткая ссылка для "{}" - "{}"'.format(url, short) 

    return render_template('form.html', message=message)

@app.route('/<string:short_url>', methods=['get'])
def short_url(short_url):
    db = DB()
    info_url = db.get_info_url(short_url)
    if not info_url:
        return abort(404)
    else:
        info_url = dict(zip(['id', 'is_short'], info_url))
    url = db.get_url_from_connect(info_url['is_short'], info_url['id'])
    if not url:
        return abort(404)
    return redirect(url[0], code=301)

if __name__ == "__main__":
    app.run(debug=True)
