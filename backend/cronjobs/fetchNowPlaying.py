import database_connect
import requests


def fetch():
    """
    This function will update from TMD to my database now playing
    :return:
    """
    import operator
    api_key = '166c772e6b94241f893e94b22f874c02'
    url = "https://api.themoviedb.org/3/movie/now_playing?api_key=" + api_key + "&language=en-US&page=1"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    np_json = r.json()
    np = sorted(np_json['results'], key=lambda k: k['vote_count'], reverse=True)
    #pprint(np)

    sqlstring = """TRUNCATE TABLE tmd_nowplaying"""
    cur.execute(sqlstring)
    #rows = cur.fetchall()

    for each in np:
        tmdid = each["id"]
        url = 'https://api.themoviedb.org/3/movie/' + str(tmdid) + '?api_key=' + api_key
        r = requests.get(url)
        mov_json = r.json()
        imdbid = mov_json['imdb_id']
        sqlstring = """INSERT INTO tmd_nowplaying (tconst, vote_count) VALUES ('""" + str(imdbid) + """','""" + str(each['vote_count']) + """');"""
        cur.execute(sqlstring)

        sqlstring = """SELECT tconst FROM title WHERE tconst='""" + imdbid + """'"""
        cur.execute(sqlstring)
        rows = cur.fetchall()

        year = re.search('\d{4}', mov_json['release_date']).group(0)
        genreStr = ""
        for id in mov_json['genre_ids']:
            """SELECT genre FROM tmd_genres WHERE id='""" + id + """'"""
            cur.execute(sqlstring)
            rows = cur.fetchall()
            for each in rows: genreStr.append(each + " ")
        url = 'https://api.themoviedb.org/3/movie/' + movieID + '/release_dates?api_key=' + api_key
        rd = requests.get(url)
        rd_json = rd.json()
        mpaa_rating = ''
        for each_dict in rd_json['results']:
            for k, v in each_dict.iteritems():
                if v == 'US':
                    mpaa_rating = each_dict['release_dates'][0]['certification']
        if not rows: #nothing exists
            sqlstring = """INSERT INTO title (tconst, primarytitle, originaltitle, startyear, genres, plot, mpaa, prodco, runtimeminutes) VALUES ('""" +\
                imdbid + """','""" + mov_json['title'] + """','""" + mov_json['original_title'] + """','""" + year + """','""" + genreStr + \
                """','""" + mov_json['overview'].replace("'","''") + """','""" + mpaa_rating  + """','""" +\
                mov_json['production_companies'][0]['name'].replace("'","''") + """','""" + mov_json['runtime'] +"""')"""
            print sqlstring
            print

        #DONT FORGET RATINGS TABLE!


if __name__ == "__main__":
    fetch()