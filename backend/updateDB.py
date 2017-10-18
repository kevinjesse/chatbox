#
# @author Kevin Jesse
# @email kevin.r.jesse@gmail.com
#

import database_connect
import requests
import re
from pprint import pprint
cur = database_connect.db_connect()
def fetch():
    """
    This function will update from TMD to my database now playing
    :return:
    """
    import operator
    sqlstring = """SELECT api_key FROM api WHERE api_type='tmd'"""
    cur.execute(sqlstring)
    rows = cur.fetchall()
    # This api_key will be moved to a database after initial build
    api_key = rows[0][0]

    #Get movies in database
    sqlstring = """SELECT tconst FROM title WHERE mpaa IS NULL OR plot IS NULL OR prodco IS NULL"""
    cur.execute(sqlstring)
    movies = cur.fetchall()
    print len(movies)
    temp_limit = 0

    for each in movies:
        # temp_limit +=1
        # if temp_limit ==4: break

        # Get movie information with tmd id
        tmdid = each[0]
        url = 'https://api.themoviedb.org/3/movie/' + str(tmdid) + '?api_key=' + api_key
        r = requests.get(url)
        mov_json = r.json()
        # pprint(mov_json)
        imdbid = mov_json['imdb_id']

        #Gather and format Necessary data
        year = re.search('\d{4}', mov_json['release_date']).group(0)
        genreStr = ""
        for each in mov_json['genres']:
            sqlstring = """SELECT genre FROM tmd_genres WHERE id='""" + str(each['id']) + """'"""
            cur.execute(sqlstring)
            rows = cur.fetchall()
            for each in rows: genreStr += each[0] + " "
        url = 'https://api.themoviedb.org/3/movie/' + imdbid + '/release_dates?api_key=' + api_key
        rd = requests.get(url)
        rd_json = rd.json()
        mpaa_rating = ''
        if mov_json['production_companies']:
            productionco = mov_json['production_companies'][0]['name'].replace("'","''")
        else:
            productionco = 'NULL'
        for each_dict in rd_json['results']:
            for k, v in each_dict.iteritems():
                if v == 'US':
                    mpaa_rating = each_dict['release_dates'][0]['certification']

        sqlstring = """UPDATE title SET plot ='""" + mov_json['overview'].replace("'","''") + """', mpaa ='""" + mpaa_rating +"""' , prodco = '""" + productionco + """' WHERE tconst = '""" + imdbid +"""'"""
        print sqlstring
        cur.execute(sqlstring)
        print
        print



if __name__ == "__main__":
    fetch()