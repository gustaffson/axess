#####################################################################################
#  Axess TMC Control Webservice - ver. 0.4
#  Developed by Gustavo Pinto
#  Not licenced for any usage - Copyright reserved
#
#  Sample de Http Request terminal -> software
#
#####################################################################################

import sqlite3
from flask import Flask, request
from flask_restful import Api

app = Flask(__name__)
api = Api(app)

# Parameters
som, rele = "beep=1", "relay=1,50"
sound_deny = "beep=2"
sound_accept = "beep=1"
porta = '5002'


def card_uid():
    req_uri = request.url
    start_badge = (req_uri.find("?"))
    end_badge = (req_uri.find("&"))
    raw_string = req_uri[start_badge:end_badge]
    raw_left_date = raw_string.find(",")
    raw_left_time = raw_string.find(",", raw_left_date + 1)
    raw_left_0 = raw_string.find(",", raw_left_time + 1)
    raw_left_card = raw_string.find(",", raw_left_0 + 1)
    raw_right_card = raw_string.find(",", raw_left_card + 1)
    final = raw_string[(raw_left_card + 1):raw_right_card]
    return final


def checkCard():
    global conn
    card = card_uid()
    conn = sqlite3.connect('axess-ws.db')
    cursor = conn.execute("select count(idCard) from cards where apbStatus = 0 and cardUid = " + '"' + card + '"')
    result = cursor.fetchone()
    if result[0] is 1:
        conn.close()
        return som + "\r\n" + rele + "\r\n"
    else:
        conn.close()
        return sound_deny + "\r\n"


@app.route('/<path:path>')
def catch_all(path):
    pedido = path
    if pedido == "batch":
        return "ack=1"
    elif pedido == "online":
        result = checkCard()
        return result
    elif path == "keepalive":
        return "ack=1" + "\r\n"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=porta)
