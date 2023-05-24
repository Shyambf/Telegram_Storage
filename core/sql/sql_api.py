"""
This program gathers information from the author_book_publisher.db
SQLite database file
"""

from sqlalchemy.exc import NoResultFound, PendingRollbackError

from core.sql.models import User, Files, Deletes, Folders
from core.scripts.utils import get_hash, get_size, read_hash


def get_all_files_by_user_in_path(session, user_id, path):
    return (
        session.query(
            Files
        )
        .filter(Files.owner == user_id)
        .filter(Files.holder == path)
        .all()
    )


def get_all_files_by_user_in_path_and_query(session, user_id):
    return (
        session.query(
            Files
        )
        .filter(Files.owner == user_id)
        .all()
    )


def get_all_User(session):
    return session.query(User).order_by(User.id).all()


def add_new_user(session, email, pas:str, sessionstr, confirmed=False):
    user = User()
    user.email = email
    user.hashed_password = get_hash(str(pas))
    user.confirmed = confirmed
    user.session_str = sessionstr
    session.add(user)
    session.commit()

def get_id_by_email(session, email:str):
    return session.query(User.id).filter(User.email == email).one()[0]
  
def add_new_file(session, id:str, owner:int, name:str, size:int, holder:int):
    files = Files()
    files.id = id
    files.name = name
    files.owner = owner
    files.size = size
    files.holder = int(holder)
    session.add(files)
    session.commit()

def confirm_user(session, ids) -> bool:
    x = session.query(User).filter(User.id == ids).one()
    if x:
        x.confirmed = True
        session.add(x)
        session.commit()
        return True
    else:
        return False

def check_email(session, email:str) -> bool:
    try:
        x = session.query(User).filter(User.email == email).one()
        print(x[1])
        if x:
            return True
    except NoResultFound:
        return False

def check_user(session, email:str, password:str) -> str:
    try:
        pas = session.query(User).filter(User.email == email).one()
        if read_hash(pas.hashed_password) == read_hash(get_hash(password)):
            return 'successfully'
        elif session.query(User).filter(User.email == email).filter(User.confirmed == 0):
            return 'the account is not confirmed please check your email'
        else:
            return 'incorrect password or email'
    except NoResultFound:
        return 'user not found'
    except PendingRollbackError:
        session.rollback()
    


def delete_file(session, id):
    session.delete(session.query(Files).filter(Files.id == id).one())
    session.commit()

def get_owner_delete_file(session, email):
    return session.query(Deletes).filter(Deletes.owner == get_id_by_email(session, email)).all()

def add_owner_delete_file(session, name, owner):
    files = Deletes()
    files.name = name
    files.owner = get_id_by_email(session, owner)
    session.add(files)
    session.commit()
    
def delete_owner_file(session, name):
    session.delete(session.query(Deletes).filter(Deletes.name == name).one())
    session.commit()

def add_folder(session, name, owner, hold):
    fol = Folders()
    fol.name = name
    fol.holder = hold
    fol.owner = get_id_by_email(session, owner)
    session.add(fol)
    session.commit()

def get_folder(session, owner, hold):
    return session.query(Folders).filter(Folders.owner == get_id_by_email(session, owner)).filter(Folders.holder == hold).all()

def delete_folder(session, ids):
    session.delete(session.query(Folders).filter(Folders.id == ids).one())
    session.commit()

def get_owner_folder(session, id):
    return session.query(Folders).filter(Folders.id == id).one()[1]

def get_holder_by_id(session, id):
    try:
        return session.query(Folders).filter(Folders.id == id).one()
    except NoResultFound:
        return 0

def rek(session, folder):
    if int(folder) == 0:    
        return '/'
    if get_holder_by_id(session, folder).holder == 0:
        return f'/{ get_holder_by_id(session, folder).name}'
    else:
        return f'{rek(session, get_holder_by_id(session, folder).holder)}/{get_holder_by_id(session, folder).name}'

def get_session(session, email):
    id = get_id_by_email(session, email)
    return session.query(User.session_str).filter(User.id == id).one()[0]
