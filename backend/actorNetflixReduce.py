import database_connect
import pickle,json
cur = database_connect.db_connect()
tconst_stars = {}
import operator

def gather():
    sqlstring = """SELECT title.tconst, stars.principalcast, crew.directors FROM title INNER JOIN stars ON title.tconst = stars.tconst INNER JOIN crew ON title.tconst = crew.tconst WHERE netflixid IS NOT NULL"""
    cur.execute(sqlstring)
    rows = cur.fetchall()
    for mov in rows:
        tconst_stars[mov[0]] = mov[1].split(' ') + mov[2].split(' ')
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
    popular = {}
    sqlstring = """SELECT nconst, pos from tmd_popular_actors"""
    cur.execute(sqlstring)
    rows = cur.fetchall()
    for row in rows:
        popular[row[0]] = int(row[1])


    namelist_pop = {}
    for each in namelist:
        if each in popular:
            namelist_pop[each] = popular[each]

    sorted_namelist_pop = sorted(namelist_pop.items(), key=operator.itemgetter(1))
    names = [i[0] for i in sorted_namelist_pop]
    print len(names)
    with open('namelist.txt', 'w') as outfile:
        pickle.dump(names, outfile)
    return names

def fetch():
    global tconst_stars
    gather()
    namelist = mergeActor()
    return tconst_stars, namelist

