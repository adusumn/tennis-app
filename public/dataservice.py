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
    db = get_db()
    rows = []
    for x in db.all():
        rows.append((x, db.get(x)["gender"], db.get(x)["rating"]))
    return rows

def add_user(user, gender, rating, age):
    db = get_db()
    if db.get(user) is not None:
        return False
    db.set(user, {"gender" : gender, "rating" : rating, "age" : age}) #can add more for each user
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
