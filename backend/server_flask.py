import argparse
import os
import json
from pprint import pprint
from flask import Flask, request, jsonify, render_template
import flask_cors

import dialogue_manager
#
# logging.basicConfig(
#     level=logging.DEBUG,
#     format='%(asctime)s %(module)s %(name)s.%(funcName)s +%(lineno)s: %(levelname)-8s [%(process)d] %(message)s',
# )

parser = argparse.ArgumentParser()
parser.add_argument("mode")
parser.add_argument("hypothesis")
parser.add_argument("-p", "--port", action="store", dest="port")
parser.add_argument("-d", "--prod", action="store_true")
args = parser.parse_args()


app = Flask(__name__, template_folder=os.path.abspath('../frontend/html'))
flask_cors.CORS(app)

dm = None


@app.route('/chatbox/api/main', methods=['GET'])
def test():
    print(request.args)
    return jsonify({
        'response': "GET CONNECTION SUCCESS"
    })


@app.route('/chatbox/api/main', methods=['POST'])
# @flask_cors.cross_origin()
def receive_message():
    data = request.get_json(force=True)
    utterance = parse_input(data)
    print("sending message")
    pprint(utterance)
    return utterance


def parse_input(json: dict):
    if json.get('action') == 'kill':
        dm.end_user_session(json.get('id'))
        return jsonify({
            'killed': True
        })

    id = json.get('id')

    if id is not None:
        if args.mode == 'reconly':
            responses = dm.utterance_silent(user_id=id, message=json)
        else:
            print('received text:', json.get('text'))
            state, responses = dm.utterance(user_id=id, message=json)
        return jsonify({
            'responses': responses,
            'state': state
        })
    else:
        return None


@app.route('/chatbox/api/db', methods=['POST'])
def request_database():
    data = request.get_json(force=True)
    if data.get('fetch_item') == 'dialogue':
        result = _fetch_dialogue(data.get('id'))
        return jsonify({
            'result': result.get('dialogue'),
            'convo_id': result.get('convo_id')
        })


def _fetch_dialogue(user_id: str) -> dict:
    import history_manager as hm
    return hm.last_user_history(user_id=user_id)


@app.route('/chatbox/api/survey_submit', methods=['POST'])
def survey_submit():
    data = request.form.to_dict()
    # print(data)
    import history_manager as hm
    hm.save_user_survey(data)
    return render_template('survey_submit.html', validation_code=data.get('cryptID'))


def init_resources():
    global dm
    dialogue_manager.init_resources(mode=args.mode, mode_hypothesis=args.hypothesis)
    dm = dialogue_manager.DialogueManager()


if __name__ == '__main__':
    init_resources()

    config = None
    config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config.json')
    try:
        f = open(config_dir, 'r')
        config = json.load(f)
    except Exception as e:
        print(e)
        exit(1)

    if args.port:
        port = args.port
    elif args.prod:
        port = config['port']
        with open(config_dir, 'w') as f:
            config['is_prod'] = True
            json.dump(config, f)
    elif not args.prod and args.prod is not None:
        port = config['port-test']
        with open(config_dir, 'w') as f:
            config['is_prod'] = False
            json.dump(config, f)
    else:
        port = 20000

    app.run(host='0.0.0.0', port=port, threaded=True)
