#
# @author Kevin Jesse
# @email kevin.r.jesse@gmail.com
#

"""
Filter movies reduces the available movies based on the dialogue selections
"""
import random
import psycopg2.sql as sql

import database
import moviedb
#import matrix_fact
import user_manager as um

from typing import List

titles = []
hypothesis = 'cf'


def init_resources(mode_hypothesis: str):
    global titles, hypothesis
    hypothesis = mode_hypothesis
    try:
        if hypothesis != 'cf':
            matrix_fact.start_engine()

        # Init list of candidate movies - (relatively new 9-20-17)
        sql_string = """SELECT tconst FROM title WHERE netflixid IS NOT NULL"""
        cur = database.connector()
        cur.execute(sql_string)
        rows = cur.fetchall()
        for mov in rows:
            titles.append(mov[0])
    except Exception as e:
        raise e


class MovieManager:

    def __init__(self, user_id: str, session_data: um.SessionData):
        self.session = session_data
        self.movie_candidates = titles
        if hypothesis in ['mf', 'online']:
            self.matrixFact = matrix_fact.MatrixFact(user_id)
        elif hypothesis in ['cf']:
            self.movies_with_ratings = []
            self.is_first_recommendation = True

    def filter_candidates(self, state: str) -> bool:

        if state == 'genre' and len(self.session.movie_preferences['genre']) > 0:
            sql_string = sql.SQL("SELECT tconst FROM title WHERE {}").format(
                sql.SQL(' AND ').join(
                    [sql.SQL("genres LIKE '%%%s%%'").format(item)
                     for item in self.session.movie_preferences['genre']]
                )
            )

            cur = database.connector()
            cur.execute(sql_string)
            rows = cur.fetchall()
            movies = [tconst[0] for tconst in rows]

        elif state == 'actor' and len(self.session.movie_preferences['actor']) > 0:
            sql_string = sql.SQL("SELECT nconst FROM name WHERE {} ORDER BY nconst ASC LIMIT {}").format(
                sql.SQL(" OR ").join(
                    [sql.SQL("primaryname = {}").format(sql.Literal(actor))
                     for actor in self.session.movie_preferences['actor']]
                ),
                sql.Literal(len(self.session.movie_preferences['actor']))
            )
            cur = database.connector()
            cur.execute(sql_string)
            rows = cur.fetchall()

            if not rows:
                return False

            names = [r[0] for r in rows]

            sql_string = sql.SQL("SELECT tconst FROM stars WHERE {}").format(
                sql.SQL(" AND ").join(
                    [sql.SQL("principalcast LIKE {}").format(sql.Literal('%' + actor + '%'))
                     for actor in names[:10]]
                )
            )

            cur.execute(sql_string)
            rows = cur.fetchall()
            movies = [tconst[0] for tconst in rows]

        elif state == 'director' and len(self.session.movie_preferences['director']) > 0:
            sql_string = sql.SQL("SELECT nconst FROM name WHERE {} ORDER BY nconst ASC LIMIT {}").format(
                sql.SQL(" OR ").join(
                    [sql.SQL("primaryname = {}").format(sql.Literal(actor))
                     for actor in self.session.movie_preferences['director']]
                ),
                sql.Literal(len(self.session.movie_preferences['director']))
            )

            cur = database.connector()
            cur.execute(sql_string)
            rows = cur.fetchall()

            if not rows:
                return False

            names = [r[0] for r in rows]

            sql_string = sql.SQL("SELECT tconst FROM stars WHERE {}").format(
                sql.SQL(" AND ").join(
                    [sql.SQL("principalcast LIKE {}").format(sql.Literal('%' + director + '%'))
                     for director in names[:10]]
                )
            )

            cur.execute(sql_string)
            rows = cur.fetchall()
            movies = [tconst[0] for tconst in rows]

        elif state == 'mpaa' and len(self.session.movie_preferences['mpaa']) > 0:
            sql_string = sql.SQL("SELECT tconst FROM title WHERE {}").format(
                sql.SQL(" AND ").join(
                    [sql.SQL("mpaa LIKE {}").format(sql.Literal('%' + mpaa + '%'))
                     for mpaa in self.session.movie_preferences['mpaa']]
                )
            )

            cur = database.connector().execute(sql_string)
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

    def next_recommendation(self):
        if hypothesis == 'cf':
            self.movies_with_ratings.pop(0)
        elif hypothesis == 'online':
            # self.matrixFact.dislike()
            pass

    def online_dislike(self):
        self.matrixFact.dislike()
        self.matrixFact.online_recommend(self.session.movie_preferences)

    def online_recommend(self):
        if self.matrixFact.is_first_recommendation:
            self.matrixFact.recommend(self.session.movie_preferences)
        tconst = self.matrixFact.get_movie()

        return tconst

    def matrix_recommend(self):
        if self.matrixFact.is_first_recommendation:
            self.matrixFact.recommend(self.session.movie_preferences)
        tconst = self.matrixFact.get_movie()

        return tconst

    def cf_recommend(self):  # cf_recommend
        sql_string = sql.SQL(
            "SELECT averagerating FROM ratings JOIN ({}) AS X (tconst, ordering) ON ratings.tconst = X.tconst "
            "ORDER BY X.ordering"
        ).format(
            sql.SQL("VALUES ") +
            sql.SQL(', ').join([sql.SQL("({}, {})").format(sql.Literal(movie), sql.Literal(i + 1))
                                for i, movie in enumerate(self.movie_candidates)])
        )

        cur = database.connector()
        cur.execute(sql_string)
        rows = cur.fetchall()
        self.movies_with_ratings = sorted(zip(self.movie_candidates, rows),
                                          key=lambda tup: tup[1],
                                          reverse=True)
        print("movies_with_ratings", len(self.movies_with_ratings))

        self.is_first_recommendation = False

        return self.movies_with_ratings

    def utterance(self):
        if hypothesis == 'cf':
            movie_with_score = self.cf_recommend() if self.is_first_recommendation else self.movies_with_ratings
            tie = [movie[0] for movie in movie_with_score if movie_with_score[0][1] == movie[1]]
            movie_ihtod = random.choice(tie)
        elif hypothesis == 'mf':
            movie_id = self.matrix_recommend()  # if self.is_first_recommendation else self.movies_with_ratings
        elif hypothesis == 'online':
            movie_id = self.online_recommend()
        else:
            return
        if movie_id:
            print(movie_id)
            movie = moviedb.movie_by_id(movie_id)
            print("Movie returning:", movie['primarytitle'])
            # process directors and actors into readable for output
            import template_manager as tm

            sentences = tm.get_sentence(dialogue_type='utterances', state='tell', return_all=True).copy()

            sentences[0] = sentences[0].format(movie_name=movie['primarytitle'], movie_year=movie['startyear'])
            sentences[1] = sentences[1].format(
                movie_name=movie['primarytitle'],
                actors=_list_to_comma_with_and(
                    moviedb.actors_by_id(movie['principalcast'].split(' ') or ['<no actors>']), limit=0
                ),
                directors=_list_to_comma_with_and(
                    moviedb.actors_by_id(movie['directors'].split(' ') or ['<no directors>']), limit=0
                )
            )
            sentences[2] = sentences[2].format(
                movie_length=movie['runtimeminutes'],
                genre="{article} {genres}".format(
                   article="an" if movie['genres'][0].lower() in 'aeiou' else "a",
                   genres=_list_to_comma_with_and(movie['genres'].split())
                ),
                mpaa=movie['mpaa'])

            print("sentences", sentences)

            return movie, sentences.copy()
        else:
            return None, None


def _list_to_comma_with_and(input_list: List[str], limit: int=0) -> str:
    if len(input_list) > limit > 0:
        return ', '.join(input_list[:limit]) + ' and more'
    elif len(input_list) == 1:
        return input_list[0]
    else:
        return ', '.join(input_list[:-1]) + ' and {}'.format(input_list[-1])

