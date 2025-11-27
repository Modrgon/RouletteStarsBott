# database.py — التعامل مع MongoDB

from pymongo import MongoClient
from bson import ObjectId
from config import MONGO_URI, DB_NAME
from datetime import datetime, timedelta

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# ======================================================
# USERS COLLECTION
# ======================================================
users = db["users"]

def get_user(user_id):
    user = users.find_one({"user_id": user_id})
    if not user:
        user = {
            "user_id": user_id,
            "stars": 0,
            "wallet": None,
            "boost_active": False,
            "boost_end": None,
            "hot_active": False,
            "hot_end": None,
        }
        users.insert_one(user)
    return users.find_one({"user_id": user_id})

def update_stars(user_id, amount):
    users.update_one({"user_id": user_id}, {"$inc": {"stars": amount}})
    return users.find_one({"user_id": user_id})

def set_wallet(user_id, wallet):
    users.update_one({"user_id": user_id}, {"$set": {"wallet": wallet}})

# ======================================================
# BOOSTERS COLLECTION
# ======================================================
boosters = db["boosters"]

def create_booster(name, level=1, price=0, duration_hours=24):
    booster = {
        "name": name,
        "level": level,
        "price": price,
        "duration_hours": duration_hours
    }
    result = boosters.insert_one(booster)
    return str(result.inserted_id)

def get_boosters():
    return list(boosters.find())

def get_booster(booster_id):
    try:
        return boosters.find_one({"_id": ObjectId(booster_id)})
    except Exception:
        return None

# ======================================================
# GIFT BOXES COLLECTION
# ======================================================
gift_boxes = db["gift_boxes"]

def create_gift_box(owner_id, title, pack_value, price, max_winners, cond_channels):
    box = {
        "owner_id": owner_id,
        "title": title,
        "pack_value": pack_value,
        "price": price,
        "max_winners": max_winners,
        "cond_channels": cond_channels,
        "participants": [],
        "active": True,
        "claimed": False,
        "winners": []
    }
    res = gift_boxes.insert_one(box)
    return str(res.inserted_id)

def get_gift_box(box_id):
    try:
        return gift_boxes.find_one({"_id": ObjectId(box_id)})
    except Exception:
        return None

def update_gift_box(box_id, data: dict):
    try:
        gift_boxes.update_one({"_id": ObjectId(box_id)}, {"$set": data})
    except Exception:
        return

def add_participant_to_box(box_id, user_id):
    try:
        gift_boxes.update_one({"_id": ObjectId(box_id)}, {"$addToSet": {"participants": user_id}})
    except Exception:
        return

def set_box_winners_and_close(box_id, winners: list):
    try:
        gift_boxes.update_one({"_id": ObjectId(box_id)}, {"$set": {"winners": winners, "active": False}})
    except Exception:
        return

def mark_box_claimed(box_id):
    try:
        gift_boxes.update_one({"_id": ObjectId(box_id)}, {"$set": {"claimed": True}})
    except Exception:
        return

# ======================================================
# BOOSTER ACTIVATION
# ======================================================
def activate_booster(user_id, duration_hours=24):
    end_time = datetime.utcnow() + timedelta(hours=duration_hours)
    users.update_one(
        {"user_id": user_id},
        {"$set": {"boost_active": True, "boost_end": end_time}}
    )

def deactivate_booster(user_id):
    users.update_one(
        {"user_id": user_id},
        {"$set": {"boost_active": False, "boost_end": None}}
    )

def is_booster_active(user_id):
    user = get_user(user_id)
    if user and user.get("boost_active") and user.get("boost_end"):
        if datetime.utcnow() > user["boost_end"]:
            deactivate_booster(user_id)
            return False
        return True
    return False

# ======================================================
# ROULETTES COLLECTION
# ======================================================
roulettes = db["roulettes"]

def create_roulette(owner_id, title, price, max_winners, cond_channels):
    roulette = {
        "owner_id": owner_id,
        "title": title,
        "price": price,
        "max_winners": max_winners,
        "participants": [],
        "cond_channels": cond_channels,
        "active": True
    }
    result = roulettes.insert_one(roulette)
    return str(result.inserted_id)

def get_roulette(rid):
    try:
        return roulettes.find_one({"_id": ObjectId(rid)})
    except Exception:
        return None

def update_roulette(rid, new_data: dict):
    try:
        roulettes.update_one({"_id": ObjectId(rid)}, {"$set": new_data})
    except Exception:
        return

def join_roulette(rid, user_id):
    try:
        roulettes.update_one({"_id": ObjectId(rid)}, {"$addToSet": {"participants": user_id}})
    except Exception:
        return

def close_roulette(rid):
    try:
        roulettes.update_one({"_id": ObjectId(rid)}, {"$set": {"active": False}})
    except Exception:
        return

def add_condition_channel(rid, channel):
    try:
        roulettes.update_one({"_id": ObjectId(rid)}, {"$addToSet": {"cond_channels": channel}})
    except Exception:
        return

def remove_condition_channel(rid, channel):
    try:
        roulettes.update_one({"_id": ObjectId(rid)}, {"$pull": {"cond_channels": channel}})
    except Exception:
        return