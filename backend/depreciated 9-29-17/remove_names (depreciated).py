#
# @author Kevin Jesse
# @email kevin.r.jesse@gmail.com
#

import database_connect
cur = database_connect.db_connect()

def remove():
    sqlstring = """SELECT tconst FROM title"""
    cur.execute(sqlstring)
    rows = cur.fetchall()
    mlist = []
    for mset in rows:
        mlist.append(mset[0])

    needactor = False
    tempActorlist = []
    sqlstring = """SELECT nconst, knownfortitles FROM name"""
    cur.execute(sqlstring)
    rows = cur.fetchall()
    # for filmtup in rows:
    #     namefilmlist = filmtup[1].split(" ")
    #     print namefilmlist
        # for knownfor in namefilmlist:
        #     if knownfor not in mlist:
        #         tempActorlist.append(filmtup[0])
        #         print filmtup[0]

















if __name__ == "__main__":
    remove()