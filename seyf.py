#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: Python -*-

"""
  ===========================================================================

  Copyright (C) 2020 Emvivre

  This file is part of SEYF.

  SEYF is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  SEYF is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with SEYF.  If not, see <http://www.gnu.org/licenses/>.

  ===========================================================================
*/
"""

############################# PARAMETERS #############################
MAX_CONTENT_LENGTH = 20 * 1024 * 1024    # maximal bytes per file
MAX_TOTAL_SIZE = 100 * 1024 * 1024       # total maximal hosted bytes
USERNAME = 'user'                        # login for the authentication
PASSWORD = 'password'                    # password for the authentication

############################### SOURCE ###############################
from flask import Flask, make_response, redirect, url_for, request
from flask_httpauth import HTTPDigestAuth
import datetime
import random

with open(__file__) as fd:
    source_file = fd.read()

last_id = 0
files_shared = {}

app = Flask(__name__)
app.config['SECRET_KEY'] = ''.join([ chr(int(254*random.random())) for i in range(32) ])
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
application = app

users = { USERNAME: PASSWORD }
auth = HTTPDigestAuth()
@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None

@app.route('/source', methods=['GET'])
@auth.login_required
def source():
    r = make_response(source_file)
    r.mimetype = 'text/plain'
    r.headers['Content-Disposition'] = 'attachment; filename="src.py"'
    return r

@app.route('/get/<int:key>', methods=['GET'])
@auth.login_required
def get(key):
    if key not in files_shared:
        return 'ERROR: File not found !'
    f = files_shared[key]
    r = make_response(f['content'])
    r.mimetype = f['mimetype']
    r.headers['Content-Disposition'] = 'attachment; filename="%s"' % f['filename']
    return r

@app.route('/delete/<int:key>', methods=['GET'])
@auth.login_required
def delete(key):
    print('---', key)
    if key not in files_shared:
        return 'ERROR: File not found !'
    del files_shared[key]
    return redirect(url_for('index'))

def timestamp2str(t):
    d = datetime.datetime.fromtimestamp(t)
    return '%4d/%02d/%02d %02d:%02d:%02d' % (d.year, d.month, d.day, d.hour, d.minute, d.second)

@app.route('/upload', methods=['POST'])
@auth.login_required
def upload():
    global last_id
    if 'input_file' not in request.files:
        return 'ERROR: no upload file found !'
    fd = request.files['input_file']
    content = fd.read()
    filesize = len(content)
    sz  = sum([ f['size'] for f in files_shared.values() ])
    sz += filesize
    if sz > MAX_TOTAL_SIZE:
        return ('ERROR: maximal server size reached !', 413)
    last_id += 1
    d = datetime.datetime.now()
    timestamp = int(d.timestamp())
    files_shared[ last_id ] = { 'filename': fd.filename,
                                'size': filesize,
                                'content': content,
                                'timestamp': timestamp,
                                'mimetype': fd.content_type }
    return redirect(url_for('index'))

@app.route('/', methods=['GET'])
@auth.login_required
def index():
    files_shared_str = ''
    nb_files = len(files_shared)
    if nb_files > 0:
        files_shared_str = '''
        Files Available: <br />
<table border='1'>
<th><td>Delete</td><td>Timestamp</td><td>Filename </td><td>Size</td><td>Download</td></th>
%s
</table>
        ''' % '\n'.join([ '<tr><td><td><a href="%(url_delete)s" style="font-size:300%%">&#128465;</a></td><td>%(timestamp)s</td><td>%(filename)s</td><td>%(size)d</td><td><form action="%(url_get)s" method="get"><button style="font-size:150%%">DOWNLOAD</button></form></td></th></tr>' % {
            'url_delete':url_for('delete', key=i),
            'url_get':url_for('get', key=i),
            'timestamp':timestamp2str(f['timestamp']),
            'filename':f['filename'],
            'size':f['size']} for (i,f) in files_shared.items()
        ])

    return '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0, user-scalable=yes">
  <title>SEYF</title>
</head>
<body>
  <h1>SEYF : Share Easily Your Files</h1>
SEYF project aims to share easily your files. Uploaded files stay in RAM, there are not saved in any file system.<br />
<br />
  Upload your file :<br />
  <form action="%(url_upload)s" method="post" enctype="multipart/form-data">
    <input name="input_file" type="file"/><br />
    <input type="submit" />
  </form>
  <br />
%(files_shared_str)s
  <hr>
Current parameters:<br />
 - MAX_FILE_SIZE: %(MAX_CONTENT_LENGTH)s<br/>
 - MAX_TOTAL_SIZE: %(MAX_TOTAL_SIZE)s<br />
<br />
  <form action="%(url_source)s" method="get">
     <button>Get Source Code</button>
  </form>
</body>
</html>''' % {
    'MAX_CONTENT_LENGTH':MAX_CONTENT_LENGTH,
    'MAX_TOTAL_SIZE':MAX_TOTAL_SIZE,
    'files_shared_str':files_shared_str,
    'url_upload':url_for('upload'),
    'url_source':url_for('source')
}


if __name__ == '__main__':
    from gevent.pywsgi import WSGIServer
    SERVER_HOST = 'localhost'
    SERVER_PORT = 8888
    http_server = WSGIServer((SERVER_HOST, SERVER_PORT), app)
    http_server.serve_forever()
