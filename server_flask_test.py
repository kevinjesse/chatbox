import requests

url = "http://interaction.cs.ucdavis.edu:20000/chatbox-rewrite"

r = requests.session()

out = r.post(url, json={
    'test': 'test'
})

print(out)
