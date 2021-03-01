import os
import json

from flask import Flask, flash, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from CLIP.clip_forward import Model

UPLOAD_FOLDER = 'static/bingo_uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bingo.db'
db = SQLAlchemy(app)

ALL_LABELS = ["mens shorts",
              "womens shorts",
              "mens jacket",
              "womens jacket",
              "mens shoes",
              "womens shoes",
              "mens shirt",
              "womens shirt",
              "mens long pants",
              "womens long pants",
              "backpack",
              "sunglasses"]

class Bingo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(200), nullable=False)
    image_path = db.Column(db.String(300), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Image %r>' % self.id

@app.route('/style-detector/<image_name>')
def display_result(**kwargs):
    messages = json.loads(request.args['messages'])
    image_path = messages['image_path']
    image_name = messages['image_name']
    output = messages['output']
    return render_template('output.html',
                           image_name=image_name,
                           image_path=image_path,
                           output=output)

@app.route('/style-detector', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        image_file = request.files['image']
        image_name = image_file.filename
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_name)

        if image_name == '':
            flash('No selected file')
            return redirect(request.url)

        image_file.save(image_path)
        new_input = Bingo(image_name=image_name,
                          image_path=image_path)
        try:
            db.session.add(new_input)
            db.session.commit()
            model = Model()
            output = model.process_input(
                image=image_path,
                labels=ALL_LABELS)
            messages = {
                'image_path': image_path,
                'image_name': image_name,
                'output': output,
            }
            return redirect(url_for('.display_result',
                            image_name=image_name,
                            messages=json.dumps(messages)))

        except Exception as e:
            print(str(e))
            return "Issue uploading image"

    else:
        return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)