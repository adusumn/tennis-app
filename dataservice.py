import pickledb
import os
import bcrypt

db_path = 'global.db'
EDITABLE_FIELDS = {"gender", "age", "rating"}
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
        rows.append((x, db.get(x)["age"], db.get(x)["gender"], db.get(x)["rating"]))
    return rows

def add_user(user, password, gender, rating, age):
    # TODO: hash the password before storing it, and save the hash in the user record DONE
    db = get_db()
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
        user = db.get(x)
        if (min_rating <= user["rating"] <= max_rating):
            rows.append((x, {"gender" : user["gender"], "rating" : user["rating"], "age" : user["age"]}))
    return rows

def find_matches(user, rating_range):
    # TODO: get the user's rating, then return other users whose rating is within
    #       +/- rating_range of it; exclude the user themself; return [] if user is missing
    

def add_match(winner, loser, date, score):
    # TODO: store a match record under a separate key space (e.g. "match:<id>") so it
    #       does not collide with user records, then call adjust_ratings(winner, loser)
    #       so both players' ratings move; return the new match id
    pass

def expected_score(rating_a, rating_b):
    # TODO: return the probability (0.0 to 1.0) that a player rated rating_a beats a
    #       player rated rating_b. Elo formula: 1 / (1 + 10 ** ((rating_b - rating_a) / SCALE))
    #       where SCALE is how big a gap counts as "much better" on the 1.0-7.0 NTRP scale
    #       (try 1.0 to start)
    pass

def adjust_ratings(winner, loser, k=0.1):
    # TODO: load both ratings, compute expected = expected_score(winner_rating, loser_rating),
    #       then:
    #         winner_rating += k * (1 - expected)   # beating a stronger player gains more
    #         loser_rating  -= k * (1 - expected)   # losing to a weaker player loses more
    #       clamp both to the 1.0-7.0 range, save with update_rating, and return the
    #       pair of new ratings; return False if either user is missing
    pass

def get_matches(user):
    # TODO: return every match record where winner or loser equals `user`,
    #       newest first
    pass

# ---------- Play requests ----------
# A request is stored under its own key space, "request:<id>", so it never collides
# with a username. Record shape:
#   {"poster": username, "date": "YYYY-MM-DD", "time": "HH:MM",
#    "status": "open" | "accepted" | "cancelled", "accepted_by": username or None}
# Ignoring a request needs no storage; the user just does nothing and it stays open.

def next_request_id():
    # TODO: read the counter stored under "request:next_id" (treat missing as 1),
    #       save counter + 1 back, and return the id that was read
    pass

def create_request(user, date, time):
    # TODO: return False if the user is missing; otherwise get an id from
    #       next_request_id(), store an "open" request record with poster=user,
    #       accepted_by=None, save, and return the new id
    pass

def get_request(request_id):
    # TODO: return the request record for "request:<request_id>", or None if missing
    pass

def get_open_requests(exclude_user):
    # TODO: loop over every key that starts with "request:" (skip "request:next_id"),
    #       keep records whose status is "open" and whose poster is not exclude_user,
    #       and return a list of (request_id, record) sorted by date then time
    pass

def accept_request(request_id, accepter):
    # TODO: return False if the request is missing, not "open", or the accepter is
    #       the poster or a missing user; otherwise set status="accepted",
    #       accepted_by=accepter, save, and return True
    pass

def cancel_request(request_id, user):
    # TODO: return False if the request is missing or `user` is not the poster;
    #       otherwise set status="cancelled", save, and return True
    pass

def get_requests_for_user(user):
    # TODO: return a list of (request_id, record) where the user is the poster or
    #       accepted_by, skipping cancelled ones, sorted by date then time
    pass
