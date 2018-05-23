import json
import os
import logging

from flask import Flask, request
from pymessenger.bot import Bot
from settings import APP_STATIC

import dialogue_manager

# import server_hook_socket as hook
# import template

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(module)s %(name)s.%(funcName)s +%(lineno)s: %(levelname)-8s [%(process)d] %(message)s',
)

app = Flask(__name__)
tokens = json.load(open(os.path.join(APP_STATIC, 'tokens.to_dict')))
ACCESS_TOKEN = tokens['ACCESS_TOKEN']
VERIFY_TOKEN = tokens['VERIFY_TOKEN']
bot = Bot(ACCESS_TOKEN)

dm = dialogue_manager.DialogueManager()


# We will receive messages that Facebook sends our bot at this endpoint
@app.route('/chatbox-messenger', methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook."""
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    # if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
        output = request.get_json()
        print('to_dict', output)
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if message.get('message'):
                    # Facebook Messenger ID for user so we know where to send response back to
                    recipient_id = message['sender']['id']
                    if message['message'].get('text'):
                        response_sent_text = get_message(
                            user_id=recipient_id,
                            user_input=message['message'].get('text')
                        )
                        send_message(recipient_id, response_sent_text)
                    # if user sends us a GIF, photo,video, or any other non-text item
                    if message['message'].get('attachments'):
                        response_sent_nontext = get_message(user_id=recipient_id)
                        send_message(recipient_id, response_sent_nontext)
    return "Message Processed"


def verify_fb_token(token_sent):
    # take token sent by facebook and verify it matches the verify token you sent
    # if they match, allow the request, else return an error
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


# chooses a random message to send to the user
def get_message(user_id: int, user_input: str):
    return dm.utterance(user_id,
                        message={
                            'action': 'submit',
                            'id': 'messenger-predict-{id}'.format(id=user_id),
                            'text': user_input,
                            'mode': False
                        })


# uses PyMessenger to send response to user
def send_message(recipient_id, response: list):
    # sends user the text message provided via input response parameter
    for r in response:
        bot.send_text_message(recipient_id, r)
    return "success"


if __name__ == '__main__':
    try:
        dialogue_manager.init_resources()
        app.run(host='0.0.0.0', port=20100)
    except Exception as e:
        print(e)
