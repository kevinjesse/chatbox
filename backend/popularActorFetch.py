import database_connect
import requests
import re
from pprint import pprint
cur = database_connect.db_connect()

imdb_ids = []
def fetch():
    t = 1
    while len(imdb_ids) < 1020:
        top20(t)
        t +=1

def top20(page):
    """
    This function will update from TMD to my database now playing
    :return:
    """
    import operator
    global imdb_ids
    sqlstring = """SELECT api_key FROM api WHERE api_type='tmd'"""
    cur.execute(sqlstring)
    rows = cur.fetchall()
    api_key = rows[0][0]

    url = "https://api.themoviedb.org/3/person/popular?api_key=" + api_key + "&language=en-US&page=" +str(page)
    print page
    r = requests.get(url)
    if r.status_code != 200:
        return None

    np_json = r.json()

    orderedPopID = [person['id'] for person in np_json['results']]
    for tmd_id in orderedPopID:
        url = "https://api.themoviedb.org/3/person/"+ str(tmd_id) +"?api_key=" + api_key + "&language=en-US"
        r = requests.get(url)
        if r.status_code != 200:
            return None

        person_json = r.json()
        if person_json["imdb_id"]:
            imdb_ids.append(person_json["imdb_id"])

    print len(imdb_ids)

def push():
    global imdb_ids
    sqlstring = """TRUNCATE TABLE tmd_popular_actors"""
    cur.execute(sqlstring)
    sqlstring = """INSERT INTO tmd_popular_actors (nconst, pos) VALUES """
    for imdb in imdb_ids[:-1]:
        sqlstring += """('""" + str(imdb) + """','""" + str(imdb_ids.index(imdb) + 1) + """') ,"""
    sqlstring += """('""" + str(imdb_ids[-1]) + """','""" + str(imdb_ids.index(imdb_ids[-1]) + 1) + """')"""
    cur.execute(sqlstring)
    # print sqlstring

if __name__ == "__main__":
    fetch()
    # print imdb_ids
    push()
    print imdb_ids