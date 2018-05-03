import logging
import json
from flask import Flask, request, jsonify

import dialogue_manager

# logging.basicConfig(
#     level=logging.DEBUG,
#     format='%(asctime)s %(module)s %(name)s.%(funcName)s +%(lineno)s: %(levelname)-8s [%(process)d] %(message)s',
# )

app = Flask(__name__)

dm = dialogue_manager.DialogueManager(api_type='cobot')


@app.route('/chatbox-cobot', methods=['GET', 'POST'])
def receive_message():
    data = request.get_json(force=True)
    utterance = parse_input(data)
    print(utterance)
    return utterance


def parse_input(json: dict):
    if json.get('action') == 'kill':
        dm.end_user_session(json.get('id'))
        return jsonify({
            'killed': True
        })

    id = json.get('id')

    if id is not None:
        print('received text:', json.get('text'))
        responses = dm.utterance(user_id=id, message=json)
        return jsonify({
            'responses': responses
        })
    else:
        return None


def init_resources():
    dialogue_manager.init_resources(mode='cobot')


if __name__ == '__main__':
    init_resources()
    app.run(host='0.0.0.0', port=20000)
