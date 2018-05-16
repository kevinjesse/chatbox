import requests
import time
from pprint import pprint

url = "http://interaction.cs.ucdavis.edu:20000/chatbox-rewrite"

r = requests.session()

sleep = 0.5


def post_json(state: str, text: str, id: str, action):
    return {
        'state': state,
        'text': text,
        'id': id,
        'action': action
    }


id = "server_flask_test_100"


def common_query():
    out = r.post(url, json=post_json('intro', "", id, 'ping'))
    pprint(out.json())
    time.sleep(sleep)

    out = r.post(url, json=post_json('genre', "action movies", id, None))
    pprint(out.json())
    time.sleep(sleep)

    out = r.post(url, json=post_json('actor', "keanu reeves", id, None))
    pprint(out.json())
    time.sleep(sleep)

    out = r.post(url, json=post_json('director', "anyone", id, None))
    pprint(out.json())
    time.sleep(sleep)

    out = r.post(url, json=post_json('mpaa', "any", id, None))
    pprint(out.json())
    time.sleep(sleep)


def not_seen_like_movie_query():
    # out = r.post(url, to_dict=post_json('tell', "yes", id, None))
    # pprint(out.to_dict())
    # time.sleep(sleep)

    out = r.post(url, json=post_json('tell', "No", id, None))
    pprint(out.json())
    time.sleep(sleep)

    out = r.post(url, json=post_json('tell', "Yes", id, None))
    pprint(out.json())
    time.sleep(sleep)


def not_seen_not_like_movie_query():
    # out = r.post(url, to_dict=post_json('tell', "yes", id, None))
    # pprint(out.to_dict())
    # time.sleep(sleep)

    out = r.post(url, json=post_json('tell', "No", id, None))
    pprint(out.json())
    time.sleep(sleep)

    out = r.post(url, json=post_json('tell', "no", id, None))
    pprint(out.json())
    time.sleep(sleep)


def kill_query():
    out = r.post(url, json=post_json('', "", id, "kill"))
    pprint(out.json())


common_query()
not_seen_not_like_movie_query()
not_seen_like_movie_query()
kill_query()


if '__name__' == '__main__':
    common_query()
    not_seen_not_like_movie_query()
    not_seen_like_movie_query()
    kill_query()
