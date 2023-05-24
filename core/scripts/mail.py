#!/usr/bin/env python
import base64
import os
import pickle

# mail
import email.utils
import mimetypes
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from google.auth.transport.requests import Request
from dotenv import load_dotenv
load_dotenv()


script_path = os.path.dirname(os.path.abspath(__file__))


def add_embedded_image_to_related(message_related):
    image_cid = email.utils.make_msgid(domain='foo.com')[1:-1]
    with open('attachments/pixabay-stock-art-free-presentation.png', 'rb') as \
            img:
        maintype, subtype = mimetypes.guess_type(img.name)
        message_related.attach(MIMEImage(img.read(), subtype, cid=image_cid))
    return image_cid


def create_message_with_attachment(sender, to, subject, msg_html, msg_plain):
    message = MIMEMultipart('mixed')
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    message_alt = MIMEMultipart('alternative')
    message_alt.attach(MIMEText(msg_plain, 'plain'))
    message_rel = MIMEMultipart('related')
    message_rel.attach(MIMEText(msg_html, 'html'))
    message_alt.attach(message_rel)
    message.attach(message_alt)
    return message


def gmail_authenticate():
    SCOPES = ['https://mail.google.com/']
    creds = None
    if os.path.exists("core/tokens/token.pickle"):
        with open("core/tokens/token.pickle", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'core/tokens/credentials.json',
                SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("core/tokens/token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)


def send_message_to_google(message, sender):
    creds = None
    service = gmail_authenticate()
    msg_raw = {'raw': base64.urlsafe_b64encode(
        message.as_string().encode()).decode()
    }
    try:
        message = (service.users().messages().send(userId=sender, body=msg_raw).execute())
        return message
    except Exception as e:
        raise e


def send_message(to_csv, hash, name='user'):
    sender = os.getenv('SENDER')
    subject = 'подтверждение почты'
    name = 'user'
    msg_html = f"""
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
    </head>
    <body style="width: 100%;">
        <table border="0" cellpadding="0" cellspacing="0" style="width: 100%; margin:0; padding:0; background: rgb(219, 153, 122);">
            <td style="min-width: 60%;">
                <p style="font-size: 30px; text-align: center;">Добро пожаловать в систему!</p>
                <p style="font-size: 20px; margin-left: 20px; text-align: center;">Вы получили данное письмо, так зарегестрировались в системе TelegramStorage</p>
                <p style="font-size: 20px; margin-left: 20px; text-align: center;">Чтобы подтвердить регистрацию нажмите на кнопку ниже.</p>
                <p style="font-size: 20px; margin-left: 20px; text-align: center;">(Если это были не Вы - проигнорируйте данное письмо)</p>
                <a href="http://127.0.0.1:8080/confirmation/{hash}"><button style="margin: 0 auto; background-color: rgb(237,221,178);
                    display: block; font-size: 20px;  min-width: 250px; min-height: 40px; margin-bottom: 100px;">Подтвердить почту</button></a>
            </td>
            <td><a><img src="https://ie.wampi.ru/2023/04/13/imgonline-com-ua-Resize-zJOMtFUafUhFLZ.png" alt=""></a></td>
        </table>
    </body>
    </html>
    """

    # text message, would use mako templating in real scenario
    msg_plain = ("Hello {}:\n\n" +
                 " As our valued customer, we would like to invite you to our annual sale!").format(name)

    # create message object
    message = create_message_with_attachment(sender, to_csv, subject, msg_html, msg_plain)
    send_message_to_google(message, sender)