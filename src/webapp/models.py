from datetime import datetime

from webapp.app import db

class Bingo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(200), nullable=False)
    image_path = db.Column(db.String(300), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Image %r>' % self.id