import os
import json

from flask import render_template, url_for, flash, get_flashed_messages, redirect, request

from webapp.app import app, db
from webapp.models import Bingo
from bingoai.inference import InferencePipeline, ALL_LABELS


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

@app.route('/', methods=['POST', 'GET'])
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
            pipeline = InferencePipeline()
            input = {
                'image': image_path,
                'labels': ALL_LABELS
            }
            output = pipeline.process_input(input=input)
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