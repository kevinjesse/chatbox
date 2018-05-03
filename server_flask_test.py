import requests

url = "http://interaction.cs.ucdavis.edu:20000/chatbox-rewrite"

r = requests.session()


def post_json(state: str, text: str, id: str, action):
    return {
        'state': state,
        'text': text,
        'id': id,
        'action': action
    }


id = "server_flask_test_100"

out = r.post(url, json=post_json('intro', "", id, None))
print(out.json())

out = r.post(url, json=post_json('genre', "action movies", id, None))
print(out.json())

out = r.post(url, json=post_json('actor', "keanu reeves", id, None))
print(out.json())

out = r.post(url, json=post_json('director', "anyone", id, None))
print(out.json())

out = r.post(url, json=post_json('mpaa', "any", id, None))
print(out.json())

out = r.post(url, json=post_json('tell', "No", id, None))
print(out.json())

out = r.post(url, json=post_json('tell', "Yes", id, None))
print(out.json())

out = r.post(url, json=post_json('', "", id, "kill"))
print(out.json())