from sqlalchemy import create_engine, MetaData, Table, Integer, String, \
    Column, Boolean, Identity

def create_bd():
    metadata = MetaData()
    engine = create_engine(f"sqlite:///core/sql/db/data.db")
    customers = Table('User', metadata,
        Column('id', Integer(), Identity(start=1, cycle=True), primary_key=True),
        Column('email', String(200), nullable=False, unique=True),
        Column('hashed_password', String(200), nullable=False),
        Column('confirmed', Boolean() , nullable=False),
        Column('session_str', String(200), nullable=False),
    )
    files = Table('Files', metadata,
        Column('id', String(200), unique=True),
        Column('owner', Integer(), nullable=False),
        Column('name', String(200), nullable=False),
        Column('size', Integer(), nullable=False),
        Column('holder', Integer(), nullable=False),
    )
    deletes = Table('deletes', metadata,
        Column('id', Integer(), Identity(start=1, cycle=True), primary_key=True),
        Column('name', String(200)),
        Column('owner', Integer(), nullable=False),
    )
    folders = Table('Folders', metadata,
        Column('id', Integer(), Identity(start=1, cycle=True), primary_key=True),
        Column('name', String(200)),
        Column('owner', Integer(), nullable=False),
        Column('holder', Integer(), nullable=False),
    )
    metadata.create_all(engine)