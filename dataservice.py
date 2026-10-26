import pickledb
import os
import bcrypt
from datetime import datetime

db_path = 'global.db'
EDITABLE_FIELDS = {"gender", "age", "rating"}
SCALE = 0.5
def get_db():
    db = pickledb.PickleDB(db_path)
    db.load()
    return db


def get_user(user):
    db = get_db()
    return db.get(user)

def get_all_users():
    # TODO: include age in each row, and never include the password hash DONE
    db = get_db()
    rows = []
    for x in db.all():
        if ":" in x or x == "next_id":
            continue
        rows.append((x, db.get(x)["age"], db.get(x)["gender"], db.get(x)["rating"]))
    return rows

def add_user(user, password, gender, rating, age):
    # TODO: hash the password before storing it, and save the hash in the user record DONE
    db = get_db()
    if (":" in user or user == "next_id"):
        return False
    if db.get(user) is not None:
        return False
    #need to hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
    db.set(user, {"password" : hashed, "gender" : gender, "rating" : rating, "age" : age}) #can add more for each user
    db.save()
    return True

def user_exists(user):
    db = get_db()
    if(db.get(user) is not None):
        return True
    else:
        return False

def verify_user(user, password):
    # TODO: look up the user, compare the given password against the stored hash,
    #       return True on match and False if the user is missing or the password is wrong DONE
    db = get_db()
    if db.get(user) is None:
        return False
    elif(bcrypt.checkpw(password.encode("utf-8"), db.get(user)["password"].encode("utf-8"))): # checks if the password given matches the username that has been inputed in the function
        return True
    else:
        return False

def update_password(user, new_password):
    # TODO: hash new_password and overwrite the stored hash; return False if user is missing DONE
    db = get_db()
    if(db.get(user) is None):
        return False
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(new_password.encode("utf-8"), salt).decode("utf-8")
    db.get(user)["password"] = hashed
    db.set(user, db.get(user))
    db.save()
    return True

def delete_user(user):
    db = get_db()
    if db.get(user) is None:
        return False
    db.remove(user)
    db.save()
    return True

def update_rating(user, rating):
    db = get_db()
    if(db.get(user) is None):
        return False
    change = db.get(user)
    change["rating"] = rating
    db.set(user, change)
    db.save()
    return True

def update_user(user, fields):
    # TODO: merge the keys in `fields` (gender, age, rating, ...) into the user's record,
    #       ignore unknown keys, save, and return False if the user is missing DONE
    db = get_db()
    if(db.get(user) is None):
        return False
    record = db.get(user)
    for key,value in fields.items():
        if key in EDITABLE_FIELDS:
            record[key] = value
    db.set(user, record)
    db.save()
    return True

def get_users_by_rating(min_rating, max_rating):
    # TODO: return a list of (username, record) for every user whose rating is
    #       between min_rating and max_rating inclusive DONE
    db = get_db()
    rows = []
    for x in db.all():
        if ":" in x or x == "next_id":
            continue
        user = db.get(x)
        if (min_rating <= user["rating"] <= max_rating):
            rows.append((x, {"gender" : user["gender"], "rating" : user["rating"], "age" : user["age"]}))
    return rows

def find_matches(user, rating_range):
    # TODO: get the user's rating, then return other users whose rating is within
    #       +/- rating_range of it; exclude the user themself; return [] if user is missing
    db = get_db()
    if db.get(user) is None:
        return []
    rating = db.get(user)["rating"]
    rows = get_users_by_rating(rating - rating_range, rating + rating_range)
    result = []
    for row in rows:
        if row[0] != user:
            result.append(row)
    return result

def add_match(winner, loser, date, score):
    # TODO: store a match record under a separate key space (e.g. "match:<id>") so it
    #       does not collide with user records, then call adjust_ratings(winner, loser, score)
    #       so both players' ratings move; return the new match id
    db = get_db()
    if db.get(winner) is None or db.get(loser) is None or winner == loser:
        return False
    match_id = db.get("match:next_id")
    if match_id is None:
        match_id = 1
    db.set("match:next_id", match_id + 1)
    db.set(f"match:{match_id}", {"winner" : winner, "loser" : loser, "date" : date, "score" : score})
    db.save()
    adjust_ratings(winner, loser, score)
    return match_id

def expected_score(rating_a, rating_b):
    # TODO: return the probability (0.0 to 1.0) that a player rated rating_a beats a
    #       player rated rating_b. Elo formula: 1 / (1 + 10 ** ((rating_b - rating_a) / SCALE))
    #       where SCALE is how big a gap counts as "much better" on the 1.0-7.0 NTRP scale
    #       (try 0.5 to start: one NTRP level apart means the better player wins ~91%)
    diff = rating_b - rating_a
    elo = 1/(1+10 ** ((diff)/SCALE))
    return elo


def parse_score(score):
    # TODO: score is winner-first, one set per space, e.g. "7-5" or "6-4 3-6 7-6(5)".
    #       drop any tiebreak points in parentheses, add up the games on each side,
    #       and return (winner_games, loser_games) DONE
    winner_games = 0
    loser_games = 0
    for set_score in score.split():
        set_score = set_score.split("(")[0]
        w, l = set_score.split("-")
        winner_games += int(w)
        loser_games += int(l)
    return winner_games, loser_games

def margin_multiplier(score):
    # TODO: get (winner_games, loser_games) from parse_score, compute
    #       margin = (winner_games - loser_games) / (winner_games + loser_games),
    #       clamp margin to at least 0, and return 0.5 + margin
    #       (0.5 for a very close match up to 1.5 for a 6-0 6-0 blowout) DONE
    winner_games, loser_games = parse_score(score)
    margin = (winner_games - loser_games) / (winner_games + loser_games)
    if margin < 0:
        margin = 0
    return 0.5 + margin

def adjust_ratings(winner, loser, score, k=0.1):
    # TODO: load both ratings, compute expected = expected_score(winner_rating, loser_rating),
    #       then:
    #         change = k * margin_multiplier(score) * (1 - expected)
    #         winner_rating += change   # beating a stronger player gains more
    #         loser_rating  -= change   # losing to a weaker player loses more
    #       a close score shrinks the change and a blowout grows it;
    #       clamp both to the 1.0-7.0 range, save with update_rating, and return the
    #       pair of new ratings; return False if either user is missing
    db = get_db()
    win = db.get(winner)
    lose = db.get(loser)
    if win is None or lose is None or winner == loser:
        return False
    expected = expected_score(win["rating"], lose["rating"])
    change = k * margin_multiplier(score) * (1-expected)
    new_win = win["rating"] + change
    new_lose = lose["rating"] - change
    if new_win > 7.0:
        new_win = 7.0
    if new_lose < 1.0:
        new_lose = 1.0
    update_rating(winner, new_win)
    update_rating(loser, new_lose)
    return new_win , new_win

def get_matches(user):
    db = get_db()
    rows = []
    for key in db.all():
        if not key.startswith("match:") or key == "match:next_id":
            continue
        record = db.get(key)
        if record["winner"] == user or record["loser"] == user:
            match_id = int(key[len("match:"):]) # 6:....starts at the id number
            rows.append((match_id, record))
    rows.sort(key=match_sort_key, reverse=True)
    return rows

def match_sort_key(row):
    match_id = row[0]
    record = row[1]
    return (record["date"], match_id)

# ---------- Play requests ----------
# A request is stored under its own key space, "request:<id>", so it never collides
# with a username. Record shape:
#   {"poster": username, "date": "YYYY-MM-DD", "time": "HH:MM",
#    "status": "open" | "accepted" | "cancelled", "accepted_by": username or None}
# Ignoring a request needs no storage; the user just does nothing and it stays open.

def next_request_id():
    # TODO: read the counter stored under "request:next_id" (treat missing as 1),
    #       save counter + 1 back, and return the id that was read
    # TODO: use the `db` passed in instead of calling get_db() here, so the counter and
    #       the new request are saved together by the caller's db.save()
    #       (a second copy of the db would overwrite the new counter when it saves)
    # TODO: don't call db.save() here; create_request saves once at the end
    db = get_db()
    counter = db.get("request:next_id")
    if counter is None:
        counter = 1
    db.set("request:next_id", counter + 1)
    db.save()
    return counter

def create_request(user, date, time):
    # TODO: return False if the user is missing; otherwise get an id from
    #       next_request_id(), store an "open" request record with poster=user,
    #       accepted_by=None, save, and return the new id
    # TODO: call get_db() once, check db.get(user) is not None
    # TODO: get the id with next_request_id(db), passing the same db
    # TODO: db.set(f"request:{request_id}", {...}) using the record shape at the top
    #       of this section, with status="open" and accepted_by=None
    # TODO: db.save() once, then return request_id
    if get_user(user) is None:
        return False
    request = next_request_id()
    db = get_db()
    db.set(f"request:{request}", {"user" : user, "date" : date, "time" : time, "status" : "open", "accepted_by" : None})
    db.save()
    return request

def get_request(request_id):
    # TODO: return the request record for "request:<request_id>", or None if missing
    # TODO: build the key with f"request:{request_id}" and return db.get(key)
    #       (db.get already returns None when the key is missing)
    db = get_db()
    record = db.get(f"request:{request_id}")
    if record is None:
        return None
    return record

def get_open_requests(user):
    # TODO: loop over every key that starts with "request:" (skip "request:next_id"),
    #       keep records whose status is "open" and whose poster is not exclude_user,
    #       and return a list of (request_id, record) sorted by date then time
    # TODO: turn the key into the id with int(key[len("request:"):])
    # TODO: skip requests that are already in the past: get now = datetime.now()
    #       (add "from datetime import datetime" at the top of the file), build
    #       today = now.strftime("%Y-%m-%d") and current_time = now.strftime("%H:%M"),
    #       and skip the record if (record["date"], record["time"]) < (today, current_time)
    #       (only filter them out here; leave them stored so they still show in history)
    # TODO: sort with key=lambda row: (row[1]["date"], row[1]["time"]) so the soonest
    #       request is first (dates "YYYY-MM-DD" and times "HH:MM" sort correctly as text)
    db = get_db()
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M")
    records = []
    for x in db.all():
        if not x.startswith("request:") or x == "request:next_id":
            continue
        record = db.get(x)
        if (record["date"], record["time"]) < (today, current_time):
            continue
        if record["status"] == "open" and record["user"] != user:
            records.append((int(x[len("request:"):]), record))
    records.sort(key=request_sort_key)
    return records

def request_sort_key(row):
    # sort by date first, then by time for requests on the same day
    record = row[1]
    return (record["date"], record["time"])

def accept_request(request_id, accepter):
    # TODO: return False if the request is missing, not "open", or the accepter is
    #       the poster or a missing user; otherwise set status="accepted",
    #       accepted_by=accepter, save, and return True
    # TODO: call get_db() once and load the record with db.get(f"request:{request_id}")
    # TODO: check each failure case in order:
    #         record is None
    #         record["status"] != "open"   (already accepted or cancelled)
    #         db.get(accepter) is None
    #         accepter == record["poster"] (can't accept your own request)
    # TODO: change the record, db.set it back under the same key, db.save(), return True
    db = get_db()
    record = db.get(f"request:{request_id}")
    if record is None or record["status"] != "open" or accepter == record["user"] or db.get(accepter) is None:
        return False
    record["status"] = "accepted"
    record["accepted_by"] = accepter
    db.set(f"request:{request_id}", record)
    db.save()
    return True

def cancel_request(request_id, user):
    # TODO: return False if the request is missing or `user` is not the poster;
    #       otherwise set status="cancelled", save, and return True
    # TODO: load the record with db.get(f"request:{request_id}")
    # TODO: return False if record is None or record["poster"] != user
    # TODO: set record["status"] = "cancelled", db.set it back, db.save(), return True
    #       (keep the record instead of db.remove so it still shows up in history)
    pass

def get_requests_for_user(user):
    # TODO: return a list of (request_id, record) where the user is the poster or
    #       accepted_by, skipping cancelled ones, sorted by date then time
    # TODO: same loop as get_open_requests: keys starting with "request:",
    #       skip "request:next_id", get the id with int(key[len("request:"):])
    # TODO: keep the record if record["poster"] == user or record["accepted_by"] == user,
    #       and record["status"] != "cancelled"
    # TODO: sort with key=lambda row: (row[1]["date"], row[1]["time"])
    pass
