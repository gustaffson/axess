#######################################################################################################################
#  Ax Webservice - ver. 0.4
#  Developed by Gustavo Pinto - Módulos Flask, Flask Restful, sqlite3 e datetime
# !/usr/bin/python
# -*- coding: <encoding name> -*-
#######################################################################################################################

import sqlite3
from flask import Flask, request
from flask_restful import Api
from datetime import datetime

app = Flask(__name__)
api = Api(app)

# Parameters
som, rele, sound_deny, sound_accept, porta = "beep=1", "relay=1,50", "beep=2", "beep=1", "5002"


def check_mov():
    conn = sqlite3.connect('axess-ws.db')
    card, direction, term_id = process_request()[0], process_request()[1], process_request()[2]

    select_id = conn.execute("select max(idTransaction) from transactions")
    id_transaction = select_id.fetchone()
    if id_transaction[0] is None:
        conn.execute("insert into transactions values (?, ?, ?, ?, ?)",
                     (1, "0000000000000000", datetime.now(), "INIT BD", "99"))
        conn.commit()

    q_entrada = conn.execute("select count(idCard) from cards where apbStatus = 0 and cardUid = " + '"' + card + '"')
    val_entrada = q_entrada.fetchone()
    q_saida = conn.execute("select count(idCard) from cards where cardUid = " + '"' + card + '"')
    val_saida = q_saida.fetchone()
    q_livre = conn.execute("select count(idCard) from cards where freeAcess = 1 and cardUid = " + '"' + card + '"')
    val_livre = q_livre.fetchone()

    if val_entrada[0] is 1 and direction == "1" and val_livre is not 1:
        conn.execute("update cards set apbStatus = 1 where cardUid = " + '"' + card + '"')
        select_id = conn.execute("select max(idTransaction) from transactions")
        id_transaction = select_id.fetchone()
        conn.execute("insert into transactions values (?, ?, ?, ?, ?)",
                     ((int(id_transaction[0]) + 1), card, datetime.now(), term_id, direction))
        conn.commit()
        return som + "\r\n" + rele + "\r\n"
    elif val_saida[0] is 1 and direction == "0" and val_livre is not 1:
        conn.execute("update cards set apbStatus = 0 where cardUid = " + '"' + card + '"')
        select_id = conn.execute("select max(idTransaction) from transactions")
        id_transaction = select_id.fetchone()
        conn.execute("insert into transactions values (?, ?, ?, ?, ?)",
                     ((int(id_transaction[0]) + 1), card, datetime.now(), term_id, direction))
        conn.commit()
        return som + "\r\n" + rele + "\r\n"
    elif val_livre[0] is 1:
        select_id = conn.execute("select max(idTransaction) from transactions")
        id_transaction = select_id.fetchone()
        conn.execute("insert into transactions values (?, ?, ?, ?, ?)", ((int(id_transaction[0]) + 1),
                                                                         card, datetime.now(), term_id, direction))
        conn.commit()
        return som + "\r\n" + rele + "\r\n"
    else:
        select_id = conn.execute("select max(idTransaction) from transactions")
        id_transaction = select_id.fetchone()
        conn.execute("insert into transactions values (?, ?, ?, ?, ?)", ((int(id_transaction[0]) + 1), card,
                                                                         datetime.now(), term_id, 3))
        conn.commit()
        return sound_deny + "\r\n"


def process_request():
    req_uri = request.url
    start_transaction = (req_uri.find("?"))
    end_transaction = (req_uri.find("&"))
    end_term_id = (req_uri.find("&", (end_transaction + 1)))
    raw_transaction = req_uri[start_transaction:end_transaction]
    term_id = req_uri[(end_transaction + 4):end_term_id]
    raw_right_date = raw_transaction.find(",")
    raw_right_time = raw_transaction.find(",", raw_right_date + 1)
    raw_right_direction = raw_transaction.find(",", raw_right_time + 1)
    raw_left_card = raw_transaction.find(",", raw_right_direction + 1)
    direction = raw_transaction[(raw_right_time + 1):(raw_right_time + 2)]
    raw_right_card = raw_transaction.find(",", raw_left_card + 1)
    final = (raw_transaction[(raw_left_card + 1):raw_right_card], direction, term_id)
    return final


@app.route('/<path:path>')
def catch_all(path):
    pedido = path
    if pedido == "batch":
        return "ack=1" + "\r\n"
    elif pedido == "online":
        result = check_mov()
        return result
    elif path == "keepalive":
        return "ack=1" + "\r\n"
    else:
        return "Tipo de pedido não suportado! Verifique a documentação!"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=porta)
