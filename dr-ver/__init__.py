""" A small flask Hello World """

import os
import subprocess
import random

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

@APP.route('/static/<path:path>', methods=['GET'])
def _send_static(path):
    return send_from_directory('static', path)
@APP.route('/favicon.ico')
def _send_favicon():
    return send_from_directory('static', 'favicon.ico')

@APP.route('/')
def _index():
    return render_template('index.html', commit_hash=commit_hash)

@APP.route('/api/v0/shorten', methods=['POST'])
def _post_shorten():
    data = request.get_json(force=True)
    key = generate_url()
    r.set(f'key:{key}', data['url'])
    count = r.incr('count')
    return jsonify({'key': key, 'count': count})

@APP.route('/<path:key>')
def _get_key(key):
    try:
        url = r.get(f'key:{key}').decode('UTF-8')
        r.incr(f'count:{key}')
        return redirect(url)
    except:
        abort(404)


def generate_url():
    keyspace = 'abcdefghijklmnopqrstuvwxyz'
    minlength = 4
    tryCount = 0
    key = ''
    for attempt in range(0, len(keyspace) ** minlength):
        for i in range(0, minlength):
            key += random.choice(keyspace)
        if r.get(f'key:{key}') is None:
            return key