from pprint import pprint
import os.path
import json
import datetime

from backend import database

cur = database.connector(dict_result=True)


def get_rec_check(user_id: str):
    sql_string = "SELECT * FROM users.convo_log WHERE user_id = %s"

    cur.execute(sql_string, (user_id, ))

    return cur.fetchall()


if __name__ == '__main__':
    results = get_rec_check("rec_check_{}".format(1))

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results.json'), 'w') as f:
        json.dump(results, f, default=lambda o: o.__str__() if isinstance(o, datetime.datetime) else o)