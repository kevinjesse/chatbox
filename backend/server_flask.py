import logging
import json
from flask import Flask, request, jsonify

import dialogue_manager as dm

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(module)s %(name)s.%(funcName)s +%(lineno)s: %(levelname)-8s [%(process)d] %(message)s',
)

app = Flask(__name__)

dialogue_manager = dm.DialogueManager()


@app.route('/chatbox-rewrite', methods=['GET', 'POST'])
def receive_message():
    data = request.get_json(force=True)

    if data.get('action') == 'kill':
        dialogue_manager.end_user_session(data.get('id'))
        return jsonify({
            'killed': True
        })

    responses = dialogue_manager.utterance(data.get('id'), data)
    print('received message:', responses)
    return jsonify({
        'responses': responses
    })


def init_resources():
    dm.initResources()


if __name__ == '__main__':
    init_resources()
    app.run(host='0.0.0.0', port=20000)
