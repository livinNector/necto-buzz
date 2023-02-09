import flask
from flask import Flask
from flask import render_template
from flask import jsonify
from flask import request
from time import sleep
import json
import os

import threading
from random_gens import random_expression_generator
from message_publisher import MessageService
from utils import format_sse
from team import Team

app = Flask(__name__)

config = {"DEBUG": True}  # run app in debug mode

# Flask to use the above defined config
app.config.from_mapping(config)
app.question_service = MessageService(3)
app.winner_service = MessageService(30)
app.teams = {}
app.winners = set()


@app.route("/")
def home():
    return render_template("home.html.jinja2", title="Home")


@app.route("/static/")
def favicon():
    return flask.send_from_directory("./static/")


@app.route("/about")
def about():
    return render_template("about.html.jinja2", title="About")


@app.route("/admin")
def admin():
    admin_key  = os.environ["ADMIN_KEY"]
    if request.args.get("key") == admin_key:
        return render_template("admin.html.jinja2",title ="Admin",key=admin_key)
    return flask.redirect("/")


@app.route("/login", methods=["POST"])
def login():
    team_name = request.form["teamName"]
    if team_name not in app.teams:
        team_id = team_name.lower().replace(" ", "_")
        app.teams[team_id] = Team(team_id, team_name)

    return flask.redirect(f"/team?id={team_id}")


@app.route("/logout", methods=["POST"])
def logout():
    team_id = request.form["teamId"]
    del app.teams[team_id]
    return flask.redirect("/")


@app.route("/team")
def team():
    team_id = request.args.get("id")
    try:
        team = app.teams[team_id]
    except:
        return flask.redirect("/")
    return render_template(
        "team.html.jinja2",
        title=team.name,
        team_name=team.name,
        team_id=team.id,
    )


@app.route("/teams")
def teams():
    return list(map(lambda x: x.__dict__, app.teams.values()))

@app.route("/remove_teams")
def remove_teams():
    teams = request.args.getlist("teams[]")
    for team in teams:
        try: 
            del app.teams[team]
        except KeyError:
            pass
    return flask.Response(status=204)

@app.route("/add_score")
def team_score():
    team_id = request.args.get("teamId")
    score = request.args.get("score")
    key = request.args.get("key")
    if key == os.environ["ADMIN_KEY"]:
        try:
            app.teams[team_id].score += int(score)
        except:
            pass
        return "success"
    return "falied"


@app.route("/threads")
def threads():
    return list(map(str, threading.enumerate()))


@app.route("/publish_question", methods=["POST"])
def publish_question():
    app.winners = set()
    if request.args.get("reset"):
        question = ""
        app.answer = ""
    else:
        question = random_expression_generator(5)
        app.answer = str(eval(question))
    app.question_service.publish(format_sse(question, "question"))
    return flask.Response(status=204)


@app.route("/question", methods=["GET"])
def question():
    if request.method == "GET":
        subscription = app.question_service.get_subscription()
        return flask.Response(
            subscription.listen(), mimetype="text/event-stream",status=200
        )


@app.route("/answer",methods=["POST"])
def answer():
    data = request.json
    team_id = data["teamId"]
    answer= data["answer"]
    if team_id not in app.winners and answer == app.answer:
        app.winners.add(team_id)
        app.winner_service.publish(
            format_sse(json.dumps(app.teams[team_id].__dict__), "winner")
        )
    return flask.Response(status=204)


@app.route("/admin_winner")
def admin_winner():
    subscription = app.winner_service.get_subscription()
    return flask.Response(
        subscription.listen(), mimetype="text/event-stream",status=200
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", threaded=True)
