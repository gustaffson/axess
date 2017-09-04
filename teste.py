import os
import json
from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def main():
    return "on main home page"

@app.route('/longword/gameid=123&playerid=456')
def Longword():
    user = request.args.get('gameid')
    return "got hardcode %d" % gameid