import pickledb
import os

db_path = 'global.db'

def get_db():
    db = pickledb.PickleDB(db_path)
    db.load()
    return db

def get_user(user):
    db = get_db()
    return db.get(user)

def get_all_users():
    # TODO: include age in each row, and never include the password hash
    db = get_db()
    rows = []
    for x in db.all():
        rows.append((x, db.get(x)["gender"], db.get(x)["rating"]))
    return rows

def add_user(user, password, gender, rating, age):
    # TODO: hash the password before storing it, and save the hash in the user record
    db = get_db()
    if db.get(user) is not None:
        return False
    db.set(user, {"gender" : gender, "rating" : rating, "age" : age}) #can add more for each user
    db.save()
    return True

def user_exists(user):
    # TODO: return True if the username is already in the database, else False
    pass

def verify_user(user, password):
    # TODO: look up the user, compare the given password against the stored hash,
    #       return True on match and False if the user is missing or the password is wrong
    pass

def update_password(user, new_password):
    # TODO: hash new_password and overwrite the stored hash; return False if user is missing
    pass

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
    #       ignore unknown keys, save, and return False if the user is missing
    pass

def get_users_by_rating(min_rating, max_rating):
    # TODO: return a list of (username, record) for every user whose rating is
    #       between min_rating and max_rating inclusive
    pass

def find_matches(user, rating_range):
    # TODO: get the user's rating, then return other users whose rating is within
    #       +/- rating_range of it; exclude the user themself; return [] if user is missing
    pass

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
    # TODO: return every match record where user_a or user_b equals `user`,
    #       newest first
    pass
