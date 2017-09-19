import database_connect
cur = database_connect.db_connect()

import numpy

def init():
    sqlstring = """SELECT COUNT(*) FROM title"""
    cur.execute(sqlstring)
    rows = cur.fetchall()
    movie_size = rows[0][0]
    #a = numpy.array([[]])

# def find (user_pref):
#     sqlstring = """SELECT * FROM title INNER JOIN tmd_nowplaying ON title.tconst=tmd_nowplaying.tconst ORDER BY vote_count DESC LIMIT 10"""
#     cur.execute(sqlstring)
#     rows = cur.fetchall()
#
