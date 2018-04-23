import logging
import json
from flask import Flask, request, jsonify

import dialogue_manager

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(module)s %(name)s.%(funcName)s +%(lineno)s: %(levelname)-8s [%(process)d] %(message)s',
)

app = Flask(__name__)

dm = dialogue_manager.DialogueManager(api_type='mturk')


@app.route('/chatbox-rewrite', methods=['GET', 'POST'])
def receive_message():
    data = request.get_json(force=True)

    if data.get('action') == 'kill':
        dm.end_user_session(data.get('id'))
        return jsonify({
            'killed': True
        })

    responses = dm.utterance(data.get('id'), data)
    print('received message:', responses)
    return jsonify({
        'responses': responses
    })


def init_resources():
    dialogue_manager.init_resources()


if __name__ == '__main__':
    init_resources()
    app.run(host='0.0.0.0', port=20000)
