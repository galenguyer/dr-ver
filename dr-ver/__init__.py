""" A small flask Hello World """

import os
import subprocess
import random
import string
import itertools

from flask import Flask, jsonify, request, render_template, redirect, abort
import redis

APP = Flask(__name__)

# Load file based configuration overrides if present
if os.path.exists(os.path.join(os.getcwd(), 'config.py')):
    APP.config.from_pyfile(os.path.join(os.getcwd(), 'config.py'))
else:
    APP.config.from_pyfile(os.path.join(os.getcwd(), 'config.env.py'))

APP.secret_key = APP.config['SECRET_KEY']

r = redis.Redis(host=APP.config['REDIS_HOST'], port=int(APP.config['REDIS_PORT']))

commit_hash = None
try:
    commit_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']) \
        .strip() \
        .decode('utf-8')
# pylint: disable=bare-except
except:
    pass


initial_consonants = (set(string.ascii_lowercase) - set('aeiou')
                      # remove those easily confused with others
                      - set('qxc')
                      # add some crunchy clusters
                      | set(['bl', 'br', 'cl', 'cr', 'dr', 'fl',
                             'fr', 'gl', 'gr', 'pl', 'pr', 'sk',
                             'sl', 'sm', 'sn', 'sp', 'st', 'str',
                             'sw', 'tr'])
                      )
final_consonants = (set(string.ascii_lowercase) - set('aeiou')
                    # confusable
                    - set('qxcsj')
                    # crunchy clusters
                    | set(['ct', 'ft', 'mp', 'nd', 'ng', 'nk', 'nt',
                           'pt', 'sk', 'sp', 'ss', 'st'])
                    )
vowels = 'aeiou' # we'll keep this simple
# each syllable is consonant-vowel-consonant "pronounceable"
syllables = list(map(''.join, itertools.product(initial_consonants, 
                                           vowels, 
                                           final_consonants)))
def gibberish(wordcount, wordlist=syllables):
    return '-'.join(random.sample(wordlist, wordcount))

@APP.route('/static/<path:path>', methods=['GET'])
def _send_static(path):
    return send_from_directory('static', path)
@APP.route('/favicon.ico')
def _send_favicon():
    return send_from_directory('static', 'favicon.ico')

@APP.route('/')
def _index():
    count = int(r.get('count').decode('UTF-8'))
    clicks = 0
    for key in r.scan_iter("clicks:*"):
        clicks += int(r.get(key).decode('UTF-8'))
    return render_template('index.html', commit_hash=commit_hash, count=count, clicks=clicks)

@APP.route('/api/v0/shorten', methods=['POST'])
def _post_api_v0_shorten():
    data = request.get_json(force=True)
    key = generate_url()
    r.set(f'key:{key}', data['url'])
    count = r.incr('count')
    return jsonify({'key': key, 'count': int(count)})

@APP.route('/api/v0/stats/<path:key>')
def _get_api_v0_stats_key(key):
    try:
        url = r.get(f'key:{key}').decode('UTF-8')
        clicks = int(r.get(f'clicks:{key}').decode('UTF-8'))
        return jsonify({'url': url, 'clicks': clicks})
    except:
        abort(404)

@APP.route('/api/v0/stats')
def _get_api_v0_stats():
    count = int(r.get('count').decode('UTF-8'))
    clicks = 0
    for key in r.scan_iter("clicks:*"):
        clicks += int(r.get(key).decode('UTF-8'))
    return jsonify({'count': count, 'clicks': clicks})

@APP.route('/<path:key>')
def _get_key(key):
    try:
        url = r.get(f'key:{key}').decode('UTF-8')
        r.incr(f'clicks:{key}')
        return redirect(url)
    except:
        abort(404)


def generate_url():
    minlength = 1
    key = ''
    while True:
        tryCount = len(syllables) ** minlength
        for attempt in range(0, tryCount):
            key = gibberish(minlength)
            if r.get(f'key:{key}') is None:
                return key
        minlength += 1
    return None