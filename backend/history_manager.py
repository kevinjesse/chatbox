from datetime import datetime
import database
from psycopg2.extras import Json

cur = database.connector(dict_result=True)
no_write = False


def save_user_history(user_id: str, conversation: dict, mode: str, mode_hypothesis: str):
    if not no_write:
        try:
            movie_preferences = Json(conversation['movie_preferences'])
            recommendations = Json(conversation['recommendations'])
            dialogue = Json(conversation['dialogue'])
        except Exception as e:
            print(e)
            return
        
        sql_string = "INSERT INTO users.convo_log " \
                     "(timestamp, user_id, mode_hypothesis, mode, movie_preferences, recommendations, dialogue) " \
                     "VALUES (%(timestamp)s, %(user_id)s, %(mode_hypothesis)s, %(mode)s, " \
                     "%(movie_preferences)s, %(recommendations)s, %(dialogue)s)"

        cur.execute(sql_string, {
            'timestamp': datetime.now(),
            'user_id': user_id,
            'mode_hypothesis': mode_hypothesis,
            'mode': mode,
            'movie_preferences': movie_preferences,
            'recommendations': recommendations,
            'dialogue': dialogue
        })

        print("saving user history to database")


def last_user_history(user_id: str) -> dict:
    sql_string = "SELECT * FROM users.convo_log WHERE user_id = %s ORDER BY timestamp DESC LIMIT 1"

    cur.execute(sql_string, (user_id,))
    history = cur.fetchone()
    # print(history)
    return history


def save_user_survey(form_data: dict):
    sql_string = "SELECT TRUE FROM users.survey_log WHERE convo_id=%s"

    cur.execute(sql_string, (form_data["convoID"], ))
    row_exists = cur.fetchone()

    if row_exists:
        print("Trying to save survey but row already exist (convoID = {}".format(form_data["convoID"]))
        return

    sql_string = "INSERT INTO users.survey_log " \
                 "(convo_id, user_id, crypt_id, turk_id, convo_ratings, survey_ratings, survey_comment, timestamp) " \
                 "VALUES (%(convo_id)s, %(user_id)s, %(crypt_id)s, %(turk_id)s, " \
                 "%(convo_ratings)s, %(survey_ratings)s, %(survey_comment)s, %(timestamp)s)"

    from pprint import pprint
    pprint(form_data)

    convo_ratings = [int(form_data['rating-q{}'.format(i + 1)]) for i in range(int(form_data['history-count']))]
    survey_ratings = [int(form_data['survey-q{}'.format(i + 1)]) for i in range(3)]

    cur.execute(sql_string, {
        'convo_id': form_data["convoID"],
        'user_id': form_data["userID"],
        'crypt_id': form_data["cryptID"],
        'turk_id': form_data["turkID"],
        'convo_ratings': convo_ratings,
        'survey_ratings': survey_ratings,
        'survey_comment': form_data["survey-q4"],
        'timestamp': datetime.fromtimestamp(float(form_data["timestamp"]))
    })

    print("user survey saved")