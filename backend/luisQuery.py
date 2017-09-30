#
# @author Kevin Jesse
# @email kevin.r.jesse@gmail.com
#

import requests

app_id = 'a40a20d8-b506-4df2-83a7-981fb73ac684'
sub_key= '8e429f4906f646fba1bdb54ed0baaf3a'
base_url = 'https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/'


def ctrl(text):
    url = base_url + app_id + '?subscription-key=' + sub_key + '&verbose=true&timezoneOffset=0&q=' + text
    print url
    r = requests.get(url)
    if r.status_code != 200:
        return None
    json = r.json()
    return json['query'], json['topScoringIntent'], json['entities']