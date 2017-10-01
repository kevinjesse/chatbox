#
# @author Kevin Jesse
# @email kevin.r.jesse@gmail.com
#

import psycopg2

def db_connect():
    cur = None
    try:
        conn = psycopg2.connect("dbname='postgres' user='postgres' host='localhost' password='postgres'")
        conn.autocommit = True #Auto commit must be on if you want changes to be immediate for insert/update
        cur = conn.cursor()
    except:
        print "[ERROR] couldn't connect to the database"
    return cur