#
# @author Kevin Jesse
# @email kevin.r.jesse@gmail.com
#

"""
Filter movies reduces the available movies based on the dialogue selections
"""
import random

import database_connect
import moviedb
import matrix_fact
import user_manager as um

from typing import TYPE_CHECKING, Dict, List, Any

cur = database_connect.db_connect()

titles = []
hypothesis = 'cf'


def init_resources(mode_hypothesis: str):
    global titles, hypothesis
    hypothesis = mode_hypothesis
    try:
        # Init list of candidate movies - (relatively new 9-20-17)
        sql_string = """SELECT tconst FROM title WHERE netflixid IS NOT NULL"""
        cur.execute(sql_string)
        rows = cur.fetchall()
        for mov in rows:
            titles.append(mov[0])
    except Exception as e:
        raise e


class MovieManager:

    def __init__(self, session_data: um.SessionData):
        self.session = session_data
        self.movie_candidates = titles
        self.movies_with_ratings = []
        self._last_rec_id = 0

    def filter_candidates(self, state: str) -> bool:

        if state == 'genre' and len(self.session.movie_preferences['genre']) > 0:
            sql_string = "SELECT tconst FROM title WHERE {}".format(
                " AND ".join(
                    ["genres LIKE '%{genre}%'".format(genre=i)
                     for i in self.session.movie_preferences['genre']]
                )
            )
            cur.execute(sql_string)
            rows = cur.fetchall()
            movies = [tconst[0] for tconst in rows]

        elif state == 'actor' and len(self.session.movie_preferences['actor']) > 0:
            sql_string = (
                    "SELECT nconst FROM name WHERE {} ".format(
                        " OR ".join(
                            ["primaryname = '{actor}'".format(actor=i)
                             for i in self.session.movie_preferences['actor']]
                        )
                    ) + "ORDER BY nconst ASC LIMIT {}".format(
                str(len(self.session.movie_preferences['actor']))
            )
            )
            cur.execute(sql_string)
            rows = cur.fetchall()

            if not rows:
                return False

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

        elif state == 'director' and len(self.session.movie_preferences['director']) > 0:
            sql_string = (
                    "SELECT nconst FROM name WHERE {} ".format(
                        " OR ".join(
                            ["primaryname = '{director}'".format(director=i)
                             for i in self.session.movie_preferences['director']]
                        )
                    ) + "ORDER BY nconst ASC LIMIT {}".format(
                str(len(self.session.movie_preferences['director']))
            )
            )
            cur.execute(sql_string)
            rows = cur.fetchall()

            if not rows:
                return False

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

        elif state == 'mpaa' and len(self.session.movie_preferences['mpaa']) > 0:
            sql_string = (
                "SELECT tconst FROM title WHERE {} ".format(
                    " AND ".join(
                        ["mpaa LIKE '%{mpaa}%'".format(mpaa=i)
                         for i in self.session.movie_preferences['mpaa']]
                    )
                )
            )
            cur.execute(sql_string)
            rows = cur.fetchall()

            movies = [tconst[0] for tconst in rows]

        else:
            return False

        if len(movies) <= 0:
            return False

        candidates = list(set(self.movie_candidates).intersection(movies))
        if len(candidates) != 0:  # the new list has nothing
            # print("len(candidates) != 0")
            self.movie_candidates = candidates
            return True
        else:
            # print("len(candidatelist) == 0 using backup")
            return False

    def matrix_recommend(self):
        recommendation = matrix_fact.recommend(self.session.movie_preferences)
        print("!!! recommendation: \n", recommendation)
        self.movies_with_ratings = recommendation

        tconst, self._last_rec_id = matrix_fact.recommendation_text(self._last_rec_id)
        return tconst

    def cf_recommend(self):  # cf_recommend
        sql_string = (
                "SELECT averagerating FROM ratings join (VALUES {alis})" +
                "AS X (tconst, ordering) ON ratings.tconst = X.tconst ORDER BY X.ordering"
        ).format(alis=", ".join(["('{}', {})".format(str(m), str(i + 1))
                                 for i, m in enumerate(self.movie_candidates)]))

        cur.execute(sql_string)
        rows = cur.fetchall()
        self.movies_with_ratings = sorted(zip(self.movie_candidates, rows),
                                          key=lambda tup: tup[1],
                                          reverse=True)
        print("movies_with_ratings", len(self.movies_with_ratings))
        return self.movies_with_ratings

    def utterance(self):
        if hypothesis == 'cf':
            movie_with_score = self.cf_recommend()
            tie = [movie[0] for movie in movie_with_score if movie_with_score[0][1] == movie[1]]
            movie_id = random.choice(tie)
        elif hypothesis == 'mf':
            movie_id = self.matrix_recommend()
        else:
            return
        if movie_id:

            movie = moviedb.movie_by_id(movie_id)
            print("Movie data:", movie)
            # process directors and actors into readable for output
            import template_manager as tm

            sentences = tm.get_sentence(dialogue_type='utterances', state='tell', return_all=True)

            sentences[0] = sentences[0].format(movie_name=movie['primarytitle'], movie_year=movie['startyear'])
            sentences[1] = sentences[1].format(
                movie_name=movie['primarytitle'],
                actors=', '.join(
                    [i for i in (moviedb.actors_by_id(movie['principalcast'].split(' ')) or ['<no actors>'])]
                ),
                directors=', '.join(
                    [i for i in (moviedb.actors_by_id(movie['directors'].split(' ')) or ['<no directors>'])]
                ))
            sentences[2] = sentences[2].format(
                movie_length=movie['runtimeminutes'],
                genre="{article} {genres}".format(
                   article="an" if movie['genres'][0].lower() in ['a', 'e', 'i', 'o', 'u'] else "a",
                   genres=movie['genres'].replace(' ', ',', movie['genres'].count(' ') - 1)
                                         .replace(' ', ' and ')
                                         .replace(',', ', ')
                ),
                mpaa=movie['mpaa'])

            return movie, sentences
        else:
            return None, None

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
