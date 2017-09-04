#####################################################################################
#  Axess TMC Control Webservice
#  Developed by Gustavo Pinto
#  Not licenced for any usage - Copyright reserved
#
#  Sample de Http Request terminal -> software
#
#  http://localhost:8181/online
#  ?badge=20101201,152110,0,0,123456789,1
#  &TerminalID=AxDoorMainEntrance
#  &mac=00:04:24:00:00:00:11:22
#####################################################################################

import sqlite3
from flask import Flask, request
from flask_restful import Resource, Api
from time import gmtime, strftime

app = Flask(__name__)
api = Api(app)

# Relay Parameters
som, rele = "beep=1", "relay=1,50"
somCr, releCr = som + '\r', rele + '\r'
somCrlf, releCrlf = somCr + '\n', releCr + '\n'
soundDeny = "beep=2"  # Action Deny Entry - Axess Default
sucesso = " --- Sucesso! --- "

# Demo Parameters
# cardUid = '123456789'  # Card UID Demo
terminalRequest = "http://localhost:8181/online?badge=20101201,152110,0,0,123456789,1&TerminalID=AxDoorMainEntrance&mac=00:04:24:00:00:00:11:22"

def requested_uri():
    # @app.route('/', defaults={'path': ''})
    # @app.route('/<path:path>')
    # req_uri = path
    req_uri = request.url
    # req_uri = terminalRequest
    print(req_uri)
    start_badge = (req_uri.find("?"))
    end_badge = (req_uri.find("&"))
    terminal_id = end_badge
    raw_string = req_uri[start_badge:end_badge]
    raw_left_date = raw_string.find(",")
    raw_left_time = raw_string.find(",", raw_left_date + 1)
    raw_left_0 = raw_string.find(",", raw_left_time + 1)
    raw_left_card = raw_string.find(",", raw_left_0 + 1)
    raw_right_card = raw_string.find(",", raw_left_card + 1)
    final = raw_string[(raw_left_card + 1):raw_right_card]
    print("Badge: ", final)
    return final

def connection_init():
    global conn
    conn = sqlite3.connect('axess-ws.db')

def connection_closed():
    conn.close()
    print(" <-- Desligado da BD")


def successful_transaction():
    global somCrlf, releCrlf, sucesso
    print(somCrlf + releCrlf)
    print(sucesso)
    datetime = (strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    print(datetime)
    print("")
    connection_closed()
    return somCrlf + releCrlf


def denied_transaction():
    global soundDeny
    print(sucesso, "Acesso Negado")
    datetime = (strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    print(datetime)
    requested_uri()
    connection_closed()
    return soundDeny


class CheckUserAPB(Resource):
    def get(self):
        global sucesso, conn
        card_uid = requested_uri()
        connection_init()
        cursor = conn.execute("select count(idCard) from cards where apbStatus = 0 and cardUid = " + card_uid)
        print(" --> Ligado à BD")
        print("")
        result = cursor.fetchone()
        if result[0] is 1:
            successful_transaction()
            return successful_transaction()
        else:
            denied_transaction()
            return denied_transaction()


class CheckManual(Resource):
    def get(self):
        manual_card_uid = str(input("Passe o cartão no leitor:"))
        print("Introduziu :" + manual_card_uid)
        CheckUserAPB()


# api.add_resource(CheckUserAPB, request.args)  # Validar Cartão
# api.add_resource(CheckManual, '/manual')  # Validar Manual

@app.route('/validar/')
def validar():
    pedido = request.args.get('badge')
    return pedido

if __name__ == '__main__':
    app.run(port='5002')
