import database_connect
import pickle,json
cur = database_connect.db_connect()
tconst_stars = {}

with open('namelist.txt', 'r') as fp:
    namelist = pickle.load(fp)

fullnamelist = []
for each in namelist:
    print each
    sqlstring = """SELECT primaryname from name WHERE nconst = '""" + each +"""'"""
    cur.execute(sqlstring)
    rows = cur.fetchall()
    fullnamelist.append(rows[0][0])

with open('fullnameList2', 'w') as outfile:
    pickle.dump(fullnamelist, outfile)
