import psycopg2
from config import config

class Dbconnetor ():


    def __init__(self):
        self.config = config()

    def connect(self):
        try:
            params = self.config
            conn = psycopg2.connect(**params)
            cur = conn.cursor()
            return conn, cur
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)


    def execute_select_query (self, query):
        conn, cur = self.connect()
        with conn:
            cur.execute(query)
            result = cur.fetchone()
            return result

    def execute_select_many_query (self, query):
        conn, cur = self.connect()
        with conn:
            cur.execute(query)
            result = cur.fetchall()
            return result

    def execute_insert_query (self, query):
        conn, cur = self.connect()
        with conn:
            cur.execute(query)
            conn.commit()