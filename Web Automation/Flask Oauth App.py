import os
import sqlite3
import requests
import urllib.parse

from flask import Flask
from flask import url_for
from flask import request
from flask import redirect
from flask import render_template
from werkzeug.utils import secure_filename

'''
Hosting on Pythonanywhere.com:
    1.  Create an account on `pythonanywhere.com` which should bring up the dashboard.
    2.  Click `Web` then `Add a new web app` then `Flask` and then `Python 3.7`.
    3.  Make sure `Force HTTPS` and `Passwor protection` are enabled.
    4.  Setup a `Username` and `Password` making sure to click the `check` icon to save the field.
    5.  Click `Files` enter file name `auth.txt` and click `New file` which should bring up the editor.
    6.  Type in `app_id app_key` (space in between) and click `Save`.
    7.  Navigate back to the dashboard and click `Files` then `mysite/`.
    8.  In the `Directories` text box enter `templates` and click `New directory`.
    9.  Click `Upload a file` and upload the `index.html` file.
    10. Navigate back to the dashboard and click `Files` then `mysite/`.
    11. Click `flask_app.py` which should bring up the editor, copy code and click `Save`.
    12. Navigate back to the dashboard and click 'Web' then click the green `Reload` button.
'''

html   = ''
server = urllib.parse.quote_plus(f'http://localhost:8080')

def init_database():
    with sqlite3.connect('data.db') as db:
        db.execute('CREATE TABLE IF NOT EXISTS pages ( \
            page_id INTEGER PRIMARY KEY,               \
            user_id INTEGER NOT NULL,                  \
            page_token TEXT NOT NULL,                  \
            name TEXT NOT NULL)')
        db.commit()

def get_pages():
    with sqlite3.connect('data.db') as db:
        query = 'SELECT page_id, page_token, name FROM pages'
        return {row[0]:{
            'page_id':    row[0],
            'page_token': row[1],
            'name':       row[2]} for row in db.execute(query)}

def add_page(page, user_id):
    with sqlite3.connect('data.db') as db:
        db.execute('INSERT OR REPLACE INTO pages (page_id, user_id, page_token, name) VALUES (?,?,?,?)', (
            page['id'],
            user_id,
            page['access_token'],
            page['name']))
        db.commit()

def call_api(verb, method, token, params, files={}):
    params.update({'access_token': token, 'format': 'json'})
    url = f'https://graph.facebook.com/{method}'
    req = requests.request(verb, url, params=params, files=files)
    return req.json() if req.json() else []

class WebApp:
    def __init__(self):
        self.redirect = f'{server}/callback'
        self.app_id, self.app_secret = open('auth.txt').read().split()
        self.create_webview()
    
    def create_webview(self):
        init_database()
        app = Flask(__name__)
        app.config['UPLOAD_FOLDER'] = 'uploads'
        os.makedirs('uploads', exist_ok=True)
        
        def upload_file(request):
            path = None
            file = request.files.get('file')
            if file:
                path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
                file.save(path)
            return path
        
        def build_page_html(page, state):
            icon = 'fa-check' if state == 'success' else 'fa-times-circle' if state == 'error' else ''
            return (
                f'\n<div class="page {state}">'
                f'\n\t<label><input type="checkbox" name="page.{page["page_id"]}"/>'
                f'<b>{page["name"]}</b>'
                f'<i class="fa {icon}"></i></label>'
                f'\n</div>')
        
        def post_message(page, message, path):
            target  = 'photos'                    if path else 'feed'
            files   = {'source': open(path,'rb')} if path else {}
            success = 'id' in call_api(
                verb   = 'POST',
                method = f'{page["page_id"]}/{target}',
                token  = page['page_token'],
                params = {'message': message},
                files  = files)
            return 'success' if success else 'error'
        
        @app.route('/', methods=['GET', 'POST'])
        def index():
            global html
            pages = get_pages()
            if request.method == 'POST':
                html = ''
                path = upload_file(request)
                text = request.form.get('message')
                pids = [int(key.split('.')[-1]) for key in request.form if key.startswith('page')]
                for page in pages.values():
                    state = post_message(page, text, path) if page['page_id'] in pids else 'default'
                    html += build_page_html(page, state)
                return redirect(url_for('index', refresh=False))
            if request.args.get('refresh') != 'False':
                html = ''
                for page in pages.values():
                    html += build_page_html(page, 'default')
            return render_template('index.html', pages=html)
        
        @app.route('/authorize')
        def authorize():
            return redirect(
                f'https://www.facebook.com/v3.3/dialog/oauth'
                f'?client_id={self.app_id}'
                f'&scope=manage_pages,publish_pages,pages_show_list'
                f'&redirect_uri={self.redirect}'
                f'&response_type=code')
        
        @app.route('/callback')
        def callback():
            short_token = requests.get((
                f'https://graph.facebook.com/v3.3/oauth/access_token'
                f'?client_id={self.app_id}'
                f'&redirect_uri={self.redirect}'
                f'&client_secret={self.app_secret}'
                f'&code={request.args.get("code")}')).json()['access_token']
            long_token = requests.get((
                'https://graph.facebook.com/oauth/access_token'
                f'?grant_type=fb_exchange_token'
                f'&client_id={self.app_id}'
                f'&client_secret={self.app_secret}'
                f'&fb_exchange_token={short_token}'
                f'&access_token={short_token}')).json()['access_token']
            uid   = call_api('GET', 'debug_token',      long_token, {'input_token': long_token})['data']['user_id']
            pages = call_api('GET', 'v3.3/me/accounts', long_token, {})['data']
            for page in pages:
                add_page(page, uid)
            return redirect(url_for('index'))
        
        app.run(host='0.0.0.0', port='8080')

if __name__ == '__main__':
    WebApp()

# index.html
'''
<!doctype html>
<style>
    @import url('//maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css');
    body {
        background: black;
        color: white;
        font: 12px Monospace;
    } 
    .app, .page, .tray, .textbox {
        display: block;
        overflow: hidden;
        padding: 3px;
        border: 1px solid #555;
    }
    .app {
        position: absolute;
        top: 100px;
        left: 0;
        right: 0;
        margin: auto;
        width: 500px;
        overflow: visible;
    }
    .page label {
        white-space: nowrap;
        text-align: left;
    }
    .page input {
        vertical-align: middle;
    }
    .message {
        background: inherit;
        color: inherit;
        height: 400px;
        width: 100%;
        resize: none;
        border-style: groove;
        border-width: 1px;
    }
    .tray file {
        float: left;
    }
    .tray button {
        float: right;
    }
    .tray button + button {
        margin-right: 2px;
    }
    .textbox {
        padding-right: 9px;
    }
    h1, h4 {
        text-align: center;
    }
    h1 {
        font-family: sans-serif;
    }
    .fa {
        float: right;
        margin-top: 4px;
        margin-right: 2px;
    }
    .default {
        color: white;
        background: #000;
    }
    .success {
        color: #4F8A10;
        background-color: #DFF2BF;
    }
    .error {
        color: #D8000C;
        background-color: #FFD2D2;
    }
</style>
<div class="app">
    <h1>Page Post</h1>
    <h4>Note - An Error Indicates 'Token Expired' or 'Platform Rejected Message'.</h4>
    <form method="POST" enctype="multipart/form-data" onsubmit="return confirm('Submit Post?');">
        {{ pages|safe }}
        <div class="textbox">
            <textarea class="message" name="message"></textarea>
        </div>
        <div class="tray">
            <input type="file" name="file" accept=".jpg,.jpeg,.gif,.png"></input>
            <button type="submit" value="Post">Post</button>
        </div>
    </form>
</div>
'''
