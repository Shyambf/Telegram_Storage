import os
import asyncio
import logging
import datetime

from flask import Flask, render_template, request, redirect, session, send_from_directory
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from werkzeug.routing import BaseConverter
from core.sql.crate_table import create_bd
from core.sql.sql_api import *
from core.scripts.mail import send_message
from core.scripts.telegram_api import upload_file, download_file, check
from core.scripts.utils import get_hash, read_hash, human_read_format, secure_filename

logging.basicConfig()
logging.getLogger('sqlalchemy').setLevel(logging.ERROR)

if not os.path.isfile('core/sql/db/data.db'):
    create_bd()
if not os.path.isdir('downloads'):
    os.mkdir('downloads')
if not os.path.isdir('core/tokens'):
    os.mkdir('core/tokens')
if not os.path.isfile('core/tokens/token.pickle'):
    send_message(os.environ['sender'], 'test')
engine = create_engine("sqlite:///core/sql/db/data.db",
                           connect_args={"check_same_thread": False}, echo=False, future=True)

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
session_sql = Session()

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = 'downloads'
app.url_map.converters['regex'] = RegexConverter
app.permanent_session_lifetime = datetime.timedelta(days=7)

@app.route('/confirmation/<regex("([a-z]|[0-9]){0,80}"):hash>/')
def confirmation(hash: str):
    for i in get_all_User(session_sql):
        if read_hash(get_hash(i.email)) == read_hash(hash):
            confirm_user(session_sql, i.id)
            return redirect('/main')
    else:
        return 0


@app.route('/download/<regex("([a-z]|[A-z]|[0-9]|-|_)*"):discharge>/')
def download_file_flask(discharge):
    filename = asyncio.run(download_file(discharge, get_session(session_sql, session['email'])))
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename, as_attachment=True)


@app.route('/delete/<regex("([a-z]|[A-z]|[0-9]|-|_)*"):discharge>/')
def delete_file_flask(discharge):
    delete_file(session_sql, discharge)
    return redirect('/main')


@app.route('/delete_folder/<num>')
def deletes_folder(num):
    delete_folder(session_sql, num)
    return redirect('/main')


@app.route('/redir/<num>')
def open_folder(num):
    if session['query'] != '':
        session['query'] = ''
        return redirect('/main')
    else:
        session['folder'] = num
        return redirect('/main')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        select = {}
        # если происходит вход
        if request.form.get('email-login'):
            select['email'] = request.form.get('email-login')
            select['password'] = request.form.get('password-login')
            if check_user(session_sql, select['email'], select['password']) == 'successfully':
                session['email'] = select['email']
                session['password'] = get_hash(select['password'])
                session['folder'] = 0
                session['query'] = ''
                return redirect('/main')
            else:
                return render_template('register.html', wrong_password='Неверные данные для входа')

            # если происходит регистрация
        else:
            if request.form.get('password-input') != request.form.get('password-input1') and request.form.get('password-input') and request.form.get('password-input1'):
                return render_template('register.html', wrong_password="Пароли не совпадают!")
            else:
                select['email-input'] = request.form.get('email-input')
                select['password-input'] = request.form.get('password-input')
                select['password-input1'] = request.form.get('password-input1')
                select['session_str'] = request.form.get('code-input')
                if not check(select['session_str']):
                    return render_template('register.html', wrong_password="Ошибка строчки")
                add_new_user(session_sql, select['email-input'], select['password-input'], select['session_str'])
                select['session_str'] = ''
                send_message(select['email-input'], get_hash(select['email-input']))
                return render_template('success.html')


@app.route('/query', methods=['POST', 'GET'])
def query():

    if request.method == 'GET':
        session['query'] = ''
        return redirect('/main')
    elif request.method == 'POST':
        # если происходит вход
       session['query'] = request.form.get('query')
       return redirect('/main')


@app.route('/main', methods=['POST', 'GET'])
def main():
    global register, email, files
    if request.method == 'GET':
        # словарь для переработки типа файла в подходящую иконку
        TYPE_TO_ICON = {
            'docx': 'word_icon.svg',
            'txt': 'text-icon.svg',
            'zip': 'archive_icon.svg',
            'rar': 'archive_icon.svg',
            'pptx': 'presentation_icon.svg',
            'xlsx': 'table_icon.svg',
            'png': 'picture_icon.svg',
            'jpg': 'picture_icon.svg',
            'svg': 'picture_icon.svg',
            'py': 'code-icon.svg',
            'cpp': 'code-icon.svg',
            'java': 'code-icon.svg',
            'go': 'code-icon.svg',
            'js': 'code-icon.svg',
            'php': 'code-icon.svg'
        }
        register = False
        # email None если пользователь не авторизован
        try:
            if session['email']:
                email = session['email'] 
                # вошел ли пользователь в свой акк или нет
                register = True
        except KeyError:
            return redirect('/register')
        if not register:
            return redirect('/register')
        
        folder = list()
        if session['query'] == '':

            for i in get_folder(session_sql, session['email'], session['folder']):
                folder.append([i.name, i.id, i.holder])
            
            files = [
                [TYPE_TO_ICON.get(i.name.split('.')[-1], 'unknown_file_icon.svg'),
                i.name, human_read_format(i.size), i.id] for i in get_all_files_by_user_in_path(session_sql,
                get_id_by_email(session_sql, session['email']), session['folder'])]
            search = False
        else: 
            files = [
                [TYPE_TO_ICON.get(i.name.split('.')[-1], 'unknown_file_icon.svg'),
                i.name.replace(session['query'], "<mark>" + session['query'] + "</mark>"), human_read_format(i.size), i.id] for i in get_all_files_by_user_in_path_and_query(session_sql,
                get_id_by_email(session_sql, session['email'])) if session['query'] in i.name]
            search = True
        try:
            holder = get_holder_by_id(session_sql, session['folder']).holder
        except BaseException:
            holder = 0

        return render_template('main.html', register=register, email=email, files=files,
                            folder=folder, adress=rek(session_sql, session['folder']), holder=holder, search=search)
    
    elif request.method == 'POST':
        try:
            file = request.files['file']
            # Если файл не выбран, то браузер может отправить пустой файл без имени.
            if file.filename == '':
                return render_template('main.html', register=register, email=email, files=files, wrong_password="Отсутствует выбранный файл!", adress=rek(session_sql, session['folder'])) 
            if file:
                # безопасно извлекаем оригинальное имя файла
                files = request.files.getlist("file")
  
        # Iterate for each file in the files List, and Save them
                for file in files:
                    # сохраняем файл
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    asyncio.run(upload_file(session_sql, os.path.join(app.config['UPLOAD_FOLDER'], filename), session['email'], session['folder'], get_session(session_sql, session['email'])))
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect('/main')
        except ValueError:
            return render_template('main.html', register=register, email=email, files=files, wrong_password="Размер Фаила = 0. Так нельзя", adress=rek(session_sql, session['folder']))
        except (NameError, KeyError):
            try:
                folder_name = request.form.get('email-login')
                add_folder(session_sql, folder_name, session['email'], session['folder'])
                return redirect('/main')
            except Exception:
                return redirect('/main')


@app.route('/')
def welcome():
    return render_template('welcome.html')

if __name__ == '__main__':
    from waitress import serve
    #serve(app, host="127.0.0.1", port=8080)
    app.run(port=8080, host='127.0.0.1', debug=True)
