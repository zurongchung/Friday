import sqlite3

class Model:

    def __init__(self, name):
        self.conn = sqlite3.connect(name)
        self.curs = self.conn.cursor()

    def create(self, tb_name):
        self.curs.execute('''CREATE TABLE records
        (id INT NOT NULL primary key,
        qty INT NOT NULL,
        index INT NOT NULL,
        remains INT
        )''')

    def insert(self, col, val):
        pass

    def update(self, col, val):
        pass

    def select(self, col):
        pass