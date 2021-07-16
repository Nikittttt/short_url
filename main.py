import argparse
import sqlite3
import shortuuid


class DB:
    def __init__(self, name_db):
        self.conn = sqlite3.connect(name_db)
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
        return dict(zip(['id', 'is_short'], self.cursor.fetchone()))

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


if __name__ == "__main__":
    db = DB("short_url.db")

    parser = argparse.ArgumentParser()
    parser.add_argument('url')
    parser.add_argument('--generate', action='store_true')
    parser.add_argument('--short_url')
    args = parser.parse_args()
    if not (args.short_url or args.generate):
        info_url = db.get_info_url(args.url)
        if not info_url:
            raise Warning('No such url')
        url = db.get_url_from_connect(info_url['is_short'], info_url['id'])
        if not url:
            raise Warning('No such url')
        print('\n'.join(url))
    elif args.generate and not args.short_url:
        id_l = db.get_or_create_id_url(args.url, 0)['id']

        short = shortuuid.uuid(name=args.url)

        id_info = db.get_or_create_connect(short, 1, id_l)
        if id_info['is_create']:
            print(short)
        else:
            raise Warning('This url already exists')
    elif args.short_url and args.generate:
        id_l = db.get_or_create_id_url(args.url, 0)['id']

        short = args.short_url

        id_info = db.get_or_create_connect(short, 1, id_l)
        print(short)

