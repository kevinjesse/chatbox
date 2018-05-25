from pprint import pprint
import os.path
import json
import csv
import datetime
import argparse

from typing import List

parser = argparse.ArgumentParser()
parser.add_argument("--turk", dest="turkpath", action="store_const")
args = parser.parse_args()

from backend import database

cur = database.connector(dict_result=True)


def get_rec_check(user_id: List[str]):
    sql_string = "SELECT * FROM users.survey_log WHERE turk_id IN %s"

    cur.execute(sql_string, (tuple(user_id), ))
    surveys = cur.fetchall()
    print(surveys)
    return surveys


def read_turk_csv(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        return [r[0] for r in reader]


if __name__ == '__main__':
    if args.turkpath:
        results = get_rec_check(read_turk_csv(args.turkpath))
    else:
        results = get_rec_check(["rec_check_1"])

    # with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results.json'), 'w') as f:
    #     json.dump(results, f, default=lambda o: o.__str__() if isinstance(o, datetime.datetime) else o)