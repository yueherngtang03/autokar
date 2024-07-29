import pymongo
import streamlit as st
from datetime import datetime
from openai import OpenAI
import os
import gpt
import bcrypt

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password)

uri = os.environ['AUTOKAR_MONGO']
client = OpenAI(api_key=os.environ['OPEN_NANNY'])
client = pymongo.MongoClient(uri)
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client['autokar']
collection = db['user']

collection.create_index("username", unique=True)


def add_user(username, password):
    """
    Adds a new user to the database with a hashed password and a wishlist.

    Parameters:
        username (str): The username of the user.
        password (str): The user's password (will be hashed before storage).

    Returns:
        str: Success or error message.
    """

    if collection.find_one({"username": username}):
        return False

    # Prepare the user document
    user_data = {
        "username": username,
        "password": password,
        "wishlist": [],
        "car": []
    }

    collection.insert_one(user_data)
    return True

def get_user(username):
    user = collection.find_one({"username": username})
    return user

def login(username, password):
    user = collection.find_one({"username": username})
    if user:
        if check_password(password,user['password']):
            return True
    return False

def add_new_car_to_wishlist(new_car):
    collection.update_one(
        {"username": st.session_state.log_in_user},
        {"$push": {"wishlist": new_car}}
    )
    return

def check_car_prices_wishlist():
    wishlist = get_car_wishlist()
    for car in wishlist:
        if (datetime.now() - car["last_updated"]).days > 90:
            prompt = f'{car["year"]} {car["brand"]} {car["model"]}'
            market = gpt.search_for_prices(client, prompt)
            collection.update_one(
                {
                    "username": st.session_state.log_in_user,
                    "wishlist.year": car["year"],
                    "wishlist.brand": car["brand"],
                    "wishlist.model": car["model"]
                },
                {
                    "$set": {"wishlist.$.market": market,
                             "wishlist.$.last_updated": datetime.now(),
                             }
                }
            )

    return


def get_car_wishlist():
    wishlist = collection.find_one({"username": st.session_state.log_in_user})['wishlist']
    return wishlist

def remove_car_from_wishlist(brand, model, year, target_price, market, last_updated):
    car = {"brand": brand, "model": model, "year": year, "price": target_price, "market": market, "last_updated": last_updated}
    collection.update_one(
        {"username": st.session_state.log_in_user},
        {"$pull": {"wishlist": car}}
    )
    return

def add_new_car_to_garage(new_car):
    collection.update_one(
        {"username": st.session_state.log_in_user},
        {"$push": {"car": new_car}}
    )
    return

def remove_car_from_garage(brand, model, year, plate):
    car = {"brand": brand, "model": model, "year": year, "plate": plate}
    collection.update_one(
        {"username": st.session_state.log_in_user},
        {"$pull": {"car": car}}
    )
    return

def get_car_garage():
    garage = collection.find_one({"username": st.session_state.log_in_user})['car']
    return garage

def count_cars_wishlist():
    return len(get_car_wishlist())

def count_cars_garage():
    return len(get_car_garage())

def change_password(username, password):
    result = collection.update_one(
        {"username": username},
        {"$set": {"password": password}}
    )

    if result:
        return True
    return False








