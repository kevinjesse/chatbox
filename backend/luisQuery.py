# #
# # @author Kevin Jesse
# # @email kevin.r.jesse@gmail.com
# #
#
# from typing import Tuple
#
# import requests
#
# import database_connect
#
# cur = database_connect.connector()
#
# sql_string = "SELECT api_key FROM api WHERE api_type='luisid'"
# cur.execute(sql_string)
# rows = cur.fetchall()
# # This api_key will be moved to a database after initial build
# app_id = rows[0][0]
#
# sql_string = "SELECT api_key FROM api WHERE api_type='luis'"
# cur.execute(sql_string)
# rows = cur.fetchall()
# sub_key= rows[0][0]
# base_url = "https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/"
#
# sql_string = "SELECT api_key FROM api WHERE api_type='bing1'"
# cur.execute(sql_string)
# rows = cur.fetchall()
# bing_key= rows[0][0]
#
#
# def query(text: str) -> Tuple[str, str, str]:
#     url = base_url + app_id + '?subscription-key=' + sub_key + '&spellCheck=true&bing-spell-check-subscription-key=' \
#           + bing_key + '&verbose=true&timezoneOffset=0&q=' + text.strip()
#     # print('luisQuery:', url)
#     r = requests.get(url)
#     if r.status_code != 200:
#         return None
#     to_dict = r.to_dict()
#     return to_dict['query'], to_dict['topScoringIntent'], to_dict['entities']