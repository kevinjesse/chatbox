#
# @author Kevin Jesse
# @email kevin.r.jesse@gmail.com
#

"""
Filter movies reduces the available movies based on the dialogue selections
"""
import random

import database_connect
import movieCtrl
import user_manager as um

cur = database_connect.db_connect()


class MovieManager:

    def __init__(self):
        movie_candidates = []


def filter_candidates(state: str, user_session_data: um.SessionData, movie_candidates: list):

    if state == 'genre' and len(user_session_data.movie_preferences['genre']) > 0:
        sql_string = "SELECT tconst FROM title WHERE {}".format(
            " AND ".join(
                ["genres LIKE '%{genre}%'".format(genre=i)
                    for i in user_session_data.movie_preferences['genre']]
            )
        )
        cur.execute(sql_string)
        rows = cur.fetchall()
        movies = [tconst[0] for tconst in rows]

    elif state == 'actor' and len(user_session_data.movie_preferences['actor']) > 0:
        sql_string = (
            "SELECT nconst FROM name WHERE {} ".format(
                " OR ".join(
                    ["primaryname = '{actor}'".format(actor=i)
                     for i in user_session_data.movie_preferences['actor']]
                )
            ) + "ORDER BY nconst ASC LIMIT {}".format(
                str(len(user_session_data.movie_preferences['actor']))
            )
        )
        cur.execute(sql_string)
        rows = cur.fetchall()

        if not rows:
            return None

        names = [r[0] for r in rows]

        sql_string = (
            "SELECT tconst FROM stars WHERE {} ".format(
                " AND ".join(
                    ["principalcast LIKE '%{actor}%'".format(actor=i)
                     for i in names[:10]]
                )
            )
        )

        cur.execute(sql_string)
        rows = cur.fetchall()
        movies = [tconst[0] for tconst in rows]

    elif state == 'director' and len(user_session_data.movie_preferences['director']) > 0:
        sql_string = (
            "SELECT nconst FROM name WHERE {} ".format(
                " OR ".join(
                    ["primaryname = '{director}'".format(director=i)
                     for i in user_session_data.movie_preferences['director']]
                )
            ) + "ORDER BY nconst ASC LIMIT {}".format(
                str(len(user_session_data.movie_preferences['director']))
            )
        )
        cur.execute(sql_string)
        rows = cur.fetchall()

        if not rows:
            return None

        names = [r[0] for r in rows]

        sql_string = (
            "SELECT tconst FROM crew WHERE {} ".format(
                " AND ".join(
                    ["directors LIKE '%{director}%'".format(director=i)
                     for i in names[:10]]
                )
            )
        )

        cur.execute(sql_string)
        rows = cur.fetchall()
        movies = [tconst[0] for tconst in rows]

    elif state == 'mpaa' and len(user_session_data.movie_preferences['mpaa']) > 0:
        sql_string = (
            "SELECT tconst FROM title WHERE {} ".format(
                " AND ".join(
                    ["mpaa LIKE '%{mpaa}%'".format(mpaa=i)
                     for i in user_session_data.movie_preferences['mpaa']]
                )
            )
        )
        cur.execute(sql_string)
        rows = cur.fetchall()

        movies = [tconst[0] for tconst in rows]

    else:
        return None

    if len(movies) <= 0:
        return None

    candidates = list(set(movie_candidates).intersection(movies))
    if len(candidates) != 0:  # the new list has nothing
        # print("len(candidates) != 0")
        return candidates
    else:
        # print("len(candidatelist) == 0 using backup")
        return None


def sort_candidates(movie_candidates):
    sql_string = (
        "SELECT averagerating FROM ratings join (VALUES {alis})" +
        "AS X (tconst, ordering) ON ratings.tconst = X.tconst ORDER BY X.ordering"
    ).format(alis=", ".join(["('{}', {})".format(str(m), str(i+1))
                             for i, m in enumerate(movie_candidates)]))

    cur.execute(sql_string)
    rows = cur.fetchall()
    movies_with_ratings = sorted(zip(movie_candidates, rows), key=lambda tup: tup[1],
                             reverse=True)
    print("movies_with_ratings", len(movies_with_ratings))
    return movies_with_ratings


def movie_to_utterance(movie_with_score):
    output = []
    if movie_with_score:
        tie = [movie[0] for movie in movie_with_score if movie_with_score[0][1] == movie[1]]
        movie_id = random.choice(tie)

        data = movieCtrl.moviebyID(movie_id)
        print(data)
        # process directors and actors into readable for output
        output.append("How about " + data[1] + " (" + data[
            3] + ")? ")
        if len(data) > 10:
            dlist = data[12].split(' ')
            alist = data[14].split(' ')
            actorNameList = movieCtrl.actorsbyID(alist)
            directorNameList = movieCtrl.actorsbyID(dlist)
            output.append(data[1] + " stars " + ", ".join(actorNameList) + " and is directed by " + \
                          ", ".join(directorNameList) + ".")
        output.append("This film is {} minutes long. It is {} {} movie, and is rated {}.".format(
            data[8],
            "an" if any(v in data[4][:1].lower() for v in ['a','e','i','o','u']) else "a",
            data[4].replace(" ", ",", data[4].count(" ") - 1) \
                .replace(" ", " and ") \
                .replace(",", ", "),
            data[6]
        ))
    return output


# def filter_candidates(state: str, user_cache, user_tconst):
#     backup_tconst = user_tconst
#     match = True
#     # print("Filter movie query")
#     try:
#
#         # if userCache[state2entity_map[state]] is None:
#         #     return user_tconst
#
#         if user_cache[state] is None:
#             print("userCache state is None")
#             return user_tconst, match
#         # Write query -  would like to do this in generic form but each query has specific joins and rows.
#         sqlstring = ''
#         if state == 'genre':
#             sqlstring += """SELECT tconst FROM title WHERE genres LIKE '%""" + user_cache['genre'][0] + """%'"""
#             if len(user_cache['genre']) > 1:
#                 for gen in user_cache['genre'][1:]:
#                     sqlstring+= """ AND genres LIKE '%""" + gen + """%'"""
#             print(sqlstring)
#             cur.execute(sqlstring)
#             rows = cur.fetchall()
#             tconst_list = [tconst[0] for tconst in rows]
#             #print tconst_list
#
#
#         elif state == 'actor':
#             sqlstring = """SELECT nconst FROM name WHERE primaryname = '""" + user_cache[state][0] + """'"""
#             if len(user_cache[state]) > 1:
#                 for more in user_cache[state][1:]:
#                     sqlstring+=""" OR primaryname = '""" + more + """' """
#             print(sqlstring)
#             sqlstring +=  """ ORDER BY nconst ASC LIMIT """ + str(len(user_cache[state]))
#             cur.execute(sqlstring)
#             rows = cur.fetchall()
#
#             if not rows:
#                 return user_tconst, False
#             names=[r[0] for r in rows]
#
#             sqlstringm = """SELECT tconst FROM stars WHERE principalcast LIKE '%""" + names[0] + """%' """
#             print(names[:10])
#             for each in names:
#                 sqlstringm += """ AND principalcast LIKE '%""" + each + """%'"""
#             # sqlstringm += """AND principalcast LIKE '%""" + nm + """%' """
#
#             print(sqlstringm)
#             cur.execute(sqlstringm)
#             rows = cur.fetchall()
#             tconst_list = [tconst[0] for tconst in rows]
#
#         #print sql_string
#         elif state == 'director':
#             # sql_string = """SELECT nconst FROM name WHERE primaryname = '""" + userCache[state][0] + """' ORDER BY nconst ASC LIMIT 1"""
#             # cur.execute(sql_string)
#             # rows = cur.fetchall()
#             # nm = rows[0][0]
#             sqlstring = """SELECT nconst FROM name WHERE primaryname = '""" + user_cache[state][0] + """'"""
#             if len(user_cache[state]) > 1:
#                 for more in user_cache[state][1:]:
#                     sqlstring+=""" OR primaryname = '""" + more + """' """
#             print(sqlstring)
#             sqlstring +=  """ ORDER BY nconst ASC LIMIT """ + str(len(user_cache[state]))
#             cur.execute(sqlstring)
#             rows = cur.fetchall()
#             if not rows:
#                 return user_tconst, False
#             names=[r[0] for r in rows]
#
#             sqlstringm = """SELECT tconst FROM crew WHERE directors LIKE '%""" + names[0] + """%' """
#             # for act in userCache[state][1:]:
#             #     sql_string = """SELECT nconst FROM name WHERE primaryname LIKE '%""" + act + """%' ORDER BY nconst ASC LIMIT 1"""
#             #     cur.execute(sql_string)
#             #     rows = cur.fetchall()
#             #     nm = rows[0][0]
#             #     sqlstringm += """AND directors LIKE '%""" + nm + """%' """
#
#             print(names[:10])
#             for each in names:
#                 sqlstringm += """ AND directors LIKE '%""" + each + """%'"""
#
#             print(sqlstringm)
#             cur.execute(sqlstringm)
#             rows = cur.fetchall()
#             tconst_list = [tconst[0] for tconst in rows]
#             # print "Tconst_list count: {}".format(len(tconst_list))
#             # print "user_tconst count: {}".format(len(user_tconst))
#             # candidatelist = list(set(user_tconst).intersection(tconst_list))
#             # if len(candidatelist) != 0: #the new list has nothing
#             #user_tconst = list(set(user_tconst).intersection(tconst_list))
#             #return user_tconst
#
#         elif state == 'mpaa':
#             sqlstring += """SELECT tconst FROM title WHERE mpaa LIKE '%""" + user_cache['mpaa'][0] + """%'"""
#             if len(user_cache['mpaa']) > 1:
#                 for mpaa in user_cache['mpaa'][1:]:
#                     """ AND mpaa LIKE '%""" + mpaa + """%'"""
#             cur.execute(sqlstring)
#             rows = cur.fetchall()
#             tconst_list = [tconst[0] for tconst in rows]
#             print(tconst_list[:10])
#             print(sqlstring)
#         else:
#             # IF STATE IS NOT IMPLEMENTED JUST RETURN what we started with
#             # for now just return user_tconst
#             return user_tconst, match
#
#         # TODO: This might change our research assumptions
#         if len(tconst_list) <= 0:
#             tconst_list = backup_tconst
#         return tconst_list, match
#     except KeyError:
#         # Error with states while developing, ignore this filter_candidates round
#         print("Error filter_candidates movies; {}".format(KeyError))
#         tconst_list = backup_tconst
#         match = False
#
#
#     candidatelist = list(set(user_tconst).intersection(tconst_list))
#     if len(candidatelist) != 0: #the new list has nothing
#         #print "len(candidatelist) != 0"
#         user_tconst = candidatelist
#     else:
#         #print "len(candidatelist) == 0 using backup"
#         user_tconst = backup_tconst
#         match = False
#     return user_tconst ,match