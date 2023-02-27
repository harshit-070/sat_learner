from app import app
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    session,
    g,
    Response,
)
from werkzeug.urls import url_parse
from app.forms import LoginForm, RegistrationForm, QuestionForm
from app.models import User, Questions, Answers, Normalizations
from app import db
from camera import Video
from identify import learning_speed
import time

number_of_questions = 2


@app.before_request
def before_request():
    g.user = None

    if "user_id" in session:
        user = User.query.filter_by(id=session["user_id"]).first()
        g.user = user


@app.route("/")
def home():
    return render_template("index.html", title="Home")


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            return redirect(url_for("login"))
        session["user_id"] = user.id
        session["marks"] = 0
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("home")
        return redirect(next_page)
        return redirect(url_for("home"))
    if g.user:
        return redirect(url_for("home"))
    return render_template("login.html", form=form, title="Login")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        session["user_id"] = user.id
        session["marks"] = 0
        return redirect(url_for("home"))
    if g.user:
        return redirect(url_for("home"))
    return render_template("register.html", title="Register", form=form)


@app.route("/question/<int:id>", methods=["GET", "POST"])
def question(id):
    form = QuestionForm()
    q = Questions.query.filter_by(q_id=id).first()

    if not q:
        return redirect(url_for("score"))
    if not g.user:
        return redirect(url_for("login"))
    answer = Answers.query.filter_by(user_id=g.user.id, question_id=id).first()
    if not answer:
        answer = Answers(
            user_id=g.user.id, question_id=id, is_correct=0, start_at=int(time.time())
        )
    answer.start_at = int(time.time())
    db.session.add(answer)
    db.session.commit()
    if request.method == "POST":
        option = request.form["options"]
        normalization = Normalizations.query.filter_by(user_id=g.user.id).first()
        if not normalization:
            normalization = Normalizations(
                user_id=g.user.id,
                current_question=id,
                normalization=0,
                previous_normalization=0,
            )
        else:
            if normalization.current_question == number_of_questions:
                normalization.normalization = 0
                normalization.previous_normalization = 0
                normalization.current_question = id
            normalization.has_updated = 0
            normalization.current_question = id

        if option == q.ans:
            if not answer:
                answer = Answers(user_id=g.user.id, question_id=id, is_correct=1)
            else:
                answer.is_correct = 1
        else:
            if not answer:
                answer = Answers(user_id=g.user.id, question_id=id, is_correct=0)
            else:
                answer.is_correct = 0
        answer.end_at = int(time.time())
        db.session.add(answer)
        db.session.add(normalization)
        db.session.commit()
        return redirect(url_for("question", id=(id + 1)))
    form.options.choices = [(q.a, q.a), (q.b, q.b), (q.c, q.c), (q.d, q.d)]
    return render_template(
        "question.html", form=form, q=q, title="Question {}".format(id)
    )


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (
            b"--frame\r\n" b"Content-Type:  image/jpeg\r\n\r\n" + frame + b"\r\n\r\n"
        )


@app.route("/video")
def video():
    return Response(
        gen(Video(g.user.id)), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/score")
def score():

    if not g.user:
        return redirect(url_for("login"))

    learner = learning_speed(g.user.id)

    return render_template("score.html", result=int(learner))


@app.route("/logout")
def logout():
    if not g.user:
        return redirect(url_for("login"))
    session.pop("user_id", None)
    session.pop("marks", None)
    return redirect(url_for("home"))


@app.route("/testing")
def test():
    if not g.user:
        return redirect(url_for("login"))

    return learning_speed(g.user.id)
