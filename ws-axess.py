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
from flask_restful import Resource, Api

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


def connection_init():
    global conn
    conn = sqlite3.connect('axess-ws.db')


def connection_closed():
    conn.close()
    print(" <-- Desligado da BD")


def successful_transaction():
    global som, rele, sucesso
    connection_closed()
    return som + "\r\n" + rele + "\r\n"


def denied_transaction():
    global sound_deny
    connection_closed()
    return sound_deny + "\r\n"


def checkCard():
   global conn
   card = card_uid()
   connection_init()
   cursor = conn.execute("select count(idCard) from cards where apbStatus = 0 and cardUid = " + '"' + card + '"')
   result = cursor.fetchone()
   if result[0] is 1:
            successful_transaction()
            return successful_transaction()
   else:
            denied_transaction()
            return denied_transaction()


@app.route('/<path:path>')
def catch_all(path):
    pedido = path
    # batch = request.args
    online_transaction = request.args.getlist('trsn')
    print(pedido)
    if pedido == "batch":
        return "ack=1"
    elif pedido == "online":
        result = checkCard()
        return result
    elif path == "keepalive":
        return "ack=1" + "\r\n"
    else:
        pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=porta)
