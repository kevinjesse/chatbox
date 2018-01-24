import database_connect
import pickle,json
cur = database_connect.db_connect()
tconst_stars = {}


def gather():
    sqlstring = """SELECT title.tconst, stars.principalcast FROM title INNER JOIN stars ON title.tconst = stars.tconst WHERE netflixid IS NOT NULL"""
    cur.execute(sqlstring)
    rows = cur.fetchall()
    for mov in rows:
        tconst_stars[mov[0]] = mov[1].split(' ')
    with open('tconst_stars.json', 'w') as outfile:
        json.dumps(tconst_stars, outfile)


    #print tconst_stars

def mergeActor():
    #allActors = set()
    allActors = []
    for mov, stars in tconst_stars.iteritems():
        # print type(stars)
        # allActors|=set(stars)
        allActors.extend(stars)

    #print allActors
    namelist = list(set(allActors))
    with open('namelist.txt', 'w') as outfile:
        pickle.dump(namelist, outfile)
    return namelist

def fetch():
    global tconst_stars
    gather()
    namelist = mergeActor()
    return tconst_stars, namelist