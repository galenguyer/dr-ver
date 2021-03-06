import secrets
import os

# Values in this file are loaded into the flask app instance, `demo.APP` in this
# demo. This file sources values from the environment if they exist, otherwise a
# set of defaults are used. This is useful for keeping secrets secret, as well
# as facilitating configuration in a container. Defaults may be overriden either
# by defining the environment variables, or by creating a `config.py` file that
# contains locally set secrets or config values.


# Defaults for flask configuration
IP = os.environ.get('IP', '127.0.0.1')
PORT = os.environ.get('PORT', 5000)
SECRET_KEY = os.environ.get('SESSION_KEY', default=''.join(secrets.token_hex(16)))

REDIS_HOST = os.environ.get('REDIS_HOST', default='localhost')
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)