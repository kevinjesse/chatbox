#
# @author Kevin Jesse
# @email kevin.r.jesse@gmail.com
#

import requests
import database_connect
cur = database_connect.db_connect()

sqlstring = """SELECT api_key FROM api WHERE api_type='luisid'"""
cur.execute(sqlstring)
rows = cur.fetchall()
# This api_key will be moved to a database after initial build
app_id = rows[0][0]

sqlstring = """SELECT api_key FROM api WHERE api_type='luis'"""
cur.execute(sqlstring)
rows = cur.fetchall()
sub_key= rows[0][0]
base_url = 'https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/'

sqlstring = """SELECT api_key FROM api WHERE api_type='bing1'"""
cur.execute(sqlstring)
rows = cur.fetchall()
bing_key= rows[0][0]


def ctrl(text):
    url = base_url + app_id + '?subscription-key=' + sub_key + '&spellCheck=true&bing-spell-check-subscription-key=' \
          + bing_key +'&verbose=true&timezoneOffset=0&q=' + text.strip()
    print url
    r = requests.get(url)
    if r.status_code != 200:
        return None
    json = r.json()
    return json['query'], json['topScoringIntent'], json['entities']