from pyrogram import Client
from core.sql.sql_api import add_new_file, get_id_by_email
from os import getenv
from dotenv import load_dotenv
load_dotenv()

api_id = getenv('API_ID')
api_hash = getenv('API_HASH')
send_to = getenv('SEND_TO')


async def upload_file(session, name, email, holder, session_str):
    async with Client("my_account", api_id, api_hash, in_memory=True, session_string=session_str) as app:
        x = await app.send_document(send_to, name)
        try:
            add_new_file(
                session,
                x.id,
                get_id_by_email(session, email),
                x.document.file_name,
                int(x.document.file_size),
                holder
            )
        except AttributeError:
            add_new_file(
                session,
                x.id,
                get_id_by_email(session, email),
                x.audio.file_name,
                int(x.audio.file_size),
                holder
            )
        return x


async def download_file(id, session_str):
    async with Client("my_account", api_id, api_hash, in_memory=True, session_string=session_str) as app:
        message = await app.get_messages(send_to, int(id))
        await app.download_media(message)
        return message.document.file_name

async def check(session_str):
    try:
        async with Client("my_account", api_id, api_hash, in_memory=True, session_string=session_str) as app:
            await app.send_message(send_to, "Test")
            return True
    except BaseException:
        return False
