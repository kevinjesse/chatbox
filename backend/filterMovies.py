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


def filter_candidates(state: str, user_cache, user_tconst):
    backup_tconst = user_tconst
    match = True
    # print("Filter movie query")
    try:

        # if userCache[state2entity_map[state]] is None:
        #     return user_tconst

        if user_cache[state] is None:
            print("userCache state is None")
            return user_tconst, match
        # Write query -  would like to do this in generic form but each query has specific joins and rows.
        sqlstring = ''
        if state == 'genre':
            sqlstring += """SELECT tconst FROM title WHERE genres LIKE '%""" + user_cache['genre'][0] + """%'"""
            if len(user_cache['genre']) > 1:
                for gen in user_cache['genre'][1:]:
                    sqlstring+= """ AND genres LIKE '%""" + gen + """%'"""
            print(sqlstring)
            cur.execute(sqlstring)
            rows = cur.fetchall()
            tconst_list = [tconst[0] for tconst in rows]
            #print tconst_list


        elif state == 'actor':
            sqlstring = """SELECT nconst FROM name WHERE primaryname = '""" + user_cache[state][0] + """'"""
            if len(user_cache[state]) > 1:
                for more in user_cache[state][1:]:
                    sqlstring+=""" OR primaryname = '""" + more + """' """
            print(sqlstring)
            sqlstring +=  """ ORDER BY nconst ASC LIMIT """ + str(len(user_cache[state]))
            cur.execute(sqlstring)
            rows = cur.fetchall()

            if not rows:
                return user_tconst, False
            names=[r[0] for r in rows]

            sqlstringm = """SELECT tconst FROM stars WHERE principalcast LIKE '%""" + names[0] + """%' """
            print(names[:10])
            for each in names:
                sqlstringm += """ AND principalcast LIKE '%""" + each + """%'"""
            # sqlstringm += """AND principalcast LIKE '%""" + nm + """%' """

            print(sqlstringm)
            cur.execute(sqlstringm)
            rows = cur.fetchall()
            tconst_list = [tconst[0] for tconst in rows]

        #print sql_string
        elif state == 'director':
            # sql_string = """SELECT nconst FROM name WHERE primaryname = '""" + userCache[state][0] + """' ORDER BY nconst ASC LIMIT 1"""
            # cur.execute(sql_string)
            # rows = cur.fetchall()
            # nm = rows[0][0]
            sqlstring = """SELECT nconst FROM name WHERE primaryname = '""" + user_cache[state][0] + """'"""
            if len(user_cache[state]) > 1:
                for more in user_cache[state][1:]:
                    sqlstring+=""" OR primaryname = '""" + more + """' """
            print(sqlstring)
            sqlstring +=  """ ORDER BY nconst ASC LIMIT """ + str(len(user_cache[state]))
            cur.execute(sqlstring)
            rows = cur.fetchall()
            if not rows:
                return user_tconst, False
            names=[r[0] for r in rows]

            sqlstringm = """SELECT tconst FROM crew WHERE directors LIKE '%""" + names[0] + """%' """
            # for act in userCache[state][1:]:
            #     sql_string = """SELECT nconst FROM name WHERE primaryname LIKE '%""" + act + """%' ORDER BY nconst ASC LIMIT 1"""
            #     cur.execute(sql_string)
            #     rows = cur.fetchall()
            #     nm = rows[0][0]
            #     sqlstringm += """AND directors LIKE '%""" + nm + """%' """

            print(names[:10])
            for each in names:
                sqlstringm += """ AND directors LIKE '%""" + each + """%'"""

            print(sqlstringm)
            cur.execute(sqlstringm)
            rows = cur.fetchall()
            tconst_list = [tconst[0] for tconst in rows]
            # print "Tconst_list count: {}".format(len(tconst_list))
            # print "user_tconst count: {}".format(len(user_tconst))
            # candidatelist = list(set(user_tconst).intersection(tconst_list))
            # if len(candidatelist) != 0: #the new list has nothing
            #user_tconst = list(set(user_tconst).intersection(tconst_list))
            #return user_tconst

        elif state == 'mpaa':
            sqlstring += """SELECT tconst FROM title WHERE mpaa LIKE '%""" + user_cache['mpaa'][0] + """%'"""
            if len(user_cache['mpaa']) > 1:
                for mpaa in user_cache['mpaa'][1:]:
                    """ AND mpaa LIKE '%""" + mpaa + """%'"""
            cur.execute(sqlstring)
            rows = cur.fetchall()
            tconst_list = [tconst[0] for tconst in rows]
            print(tconst_list[:10])
            print(sqlstring)
        else:
            # IF STATE IS NOT IMPLEMENTED JUST RETURN what we started with
            # for now just return user_tconst
            return user_tconst, match

        # TODO: This might change our research assumptions
        if len(tconst_list) <= 0:
            tconst_list = backup_tconst
        return tconst_list, match
    except KeyError:
        # Error with states while developing, ignore this filter_candidates round
        print("Error filter_candidates movies; {}".format(KeyError))
        tconst_list = backup_tconst
        match = False


    candidatelist = list(set(user_tconst).intersection(tconst_list))
    if len(candidatelist) != 0: #the new list has nothing
        #print "len(candidatelist) != 0"
        user_tconst = candidatelist
    else:
        #print "len(candidatelist) == 0 using backup"
        user_tconst = backup_tconst
        match = False
    return user_tconst ,match