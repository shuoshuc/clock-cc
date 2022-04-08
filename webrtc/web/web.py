#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    template = 'server.html' if is_server else 'client.html'
    return render_template(template)

if __name__ == '__main__':
    global is_server
    is_server = ('server' == sys.argv[1])
    if is_server:
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        app.run(debug=True, host='0.0.0.0', port=5001)
