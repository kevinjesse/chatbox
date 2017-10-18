#
# @author Kevin Jesse
# @email kevin.r.jesse@gmail.com
#

"""
Fetch Now Playing adds all the information necessary to populate the database for this weeks list of movies now playing
"""

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

    #Get now playing data
    url = "https://api.themoviedb.org/3/movie/now_playing?api_key=" + api_key + "&language=en-US&page=1"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    np_json = r.json()
    np = sorted(np_json['results'], key=lambda k: k['vote_count'], reverse=True)

    #Drop existing now playing small table
    sqlstring = """TRUNCATE TABLE tmd_nowplaying"""
    cur.execute(sqlstring)
    #rows = cur.fetchall()

    for each in np:

        # Get movie information with tmd id
        tmdid = each["id"]
        url = 'https://api.themoviedb.org/3/movie/' + str(tmdid) + '?api_key=' + api_key
        r = requests.get(url)
        mov_json = r.json()
        # pprint(mov_json)
        imdbid = mov_json['imdb_id']
        sqlstring = """INSERT INTO tmd_nowplaying (tconst, vote_count) VALUES ('""" + str(imdbid) + """','""" + str(each['vote_count']) + """');"""
        cur.execute(sqlstring)

        #Figure out if the current now play is not in database
        sqlstring = """SELECT tconst FROM title WHERE tconst='""" + imdbid + """'"""
        cur.execute(sqlstring)
        movie_exists = cur.fetchall()



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

        # If not in the database from earlier, put into approapriate tables
        if not movie_exists:
            #Title table insert
            sqlstring = """INSERT INTO title (tconst, primarytitle, originaltitle, startyear, genres, plot, mpaa, prodco, runtimeminutes) VALUES ('""" +\
                imdbid + """','""" + mov_json['title'].replace("'","''") + """','""" + mov_json['original_title'].replace("'","''") + """','""" + year + """','""" + genreStr + \
                """','""" + mov_json['overview'].replace("'","''") + """','""" + mpaa_rating  + """','""" +\
                 productionco + """','""" + str(mov_json['runtime']) +"""')"""
            print sqlstring
            cur.execute(sqlstring)

            #Ratings table insert
            sqlstring = """INSERT INTO ratings (tconst, averagerating, numvotes) VALUES ('""" + imdbid + """','""" + str(mov_json['vote_average']) + \
                        """','""" + str(mov_json['vote_count'])+"""')"""
            print sqlstring
            cur.execute(sqlstring)
            print
            print


if __name__ == "__main__":
    fetch()