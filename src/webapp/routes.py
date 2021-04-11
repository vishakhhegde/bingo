import os
import json

from flask import render_template, url_for, flash, get_flashed_messages, redirect, request

from webapp.app import app, db
from webapp.models import Bingo

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')
