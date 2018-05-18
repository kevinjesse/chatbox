import requests
import time
from pprint import pprint

url = "http://interaction.cs.ucdavis.edu:20000/chatbox/api/main"
url_h = "http://interaction.cs.ucdavis.edu:20000/chatbox/api/db"

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
    print(out.request)
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


def rec_query():
    out = r.post(url, json={
        'id': id,
        'action': None,
        'preferences': {
            'genre': [],
            'actor': [],
            'director': [],
            'mpaa': []
        }
    })
    pprint(out.json())


def default_test():
    common_query()
    not_seen_not_like_movie_query()
    not_seen_like_movie_query()
    kill_query()


def history_test():
    out = r.post(url_h, json={
        'fetch_item': 'dialogue',
        'id': '5afe5152e6ff7'
    })
    pprint(out.json())


history_test()
