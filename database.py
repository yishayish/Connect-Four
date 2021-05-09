import sqlite3
from utils import threaded

DB_FILE = 'engine.sqlite'


def get_db():
    db = sqlite3.connect(
        DB_FILE,
        detect_types=sqlite3.PARSE_DECLTYPES
    )
    db.row_factory = sqlite3.Row

    return db


def init_db():
    db = get_db()

    with open('schema.sql') as f:
        db.executescript(f.read())


@threaded
def store_position(matrix, score):
    db = get_db()
    db.execute('INSERT OR IGNORE INTO engine (id, score) VALUES (?, ?)',
               (str(matrix), score))
    db.commit()


def search_position(matrix):
    db = get_db()
    score = db.execute('SELECT score FROM engine WHERE id = ?',
                       (str(matrix),)).fetchone()
    if score:
        return score['score']
    else:
        return None


def db_to_dict():
    db = get_db()
    data = db.execute('SELECT * FROM engine').fetchall()
    return {eval(val['id']): val['score'] for val in data}
