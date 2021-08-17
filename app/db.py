from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from main import app

db = SQLAlchemy(app)
migrate = Migrate(app, db)

urls = db.Table('urls', db.Model.metadata,
                db.Column('url1_id', db.Integer, db.ForeignKey('Url.id')),
                db.Column('url2_id', db.Integer, db.ForeignKey('Url.id'))
                )


class Url(db.Model):
    __tablename__ = 'Url'
    id = db.Column(db.Integer, primary_key=True)
    is_short = db.Column(db.Boolean(), nullable=False)
    url = db.Column(db.String(255), nullable=False, unique=True)
    url_relationship = db.relationship('Url', secondary=urls,
                           primaryjoin="Url.id == urls.c.url1_id",
                           secondaryjoin="Url.id == urls.c.url2_id",
                           backref=db.backref('urls', lazy='dynamic'),
                           lazy='dynamic')

    def __init__(self, is_short, url):
        self.is_short = is_short
        self.url = url


class DB:

    def get_url_by_id(self, id_):
        url = Url.query.get(id_)
        return url

    def get_info_url(self, url):
        url = Url.query.filter_by(url=url).first()
        if url:
            url = [url.id, url.is_short]
        else:
            url = []
        return url

    def get_or_create_id_url(self, url, is_short):
        id_ = self.get_info_url(url)
        is_create = 0
        if not id_:
            is_create = 1
            url = Url(url=url, is_short=is_short)
            db.session.add(url)
            db.session.commit()
            id_ = url.id
        else:
            id_ = id_[0]
        return {'is_create': is_create, 'id': id_}

    def get_or_create_connect(self, url, is_short, id_l):
        id_ = self.get_or_create_id_url(url, is_short)
        if id_['is_create']:
            id_s = id_['id']
            url_main = self.get_url_by_id(id_l)
            url_short = self.get_url_by_id(id_s)
            url_main.urls.append(url_short)
            db.session.add(url_main)
            db.session.commit()
        return {'is_create': id_['is_create']}

    def get_url_from_connect(self, is_short, id_):
        if is_short:
            url_short = Url.query.get(id_)
            url_main = Url.query.with_parent(url_short).first()
            url = url_main.url
        else:
            url_main = Url.query.get(id_)
            url = url_main.urls.url
        return url
