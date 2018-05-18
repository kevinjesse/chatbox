from datetime import datetime
import database_connect
from psycopg2.extras import Json

cur = database_connect.connect(dict_result=True)
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
