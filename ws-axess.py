#!/usr/bin/python
#coding=utf-8
"""
  Ax Webservice - ver. 1.05
  Developed by Gustavo Pinto - Módulos Flask, Flask Restful, e sqlite3
"""

import sqlite3
from flask import Flask, request
from flask_restful import Api

app = Flask(__name__)
api = Api(app)

# Parameters

som, rele, sound_deny, sound_accept, porta = "beep=1", "relay=1,50", "beep=2", "beep=1", "5002"


def resultado_terminal():  #ORDEM PARA O TERMINAL
    if resultado == 1:
        return sound_accept + "\r\n" + rele + "\r\n"
    else:
        return sound_deny + "\r\n"


def print_message():  #MENSAGENS DE DEBUG
    print()
    print("NOME DO TERMINAL: ", mensagem['id'])
    print("MAC ADDRESS: ", mensagem['mac'])
    print()
    print("CARTÃO UID:\r\n", card)
    print("DATA DO MOVIMENTO:\r\n", date_transaction[-2:] + "-"
          + date_transaction[4:6] + "-" + date_transaction[:4])
    print("HORA DO MOVIMENTO:\r\n", time_transaction[:2] + ":"
          + time_transaction[2:4] + ":" + time_transaction[-2:])
    print()
    print("TAG LIVRE ACESSO VÁLIDA:", contador)
    print("SALDO INICIAL:", saldo)
    print()


def reset_variables():  #LIMPAR TRANSACÇÃO
    global card, resultado, saldo, contador, rows, rows_credit
    card = 0
    resultado = 0
    saldo = 0
    contador = 0
    rows = 0
    rows_credit = 0


def reject_entry():  # REJEITAR MOVIMENTO!
    global resultado
    resultado = 0
    print("REJEITAR ENTRADA")
    print()
    conn.close()
    return resultado_terminal()


def debit_account():  # ACEITAR MOVIMENTO E DEBITAR SALDO
    global resultado
    resultado = 1
    conn.execute('UPDATE cards SET credit = ' + str(saldo_final)
                 + ' WHERE cardUid = "' + str(card) + '"')
    print("DEBITAR SALDO:", saldo_final)
    print()
    conn.commit()
    conn.close()
    return resultado_terminal()


def free_access():  # ACEITAR MOVIMENTO
    global resultado
    resultado = 1
    print("FREE ACESS")
    print()
    conn.close()
    return resultado_terminal()


def online_request():  #TRATAR UM PEDIDO ONLINE DE UM TERMINAL
    global term_id, card, resultado, conn, mensagem, transaction_split, \
        transaction_stamp, date_transaction, time_transaction, rows, rows_credit, \
        contador, resultado, saldo, saldo_final
    mensagem = request.args
    transaction_stamp = mensagem['trsn']
    transaction_split = transaction_stamp.split(",")
    card = transaction_split[4]
    date_transaction = transaction_split[0]
    time_transaction = transaction_split[1]
    cursor = conn.execute('SELECT count(*) FROM cards WHERE freeAcess = 1 and cardUid = "'
                          + str(card) + '"')
    cursor_credit = conn.execute('SELECT credit FROM cards WHERE cardUid = "' + str(card) + '"')
    rows = cursor.fetchall()
    rows_credit = cursor_credit.fetchall()
    print('SELECT credit FROM cards WHERE cardUid = "' + str(card) + '"')
    if len(rows_credit) < 1:
        print("Uknown Card: Correcting Balance")
        rows_credit = [(0,), ]
    contador = rows[0]
    contador = contador[0]
    saldo = rows_credit[0]
    saldo = saldo[0]
    saldo_final = saldo - 1
    print_message()


def process_request():  #ANALISAR E DEVOLVER O PEDIDO AO TERMINAL DE ACORDO
    global term_id, card, resultado, conn, mensagem, transaction_split, transaction_stamp, \
        date_transaction, time_transaction, rows, rows_credit, contador, resultado, saldo, \
        saldo_final, pedido

    if 'online' in pedido:  # AXESS ONLINE REQUEST
        online_request()
        if contador > 0:
            return free_access()
        elif saldo >= 1:
            return debit_account()
        else:
            return reject_entry()
    elif 'batch' in pedido:
        return "ack=1" + "\r\n"
    elif 'keepalive' in pedido:
        return "ack=1" + "\r\n"
    else:
        texto_final = "Pedido não suportado! Verifique a documentação!" \
                      + "\r\n" + "Grupo Copigés - suporte@copiges.pt" + "\r\n"
        conn.close()
        return texto_final


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST'])


def catch_all(path):
    global term_id, card, resultado, conn, mensagem, transaction_split, \
        transaction_stamp, date_transaction, time_transaction, rows, rows_credit, \
        contador, resultado, saldo, saldo_final, pedido

    conn = sqlite3.connect('axess-ws.db')
    pedido = path

    reset_variables()

    return process_request()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=porta)

