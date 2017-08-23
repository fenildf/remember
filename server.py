#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# all the imports

from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash
from flask_sqlalchemy import SQLAlchemy
import random
from sqlalchemy import and_
from my_tools import translate_english, bing_image_search_by_requests

# configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:///./databases.db'
DEBUG = True
SECRET_KEY = 'remember'
SQLALCHEMY_TRACK_MODIFICATIONS = True

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

db = SQLAlchemy(app)


class Words(db.Model):
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    word = db.Column('word', db.String(50))
    term_frequency = db.Column('term_frequency', db.Integer)

    def __init__(self, word, term_frequency):
        self.word = word
        self.term_frequency = term_frequency

    def __repr__(self):
        return '<EnglishWords %r>' % self.word


@app.route('/')
def home_page():
    return redirect(url_for('show_index'))


@app.route('/index', methods=['GET'])
def show_index():
    from_num = request.args.get('from_num', 50)
    to_num = request.args.get('to_num', 100)

    min_word = Words.query.filter(
        and_(Words.term_frequency >= from_num, Words.term_frequency <= to_num)).order_by(
        Words.id).first()
    max_word = Words.query.filter(
        and_(Words.term_frequency >= from_num, Words.term_frequency <= to_num)).order_by(
        Words.id.desc()).first()

    random_id = random.randint(min_word.id, max_word.id)

    word = Words.query.filter(Words.id >= random_id).first()

    word.images = bing_image_search_by_requests(word.word)
    word.ext = translate_english(word.word)

    data = {}
    data['word'] = word
    data['from_num'] = from_num
    data['to_num'] = to_num

    return render_template('show_index.html', data=data)


@app.route('/tongji')
def show_tontji():
    count = []
    categories = []

    for i in range(1, 10):
        s = i * 10 - 9
        e = i * 10

        categories.append('/'.join([str(s), str(e)]))

        item_count = Words.query.filter(
            and_(Words.term_frequency >= s, Words.term_frequency < e)).count()
        count.append(item_count)

    item_count = Words.query.filter(Words.term_frequency >= 100).count()
    count.append(item_count)
    categories.append('100/~')

    return render_template('tongji.html', count=count, categories=categories)


if __name__ == '__main__':
    # show_index()
    app.run(host='0.0.0.0', port=8080)
