from app import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    marks = db.Column(db.Integer, index=True)

    def __repr__(self):
        return "<User {}>".format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Questions(db.Model):
    q_id = db.Column(db.Integer, primary_key=True)
    ques = db.Column(db.String(350), unique=True)
    a = db.Column(db.String(100))
    b = db.Column(db.String(100))
    c = db.Column(db.String(100))
    d = db.Column(db.String(100))
    ans = db.Column(db.String(100))
    score = db.Column(db.REAL)

    def __repr__(self):
        return "<Question: {}>".format(self.ques)


class Answers(db.Model):
    a_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    question_id = db.Column(db.Integer)
    is_correct = db.Column(db.Integer)
    start_at = db.Column(db.Integer)
    end_at = db.Column(db.Integer)


class Normalizations(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    current_question = db.Column(db.Integer)
    normalization = db.Column(db.REAL)
    previous_normalization = db.Column(db.REAL)
    has_updated = db.Column(db.Integer)
