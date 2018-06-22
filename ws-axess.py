# ! / usr / bin / python
# coding=utf-8
"""
  Ax Webservice - ver. 0.80
  Developed by Gustavo Pinto - Módulos Flask, Flask Restful, sqlite3 e datetime
"""

import sqlite3
from flask import Flask, request
from flask_restful import Api

app = Flask(__name__)
api = Api(app)

# Parameters
som, rele, sound_deny, sound_accept, porta = "beep=1", "relay=1,50", "beep=2", "beep=1", "5002"
card = ''
term_id = ''
resultado = 0
conn = sqlite3.connect('axess-ws.db')


def resultado_terminal():
    if resultado == 1:
        return sound_accept + "\r\n" + rele + "\r\n"
    else:
        return sound_deny + "\r\n"


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    global id_transaction
    global direction
    global term_id
    global card
    global transaction_stamp
    global date_transaction
    global time_transaction
    global resultado
    global conn
    pedido = path
    if 'online' in pedido:
        mensagem=request.args
        print()
        print("NOME DO TERMINAL: ", mensagem['id'])
        print("MAC ADDRESS: ", mensagem['mac'])
        transaction_stamp = mensagem['trsn']
        transaction_split = transaction_stamp.split(",")
        card = transaction_split[4]
        print()
        print("CARTÃO UID:\r\n", card)
        date_transaction = transaction_split[0]
        print("DATA DO MOVIMENTO:\r\n", date_transaction[-2:] + "-" + date_transaction[4:6] + "-" + date_transaction[:4])
        time_transaction = transaction_split[1]
        print("HORA DO MOVIMENTO:\r\n", time_transaction[:2] + ":" + time_transaction[2:4] + ":" + time_transaction[-2:])
        print()
        cursor = conn.execute('SELECT count(*) FROM cards WHERE freeAcess = 1 and cardUid = "' + str(card) + '"')
        cursor_credit = conn.execute('SELECT credit FROM cards WHERE cardUid ="' + str(card) + '"')
        rows = cursor.fetchall()
        rows_credit = cursor_credit.fetchall()
        contador = rows[0]
        saldo = rows_credit[0]
        saldo_final = saldo[0]-1
        print("Contador:", contador[0])
        print("Saldo Inicial:", saldo[0])
        print("VÁLIDOS EM BD: ", contador[0])
        print()
        if contador[0] == 1:
            resultado = 1 # ACEITAR MOVIMENTO
            print("FREE ACESS")
            return resultado_terminal()
        elif saldo[0] >= 1:
            resultado = 1  # ACEITAR MOVIMENTO E DEBITAR SALDO
            cursor = conn.execute('UPDATE cards SET credit = ' + str(saldo_final) + ' WHERE cardUid = "' + str(card) + '"')
            print("DEBITAR SALDO:", saldo_final)
            print()
            conn.commit()
            return resultado_terminal()
        else:
            resultado = 0 # REJEITAR MOVIMENTO!
            print("REJEITAR ENTRADA")
            print()
            return resultado_terminal()
    elif 'batch' in pedido:
        return "ack=1" + "\r\n"
    elif 'keepalive' in pedido:
        return "ack=1" + "\r\n"
    else:
        texto_final = "Tipo de pedido não suportado! Verifique a documentação!" + "\r\n" + "Grupo Copigés - suporte@copiges.pt" + "\r\n"
        return texto_final
    conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=porta)