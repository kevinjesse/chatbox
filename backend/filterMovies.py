#
# @author Kevin Jesse
# @email kevin.r.jesse@gmail.com
#

"""
Filter movies reduces the available movies based on the dialogue selections
"""

import database_connect
cur = database_connect.db_connect()

state2entity_map ={'genre': 'genre', 'role': 'role', 'mpaa':'mpaa', 'title': 'title', 'rating': 'rating',
                       'actor':'person', 'director': 'person', 'year': 'year', 'tell': 'tell' , 'bye': 'bye'}

# state2tablerow = {'genre': ('title','genres'), 'role': 'role', 'mpaa':('title','mpaa'), 'title': 'title', 'rating': 'rating',
#                        'actor':('stars', 'principalcast'), 'director': 'person', 'year': 'year'}




def ctrl(state, userCache, user_tconst):
    backup_tconst = user_tconst
    try:
        if userCache[state2entity_map[state]] is None:
            return user_tconst
        # Write query -  would like to do this in generic form but each query has specific joins and rows.
        sqlstring = ''
        if state == 'genre':
            sqlstring += """SELECT tconst FROM title WHERE genres LIKE '%""" + userCache['genre'][0] + """%'"""
            if len(userCache['genre']) > 1:
                for gen in userCache['genre'][1:]:
                    """ AND genres LIKE '%""" + gen + """%'"""
            cur.execute(sqlstring)
            rows = cur.fetchall()
            tconst_list = [tconst[0] for tconst in rows]

        elif state == 'actor':
            sqlstring = """SELECT nconst FROM name WHERE primaryname = '""" + userCache[state2entity_map[state]][0] + """' LIMIT 1"""
            cur.execute(sqlstring)
            rows = cur.fetchall()
            nm = rows[0][0]
            sqlstringm = """SELECT tconst FROM stars WHERE principalcast LIKE '%""" + nm + """%' """
            for act in userCache[state2entity_map[state]][1:]:
                sqlstring = """SELECT nconst FROM name WHERE primaryname LIKE '%""" + act + """%' LIMIT 1"""
                cur.execute(sqlstring)
                rows = cur.fetchall()
                nm = rows[0][0]
                sqlstringm += """AND principalcast LIKE '%""" + nm + """%' """

            cur.execute(sqlstringm)
            rows = cur.fetchall()
            tconst_list = [tconst[0] for tconst in rows]
        #print sqlstring
        elif state == 'director':
            sqlstring = """SELECT nconst FROM name WHERE primaryname = '""" + userCache[state2entity_map[state]][
                0] + """' LIMIT 1"""
            cur.execute(sqlstring)
            rows = cur.fetchall()
            nm = rows[0][0]
            sqlstringm = """SELECT tconst FROM crew WHERE directors LIKE '%""" + nm + """%' """
            for act in userCache[state2entity_map[state]][1:]:
                sqlstring = """SELECT nconst FROM name WHERE primaryname LIKE '%""" + act + """%' LIMIT 1"""
                cur.execute(sqlstring)
                rows = cur.fetchall()
                nm = rows[0][0]
                sqlstringm += """AND directors LIKE '%""" + nm + """%' """

            cur.execute(sqlstringm)
            rows = cur.fetchall()
            tconst_list = [tconst[0] for tconst in rows]
            print "Tconst_list count: {}".format(len(tconst_list))
            print "user_tconst count: {}".format(len(user_tconst))
            user_tconst = list(set(user_tconst).union(tconst_list))
            return user_tconst



        else:
            # IF STATE IS NOT IMPLEMENTED JUST RETURN what we started with
            # for now just return user_tconst
            return user_tconst
    except KeyError as e:
        # Error with states while developing, ignore this filter round
        tconst_list = backup_tconst

    user_tconst = list(set(user_tconst).intersection(tconst_list))
    return user_tconst