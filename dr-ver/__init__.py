""" A small flask Hello World """

import os
import subprocess

from flask import Flask, jsonify, render_template
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