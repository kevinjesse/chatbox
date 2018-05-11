import requests
from pprint import pprint

url = "http://interaction.cs.ucdavis.edu:20500/chatbox-rewrite"

r = requests.session()


def post_json(state: str, text: str, id: str, action):
    return {
        'state': state,
        'text': text,
        'id': id,
        'action': action
    }


id = "server_flask_test_100"


def common_query():
    out = r.post(url, json=post_json('intro', "", id, None))
    pprint(out.json())

    out = r.post(url, json=post_json('genre', "action movies", id, None))
    pprint(out.json())

    out = r.post(url, json=post_json('actor', "keanu reeves", id, None))
    pprint(out.json())

    out = r.post(url, json=post_json('director', "anyone", id, None))
    pprint(out.json())

    out = r.post(url, json=post_json('mpaa', "any", id, None))
    pprint(out.json())


def not_seen_like_movie_query():
    # out = r.post(url, json=post_json('tell', "yes", id, None))
    # pprint(out.json())

    out = r.post(url, json=post_json('tell', "No", id, None))
    pprint(out.json())

    out = r.post(url, json=post_json('tell', "Yes", id, None))
    pprint(out.json())


def not_seen_not_like_movie_query():
    # out = r.post(url, json=post_json('tell', "yes", id, None))
    # pprint(out.json())

    out = r.post(url, json=post_json('tell', "No", id, None))
    pprint(out.json())

    out = r.post(url, json=post_json('tell', "no", id, None))
    pprint(out.json())


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
