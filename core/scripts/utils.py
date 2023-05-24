import re
from hashlib import sha256
from random import choice
import sys
import os

OTHER_STRINGS = '0123456789abcdefghijklmnopqrstuvwxyz0123456789'
SPECIAL_SIMBOLS = '@#№;"?/<>|\\/~`%!.,+=-_()'

def get_hash(text:str) -> str:
    # gets the hash of the transmitted element with the addition of random characters
    pas = ''.join([choice(OTHER_STRINGS) for _ in range(16)])
    return pas[:8] + \
        sha256(str(text).encode('utf-8')).hexdigest() +  \
            pas[8:]

def read_hash(hash:str) -> str:
    return hash[8:-8]

def mail_validator(email:str) -> bool:
    pattern = re.compile("^[^@]+@[^@]+\.[^@]+$")
    return bool(pattern.match(email))

def password_validator(password:str) -> bool:
    return bool([i for i in password if i in SPECIAL_SIMBOLS] and len(password) >= 8)

def get_size(file=None, filepath:str=None) -> int:
    if file:
        file.seek(0, os.SEEK_END)
        return file.tell()
    if filepath:
        return os.path.getsize(filepath)

def int_r(num):
    num = int(num + (0.5 if num > 0 else -0.5))
    return num
 
 
def human_read_format(number):
    if number >= 1024 * 1024 * 1024:
        return str(int_r(number / (1024 * 1024 * 1024))) + 'ГБ'
    elif number >= 1024 * 1024:
        return str(int_r(number / (1024 * 1024))) + 'МБ'
    elif number >= 1024:
        return str(int_r(number / 1024)) + 'КБ'
    else:
        return str(number) + 'Б'



PY2 = sys.version_info[0] == 2
if PY2:
    text_type = unicode
else:
    text_type = str

_windows_device_files = (
    "CON",
    "AUX",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "LPT1",
    "LPT2",
    "LPT3",
    "PRN",
    "NUL",
)

_filename_strip_re = re.compile(r"[^A-Za-zа-яА-ЯёЁ0-9_.-]")


def secure_filename(filename: str) -> str:
    if isinstance(filename, text_type):
        from unicodedata import normalize
        filename = normalize("NFKD", filename)

    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, " ")

    filename = str(_filename_strip_re.sub("", "_".join(filename.split()))).strip(
        "._"
    )
    
    if (
        os.name == "nt"
        and filename
        and filename.split(".")[0].upper() in _windows_device_files
    ):
        filename = f"_{filename}"

    return filename