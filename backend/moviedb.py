#
# @author Kevin Jesse
# @email kevin.r.jesse@gmail.com
#

import database_connect
import requests

cur = database_connect.db_connect(dict_result=True)

cur.execute("SELECT api_key FROM api WHERE api_type='tmd'")
api_key = cur.fetchone()['api_key']


def movie_by_id(movie_id: str):
    """

    :param movie_id:
    :return:
    """
    sql_string = "SELECT * FROM title INNER JOIN crew ON title.tconst=crew.tconst INNER JOIN stars ON title.tconst = " \
                 "stars.tconst WHERE mpaa IS NOT NULL AND title.tconst = '{movie_id}'".format(movie_id=movie_id)
    cur.execute(sql_string)
    row = cur.fetchone()
    if not row:
        url = "https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}".format(movie_id=movie_id,
                                                                                       api_key=api_key)
        r = requests.get(url)
        if r.status_code != 200:
            return None
        mov_json = r.json()
        url = "https://api.themoviedb.org/3/movie/{movie_id}/release_dates?api_key={api_key}".format(movie_id=movie_id,
                                                                                                     api_key=api_key)
        rd = requests.get(url)
        if rd.status_code != 200:
            return None

        mpaa_rating = ""
        for each_dict in rd.json()['results']:
            for v in each_dict.value():
                if v == 'US':
                    mpaa_rating = each_dict['release_dates'][0]['certification']
        # pprint(mov_json)
        sql_string = "UPDATE title SET plot = '{}', mpaa = '{}', prodco = '{}' WHERE tconst = '{}' RETURNING *".format(
            mov_json['overview'].replace("'", "''"),
            mpaa_rating,
            mov_json['production_companies'][0]['name'].replace("'", "''"),
            movie_id
        )

        # print(sql_string)
        cur.execute(sql_string)
        row = cur.fetchone()
    return row


def actors_by_id(actors):
    actors_str = ", ".join(["('{}', {})".format(a, i + 1) for i, a in enumerate(actors)])

    sql_string = "SELECT primaryname FROM name join (VALUES {actors}) AS X (nconst, ordering) ON name.nconst = " \
                 "X.nconst ORDER BY X.ordering".format(actors=actors_str)
    # print(sql_string)
    cur.execute(sql_string)
    rows = cur.fetchall()
    # print('actors', rows)
    return [person['primaryname'] for person in rows] if rows else None


# def people_by_id(actors):
#     global names
#     actornamelist = []
#     for actor in actors:
#         try:
#             actornamelist.append(names[actor])
#         except Exception as e:
#             actornamelist.append("")
#     return actornamelist

# def directorsbyID(dlist):
#     directornamelist = []
#     for director in dlist:
#         sqlstring = """SELECT primaryname FROM name WHERE nconst='""" + director + """' LIMIT 1"""
#         cur.execute(sqlstring)
#         rows = cur.fetchall()
#         directornamelist.append(rows[0][0])
#     return directornamelist

# def upcomingMovies():
#     """
#     Return the top 5 upcoming movies
#     :return:
#     """

# def nowPlayingMovies():
#     """
#     retrieve from the DB the list of now playing movies
#     :return:
#     """
#     #JOING TABLE AND SORT BY DECREASING AND LIMIT TO MEH 10
#     sqlstring = """SELECT * FROM title INNER JOIN tmd_nowplaying ON title.tconst=tmd_nowplaying.tconst ORDER BY vote_count DESC LIMIT 10"""
#     cur.execute(sqlstring)
#     rows = cur.fetchall()
#     return rows
