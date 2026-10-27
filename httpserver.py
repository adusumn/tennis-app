import flask
import json
import os
from flask import jsonify
from flask import request
from flask import session
from flask import redirect
import functools
import dataservice

from werkzeug.utils import secure_filename

# serve everything in public/ (html, styles, scripts) at the site root,
# e.g. public/signin.html -> /signin.html
app = flask.Flask(__name__, static_folder="public", static_url_path="")
app.secret_key = "s#em%p9ejwrvE6Tns6Ra"   # used a random string generator https://www.textfixer.com/tools/random-string-generator.php
    

def login_required(view):
    # TODO: wrap `view` with @functools.wraps(view); if "user" is not in session,
    #       return jsonify({"error": "not signed in"}), 401; otherwise call view(*args, **kwargs) DONE
    @functools.wraps(view)
    def wrap(*args, **kwargs):
        if "user" not in session:
            return jsonify({"error": "not signed in"}), 401
        return view(*args, **kwargs)
    return wrap

# ---------- Pages ----------

@app.route("/")
def index():
    # TODO: redirect to /homepage.html if signed in, otherwise to /signin.html
    if "user" in session:
        flask.redirect("/homepage.html")
    flask.redirect("/signin.html")

# ---------- Accounts ----------

@app.route("/signup", methods=["POST"])
def signup():
    # TODO: read username, password, confirm_password, gender, age, rating from request.form
    #       (age -> int, rating -> float); return to /signup.html if the passwords don't match
    #       or dataservice.add_user returns False (username taken); otherwise put the username
    #       in session["user"] and redirect to /homepage.html
    username = request.form["username"]
    password = request.form["password"]
    gender = request.form["gender"]
    confirm_password = request.form["confirm_password"]
    age = int(request.form["age"])
    rating = float(request.form["rating"])
    # TODO: the form's min/max is only checked by the browser, so someone can send any rating
    #       straight to /signup; redirect back to /signup.html if rating < 1.0 or rating > 7.0
    if password != confirm_password:
        return flask.redirect("/signup.html")
    if dataservice.get_user(username) is not None:
        return flask.redirect("/signin.html")
    dataservice.add_user(username, password, gender, rating, age)
    session["user"] = username
    return flask.redirect("/homepage.html")

@app.route("/signin", methods=["POST"])
def signin():
    # TODO: read username and password from request.form; if dataservice.verify_user is True,
    #       set session["user"] and redirect to /homepage.html, otherwise back to /signin.html
    username = request.form["username"]
    password = request.form["password"]
    if dataservice.verify_user(username, password):
        session["user"] = username
        return flask.redirect("/homepage.html")
    return flask.redirect("/signin.html")

@app.route("/signout", methods=["POST"])
def signout():
    # TODO: remove "user" from session and redirect to /signin.html
    session.pop("user", None)
    return flask.redirect("/signin.html")


# ---------- Profile ----------

@app.route("/api/me", methods=["GET"])
@login_required
def get_me():
    # TODO: return jsonify of dataservice.get_user(session["user"]) with the password hash
    #       removed, plus the username
    response = dataservice.get_user(session["user"])
    if response is None:
        session.pop("user", None)
        return jsonify({"ERROR": "Not Signed In"}), 401    
    profile = {
        "username" : session["user"],
        "rating" : response["rating"],
        "age" : response["age"],
        "gender" : response["gender"]
    }
    return jsonify(profile)

@app.route("/api/me", methods=["PUT"])
@login_required
def update_me():
    # TODO: pass request.get_json() to dataservice.update_user(session["user"], fields);
    #       return {"ok": True} or a 400 error
    data = request.get_json()
    age = data.get("age")
    if not isinstance(age, int) or isinstance(age, bool) or age < 5 or age > 120:
        return jsonify({"error": "invalid age"}), 400
    gender = data.get("gender")
    if gender not in {"male", "female", "other", "prefer_not"}:
        return jsonify({"error": "invalid gender"}), 400
    if dataservice.update_user(session["user"], data):
        return jsonify({"ok" : True})
    return jsonify({"error": ""}), 400

@app.route("/api/me/password", methods=["PUT"])
@login_required
def change_password():
    # TODO: read old_password and new_password from request.get_json(); check the old one
    #       with dataservice.verify_user first, then call dataservice.update_password DONE
    data = request.get_json()
    old_password = data.get("old_password", "")
    new_password = data.get("new_password", "")
    if not new_password:
        return jsonify({"error": "new password is required"}), 400
    if not dataservice.verify_user(session["user"], old_password):
        return jsonify({"error": "current password is wrong"}), 403
    dataservice.update_password(session["user"], new_password)
    return jsonify({"ok": True})

@app.route("/api/me", methods=["DELETE"])
@login_required
def delete_me():
    # TODO: call dataservice.delete_user(session["user"]), clear the session, return {"ok": True}
    #then we have to go through the request_ids in records DONE
    for request_id, record in dataservice.get_requests_for_user(session["user"]):
        if(record["status"] == "open" and record["user"] == session["user"]):
            dataservice.cancel_request(request_id, session["user"])
    dataservice.delete_user(session["user"])
    session.clear()
    return {"ok": True}

# ---------- Finding players ----------

@app.route("/api/players", methods=["GET"])
@login_required
def find_players():
    # TODO: read ?range= from request.args (default 0.5, as a float) and return jsonify of
    #       dataservice.find_matches(session["user"], rating_range)
    rating_range = request.args.get("range", 0.5, type=float)
    return jsonify(dataservice.find_matches(session["user"], rating_range))


# ---------- Matches ----------

@app.route("/api/matches", methods=["POST"])
@login_required
def record_match():
    # TODO: read winner, loser, date, score from request.get_json(); return 403 unless
    #       session["user"] is the winner or the loser; call dataservice.add_match and return
    #       the new match id, or a 400 error if it returned False
    # TODO: pass session["user"] to add_match as reported_by; the match is saved as "pending"
    #       and ratings don't change until the other player confirms it
    response = request.get_json()
    winner = response["winner"]
    loser = response["loser"]
    date = response["date"]
    score = response["score"]


@app.route("/api/matches", methods=["GET"])
@login_required
def my_matches():
    # TODO: return jsonify of dataservice.get_matches(session["user"])
    pass

@app.route("/api/matches/<int:match_id>/confirm", methods=["POST"])
@login_required
def confirm(match_id):
    # TODO: call dataservice.confirm_match(match_id, session["user"]);
    #       return {"ok": True}, or a 400 error if it returned False
    pass

@app.route("/api/matches/<int:match_id>/decline", methods=["POST"])
@login_required
def decline(match_id):
    # TODO: call dataservice.decline_match(match_id, session["user"]);
    #       return {"ok": True}, or a 400 error if it returned False
    pass


# ---------- Play requests ----------

@app.route("/api/requests", methods=["POST"])
@login_required
def new_request():
    # TODO: read date and time from request.get_json(); call
    #       dataservice.create_request(session["user"], date, time) and return the new id
    pass

@app.route("/api/requests/open", methods=["GET"])
@login_required
def open_requests():
    # TODO: return jsonify of dataservice.get_open_requests(session["user"])
    pass

@app.route("/api/requests/mine", methods=["GET"])
@login_required
def my_requests():
    # TODO: return jsonify of dataservice.get_requests_for_user(session["user"])
    pass

@app.route("/api/requests/<int:request_id>", methods=["GET"])
@login_required
def one_request(request_id):
    # TODO: return jsonify of dataservice.get_request(request_id), or 404 if it's None
    pass

@app.route("/api/requests/<int:request_id>/accept", methods=["POST"])
@login_required
def accept(request_id):
    # TODO: call dataservice.accept_request(request_id, session["user"]);
    #       return {"ok": True} or a 400 error if it returned False
    pass

@app.route("/api/requests/<int:request_id>/cancel", methods=["POST"])
@login_required
def cancel(request_id):
    # TODO: call dataservice.cancel_request(request_id, session["user"]);
    #       return {"ok": True} or a 403 error if it returned False
    pass


if __name__ == "__main__":
    app.run(debug=True, port=5000)
