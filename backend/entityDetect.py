#
# @author Kevin Jesse
# @email kevin.r.jesse@gmail.com
#

import database_connect
cur = database_connect.db_connect()

entity2table = {'genre':('title', 'genres'), 'actor':('name', 'primaryname') ,
                'director': ('name', 'primaryname'), 'mpaa': ('title', 'mpaa'),}
entity_map = {'mpaa': 'Entertainment.ContentRating', 'genre': 'Entertainment.Genre', 'role': 'Entertainment.Role',
              'title': 'Entertainment.Title', 'rating': 'Entertainment.UserRating', 'actor': 'Entertainment.Person',
              'director' : 'Entertainment.Person'}
def entdata(state, entities):
    for ent in entities:
        if entity_map[state] == ent['type']:
            tc = entity2table[state]
            table = tc[0]
            column = tc[1]
            sqlstring = """SELECT COUNT(*) FROM """ + table + """ WHERE """ +column + """ LIKE '%""" + ent['entity'] + """%' LIMIT 1"""
            cur.execute(sqlstring)
            rows = cur.fetchall()
            if rows[0][0] > 0: return True
    return False


def detect(state, entities):
    answered = False
    answered = entdata(state, entities)
    print answered