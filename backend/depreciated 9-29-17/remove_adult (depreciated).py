#
# @author Kevin Jesse
# @email kevin.r.jesse@gmail.com
#

import database_connect
import string
def removeadult(cur):
    adult_movieids = []
    sqlstring = """SELECT tconst FROM title WHERE isadult='1'"""
    cur.execute(sqlstring)
    rows = cur.fetchall()
    for row in rows:
        adult_movieids.append(row)

    #
    # #ALSO TOO SLOW O(N)^2
    # # adult_stars = []
    # sqlstring = """SELECT nconst, knownfortitles FROM name"""
    # cur.execute(sqlstring)
    # rows = cur.fetchall()
    # film_to_stars = []
    # for row in rows:
    #     for m in row[1].split(' '):
    #         film_to_stars.append(m)
    #
    # print list(set(adult_movieids).intersection(film_to_stars))

    # for row in rows:
    #     #row[0] for adultmovie in adult_movieids if adultmovie in row[1]
    #     adult_stars.append(row[0] for adultmovie in adult_movieids if adultmovie in row[1])

    #print adult_stars

    #     for row in rows:
    #         if row not in adult_stars:
    #             adult_stars.append(row)
    #Super slow O^2
    # for adult_film in adult_movieids:
    #     sqlstring = """SELECT nconst FROM name WHERE knownfortitles LIKE '%""" + adult_film[0] + """%'"""
    #     cur.execute(sqlstring)
    #     rows = cur.fetchall()
    #     for row in rows:
    #         if row not in adult_stars:
    #             adult_stars.append(row)
    #
    # print adult_stars
cur = database_connect.db_connect()
#removeadult(cur)

