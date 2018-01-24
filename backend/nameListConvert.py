import database_connect
import pickle,json
cur = database_connect.db_connect()
newlist = []

def lookup():
    with open('namelist.txt', 'r') as outfile:
        namelist = pickle.load(outfile)
    count = 1
    for each in namelist:
        print count
        count +=1
        sqlstring = """SELECT primaryname from name WHERE nconst = '""" + each + """'"""
        # print sqlstring
        cur.execute(sqlstring)
        rows = cur.fetchall()
        # print rows
        newlist.append(rows[0])

    with open('fullNamelist.txt', 'w') as outfile:
        pickle.dump(newlist, outfile)

def fix():
    newlist = []
    with open('fullNamelist.txt', 'r') as outfile:
        namelist = pickle.load(outfile)
    for each in namelist:
        newlist.append(each[0])
    with open('fullNamelist1.txt', 'w') as outfile:
        pickle.dump(newlist, outfile)

fix()