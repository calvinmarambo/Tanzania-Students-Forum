from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for,jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd
from datetime import datetime
from cs50 import get_string
import plotly.plotly as py
import plotly.graph_objs as go

# Configure application
app = Flask(__name__)

# Ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///forum.db")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        username, password, schoolname = request.form.get("username"), \
            request.form.get("password"), request.form.get("schoolname")

        if not username:
            return apology("Missing a Username")
        if not schoolname:
            return apology("Enter your School name")
        if not password:
            return apology("Enter a Password")
        if password != request.form.get("confirmation"):
            return apology("Passwords don't Match")

        # query to see if username taken
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=username)

        # username already exists
        if len(rows) > 0:
            return apology("Username Already Taken")
        else:
            passHash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

            # create new user
            db.execute("INSERT INTO users (username,schoolname,password) VALUES (:username, :schoolname, :passHash)",\
                       username=username, schoolname=schoolname, passHash=passHash)

        # remember user and return to homepage
        session["user_id"] = db.execute(
            "SELECT * FROM users WHERE username = :username", username=username)[0]["user_id"]
        return redirect("/")

    # GET request
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    session.clear()

    if request.method == "POST":

        username, password = request.form.get("username"), request.form.get("password")

        if not username:
            return apology("must provide username", 403)
        if not password:
            return apology("must provide password", 403)

        # query for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",\
                          username=username)

        # username doesn't exist
        if len(rows) != 1:
            return apology("invalid username", 403)
        if not check_password_hash(rows[0]["password"], password):
            return apology("invalid password", 403)

        # remember user and return to homepage
        session["user_id"] = rows[0]["user_id"]
        return redirect("/")

    # GET request
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    session.clear()
    return redirect("/")


@app.route("/changepassword", methods=["GET", "POST"])
def changepassword():
    """Change password"""

    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            return apology("Enter your username")

        newpassword, confirmation = request.form.get("password"), request.form.get("confirmation")
        if not newpassword:
            return apology("Enter a Password")
        if not confirmation:
            return apology("Confirm Password")
        if newpassword != confirmation:
            return apology("Passwords don't Match")

        passHash = generate_password_hash(newpassword, method='pbkdf2:sha256', salt_length=8)

        # update new password for user
        db.execute("UPDATE users SET password=:passHash WHERE username=:username",\
                   passHash=passHash, username=username)

        return redirect("/")

    # GET request
    else:
        return render_template("changepassword.html")


@app.route("/askquestion", methods=["GET", "POST"])
def askquestion():
    """Add question"""

    if request.method == "POST":

        question, category = request.form.get("question"), request.form.get("category")

        if not question:
            return apology("Missing a question buddy!")

        # formats time of transaction
        time = "{:%Y-%m-%d %H:%M:%S}".format(datetime.now())

        # insert question, category, and time into database
        db.execute("INSERT INTO questions (user_id,question_id, question, category,time) VALUES (:u_id, :qn_id, :qn, :cat,:t)",\
                   u_id=session.get("user_id"), qn_id=session.get("question_id"), qn=question, cat=category, t=time)

        return redirect("/")

    # GET request
    else:

        # get all questions from database, ordered by time (most recent first)
        questions = db.execute("SELECT * FROM questions ORDER BY time desc limit 10")

        # redirect to ask questions page
        return render_template("ask.html", questions=questions)


@app.route("/explore")
@login_required
def explore():
    """Show all questions"""

    # get all questions asked
    questions = db.execute("SELECT * FROM questions ORDER BY time desc")

    if len(questions) == 0:
        return apology("Questions bank empty")

    for question in questions:

        # create a link to that page
        question["link"] = url_for("question") + '?question=' + \
            str(question["question_id"]) + "&usr=" + str(question["user_id"])

    return render_template("questionsbank.html", questions=questions)


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    """Search for places that match query"""

    if request.method == "POST":

        text = request.form.get("search")
        keywords, allQuestions = text.split(), []

        # here we just get all questions that contain the query of the user
        for i in range(len(keywords)):
            questions = db.execute("SELECT * FROM questions WHERE question LIKE :q OR category LIKE :q",\
                                   q='%' + keywords[i] + '%')

            for question in questions:
                question["link"] = url_for("question") + "?question=" + \
                    str(question["question_id"]) + "&usr=" + str(question["user_id"])

            if len(questions) != 0:
                allQuestions += questions

        if len(allQuestions) == 0:
            return apology("No matches found!")

        # remove duplicates
        allQuestions = [dict(t) for t in set([tuple(d.items()) for d in allQuestions])]

        # finds how many words x (string) and keywords (list) have in common
        def numSimilarities(x, keywords):
            count = 0
            words = x["question"].split()
            for word in words:
                if word in keywords:
                    count += 1
            return count

        # makes list of (questionDict, numCommonWords)
        questionsAndCount = list(map(lambda x: (x, numSimilarities(x, keywords)), allQuestions))

        # sorts the list based on the amount of words common with keywords
        questionsAndCount.sort(key=lambda x: x[1], reverse=True)

        # get back our question dictionaries, now sorted
        allQuestions = list(map(lambda x: x[0], questionsAndCount))

        return render_template("questionsbank.html", questions=allQuestions)

     # GET request
    else:
        return render_template("questionsbank.html")


@app.route("/question", methods=["GET", "POST"])
@login_required
def question():

    if request.method == "GET":
        question_id, q_user_id = int(request.args.get("question")), \
            int(request.args.get("usr"))

        # remember locally in case comment posted
        session["question_id"] = question_id
        session["q_user_id"] = q_user_id

        questionInfo = db.execute("SELECT question, time FROM questions WHERE question_id = :qn_id",\
                                  qn_id=question_id)

        question, time = questionInfo[0]["question"], questionInfo[0]["time"]

        comments = db.execute("SELECT * FROM comments WHERE question_id = :qn_id", qn_id=question_id)

        username = db.execute("SELECT username FROM users WHERE user_id=:user_id",\
                              user_id=session["user_id"])[0]["username"]

        # check to see if current user is going to question (so they can edit the page)
        canEdit = (session["user_id"] == q_user_id)

        # create link for question
        link = url_for("edit") + "?question=" + question.replace(" ", "+").replace("?", "%3F")
        return render_template("question.html", question=question, comments=comments, username=username, time=time, canEdit=canEdit, link=link)

    # POST method
    else:
        comment = request.form.get("comment")

        if not comment:
            return apology("comment empty")

        time = "{:%Y-%m-%d %H:%M:%S}".format(datetime.now())

        username = db.execute("SELECT username FROM users WHERE user_id=:user_id",\
                              user_id=session["user_id"])[0]["username"]

        # inserts comment into the database
        db.execute("INSERT INTO comments (comment, username, time, question_id) VALUES (:comment,:username,:time,:qn_id)",\
                   comment=comment, username=username, time=time, qn_id=session["question_id"])

        url = url_for("question") + "?question=" + \
            str(session["question_id"]) + "&usr=" + str(session["q_user_id"])
        return redirect(url)


@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    if request.method == "GET":
        return render_template("edit.html", question=request.args.get("question"))

    # POST method
    else:
        newQuestion, newCategory = request.form.get("edit"), request.form.get("category")
        if not newQuestion:
            return apology("Need inputs for question")
        if not newCategory:
            return apology("Need categor")
        # update question and category
        db.execute("UPDATE questions SET question=:question, category=:category WHERE question_id=:qn_id",\
                   question=newQuestion, category=newCategory, qn_id=session["question_id"])

        url = url_for("question") + "?question=" + \
            str(session["question_id"]) + "&usr=" + str(session["q_user_id"])
        return redirect(url)


@app.route("/")
@login_required
def index():
    """Show users questions"""

    # query database user's questions
    questionRows = db.execute("SELECT * FROM questions WHERE user_id = :userid ORDER BY time desc",\
                              userid=session["user_id"])

    # check if there are no questions asked
    if len(questionRows) == 0:
        return apology("You have not posted yet!")

    else:

        for question in questionRows:
            question["link"] = url_for("question") + '?question=' + \
                str(question["question_id"]) + "&usr=" + str(question["user_id"])

        # query for username and schoolname of user
        name = db.execute(
            "SELECT username, schoolname FROM users WHERE user_id=:user_id", user_id=session["user_id"])[0]

        return render_template("index.html", questionrows=questionRows, name=name)


@app.route("/analytics")
@login_required
def analytics():
    """Show users questions"""

    # number of questions asked per user, sorted by user_id (smallest to largest)
    question_count = db.execute("SELECT user_id, COUNT(*) FROM questions GROUP BY user_id")

    # get all usernames and user_ids
    users = db.execute("SELECT username, user_id FROM users")

    # sort users by their user_id (smallest to largest)
    users.sort(key=lambda x: x["user_id"])

    skipped = 0
    for i in range(len(question_count)):
        while question_count[i]["user_id"] != users[skipped + i]["user_id"]:
            skipped += 1

        # change user_id field to username
        question_count[i]["user_id"] = users[skipped + i]["username"]

    return jsonify(question_count)


@app.route("/display")
# @login_required
def display():

    return render_template("display.html")


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
