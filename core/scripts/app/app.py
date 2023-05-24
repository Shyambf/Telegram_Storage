from pyrogram import Client
from os import remove, getenv
from dotenv import load_dotenv
load_dotenv()

api_id = getenv('API_ID')
api_hash = getenv('API_HASH')
print('app.exe v0.1b')

with Client('s', api_id, api_hash) as client:
    print(f'the code to enter on the website:\n\n\n{client.export_session_string()}\n\n\n\n')

remove('s.session')
input('press any key to close the application...')