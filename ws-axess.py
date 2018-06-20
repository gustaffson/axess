'''
  Ax Webservice - ver. 0.4
  Developed by Gustavo Pinto - Módulos Flask, Flask Restful, sqlite3 e datetime
  !/usr/bin/python
  -*- coding: utf8 -*-
'''

import sqlite3
import re
from flask import Flask, request
from flask_restful import Api
from datetime import datetime

app = Flask(__name__)
api = Api(app)

# Parameters
som, rele, sound_deny, sound_accept, porta = "beep=1", "relay=1,50", "beep=2", "beep=1", "5002"
conn = sqlite3.connect('axess-ws.db')
card = '?'
term_id = '?'
resultado = 0

def check_mov():
    global id_transaction
    global direction
    global term_id
    global card
    card, direction, term_id = process_request()[0], process_request()[1], process_request()[2]
    select_id = conn.execute("select max(idTransaction) from transactions")
    id_transaction = select_id.fetchone()

def store_mov():
    global id_transaction
    global direction
    global term_id
    global card
    card, direction, term_id = process_request()[0], process_request()[1], process_request()[2]
    select_id = conn.execute("select max(idTransaction) from transactions")
    id_transaction = select_id.fetchone()
    if id_transaction[0] is None:
        conn.execute("insert into transactions values (?, ?, ?, ?, ?)",
                     (1, "0000000000000000", datetime.now(), "INIT BD", "99"))
        conn.commit()
        select_id = conn.execute("select max(idTransaction) from transactions")
        id_transaction = select_id.fetchone()
        conn.execute("insert into transactions values (?, ?, ?, ?, ?)",
                     ((int(id_transaction[0]) + 1), card, datetime.now(), term_id, direction))
        conn.commit()
        conn.close()

def process_request():
    global id_transaction
    global direction
    global term_id
    global card
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


def resultado_terminal():
    if (resultado == 0):
        return sound_deny + "\r\n"
    elif (resultado == 1):
        return sound_accept + "\r\n" + rele + "\r\n"


val_entrada = conn.execute("select count(idCard) from cards where apbStatus = 0 and cardUid = " + '"' + card + '"')
val_saida = conn.execute("select count(idCard) from cards where apbStatus = 1 and cardUid = " + '"' + card + '"')
val_livre = conn.execute("select count(idCard) from cards where freeAcess = 1")

if val_entrada == 0 and direction == 1 and val_livre is not 1:  # VALIDAÇÃO DE ENTRADA SEM ACESSO LIVRE
    conn.execute("update cards set apbStatus = 1 where cardUid = " + '"' + card + '"')
    select_id = conn.execute("select max(idTransaction) from transactions")
    id_transaction = select_id.fetchone()
    conn.execute("insert into transactions values (?, ?, ?, ?, ?)",
                 ((int(id_transaction[0]) + 1), card, datetime.now(), term_id, direction))
    conn.commit()
    resultado = 1
    resultado_terminal()
elif val_saida == 1:  # VALIDAÇAO DE SAÍDA
    conn.execute('update cards set apbStatus = 0 where cardUid = ' + '"' + card + '"')
    select_id = conn.execute("select max(idTransaction) from transactions")
    id_transaction = select_id.fetchone()
    conn.execute("insert into transactions values (?, ?, ?, ?, ?)",
                 ((int(id_transaction[0]) + 1), card, datetime.now(), term_id, direction))
    conn.commit()
    resultado = 1
    resultado_terminal()
else:  # ACESSO RECUSADO COM LOG
    select_id = conn.execute("select max(idTransaction) from transactions")
    id_transaction = select_id.fetchone()
    conn.execute('insert into transactions values (?, ?, ?, ?, ?)',
                 ((int(id_transaction[0]) + 1), card, datetime.now(), term_id, 3))
    conn.commit()
    resultado = 0
    resultado_terminal()

@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    global id_transaction
    global direction
    global term_id
    global card
    pedido = path
    regexp = re.compile(r'ba[rzd]')
    if regexp.search(online):
        process_request()
        ticket = check_mov()
        return ticket
    if pedido == "batch":
        process_request()
        store_mov()
        return "ack=1" + "\r\n"
    elif pedido == "keepalive":
        return "ack=1" + "\r\n"
    else:
        texto_final = "Tipo de pedido não suportado! Verifique a documentação!" + "\r\n" + "Grupo Copigés - suporte@copiges.pt" + "\r\n"
        return texto_final

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=porta)
