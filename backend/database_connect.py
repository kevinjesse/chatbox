#
# @author Kevin Jesse
# @email kevin.r.jesse@gmail.com
#

"""
Database Connect serves to connect to the database postgres, as the master user. Autocommit has been turned on so
all inserts, updates, and deletes will be enforced atomically
"""

import psycopg2
import psycopg2.extras


def connect(dict_result=False):
    cur = None
    try:
        conn = psycopg2.connect(
            database='postgres',
            user='postgres',
            password='2251',
            host='localhost',
            connect_timeout=30
        )
        conn.autocommit = True  # Auto commit must be on if you want changes to be immediate for insert/update
        cur = conn.cursor() if not dict_result else conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.itersize = 10000
    except:
        print("[ERROR] couldn't connect to the database")
    return cur
