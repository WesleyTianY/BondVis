#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import argparse
from backend.app import create_app
from gevent.pywsgi import WSGIServer
# app.config['STATIC_FOLDER'] = './client/assets'

def main():
    parser = argparse.ArgumentParser(description="Run the Flask application.")
    parser.add_argument('-p', '--prod', action='store_true', help="Run in production mode")
    args = parser.parse_args()

    if args.prod:
        os.environ['FLASK_CONFIG'] = 'prod'
    else:
        os.environ['FLASK_CONFIG'] = 'local'

    app = create_app()
    http_server = WSGIServer(('', 5003), app)
    http_server.serve_forever()

if __name__ == "__main__":
    main()
