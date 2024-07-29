import time
from openai import OpenAI
import streamlit as st
from datetime import datetime
import base64
from PIL import Image
from io import BytesIO
import database as db
from main import hash_password
import os
import gpt

def greet_based_on_time():
    now = datetime.now()
    current_hour = now.hour

    if 5 <= current_hour < 12:
        return "Good Morning,"
    elif 12 <= current_hour < 18:
        return "Good Afternoon,"
    else:
        return "Good Evening,"

def add_wishlist(brand, model, year, target_price):
    prompt = f'{year} {brand} {model}'
    #st.write(prompt)
    market = gpt.search_for_prices(client, prompt)
    #st.write(market)
    wish_car = {"brand": brand, "model": model, "year": year, "price": target_price, "market": market, "last_updated": datetime.now()}
    db.add_new_car_to_wishlist(wish_car)
    return

def delete_car_from_wishlist(brand, model, year, target_price, market, last_updated):
    db.remove_car_from_wishlist(brand, model, year, target_price, market, last_updated)
    return

def add_garage(brand, model, year, plate):
    garage_car = {"brand": brand, "model": model, "year": year, "plate": plate}
    db.add_new_car_to_garage(garage_car)
    return

def delete_car_from_garage(brand, model, year, plate):
    db.remove_car_from_garage(brand, model, year, plate)
    return

image_path = 'logo.png'
image = Image.open(image_path)
buffered = BytesIO()
image.save(buffered, format="PNG")
img_base64 = base64.b64encode(buffered.getvalue()).decode()
html_code = f"""
    <div style="display: flex; justify-content: flex-end;">
        <img src="data:image/png;base64,{img_base64}" width="50" style="display: block; margin: 0 auto;" />
    </div>
"""
st.markdown(html_code, unsafe_allow_html=True)
client = OpenAI(api_key=os.environ['OPEN_NANNY'])
greeting = greet_based_on_time()
st.title(greeting + " " + st.session_state.log_in_user)

#add_wishlist("BMW", "323i", 2011, 130000)

tab1, tab2, tab3, tab4 = st.tabs(["My Garage", "Wishlist", "KarAi", "Profile"])

# with tab0:
#     st.image("https://static.streamlit.io/examples/cat.jpg", width=200)


with tab1:
    st.subheader("Add A Car")
    brand = st.text_input("Manufacturer")
    model = st.text_input("Vehicle Model")
    plate = st.text_input("Number Plate")
    year = st.slider(
        "Year of Manufacture",
        min_value=1980,
        max_value=datetime.now().year,
        value=2022, step=1)

    add_car_garage_button = st.button("Add To Garage")

    if add_car_garage_button:
        add_garage(brand, model, year, plate)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Your Garage")
    garage = db.get_car_garage()

    for car in garage:
        # bubble_html = f"""
        #                   <div style="border-radius: 10px; background-color: black; padding: 10px; margin: 5px;">
        #                       <strong style="font-size: 18px;">{car['brand']} {car['model']}</strong><br>
        #                       Year: {car['year']}<br>
        #                       Number Plate: {car['plate']}<br>
        #                   </div>
        #                   """
        # st.markdown(bubble_html, unsafe_allow_html=True)
        col1, col2 = st.columns([4, 1])
        with col1:
            bubble_html = f"""
                        <div style="border-radius: 10px; background-color: black; padding: 10px; margin: 5px;">
                            <strong style="font-size: 18px;">{car['brand']} {car['model']}</strong><br>
                            Year: {car['year']}<br>
                            Number Plate: {car['plate']}<br>
                        </div>
                    """
            st.markdown(bubble_html, unsafe_allow_html=True)
        with col2:
            #st.markdown("<br>", unsafe_allow_html=True)
            delete_button = st.button(f"X", key=car['plate'])
            if delete_button:
                delete_car_from_garage(car['brand'],car['model'],car['year'],car['plate'])
                with col1:
                    st.success(f"{car['plate']} has been deleted")
                    time.sleep(2)
                st.experimental_rerun()

with tab2:
    #st.image("https://static.streamlit.io/examples/dog.jpg", width=200)

    st.subheader("Add A Car")
    brand = st.text_input("Make")
    model = st.text_input("Car Model")
    year = st.slider(
       "Manufactured Year",
       min_value=1980,
       max_value=datetime.now().year,
       value= 2022, step = 1)
    price = st.slider(
       "Target Price",
       min_value=100,
       max_value=2000000,
       value= 100000, step = 2000)

    add_car_wishlist_button = st.button("Add To Wishlist")

    if add_car_wishlist_button:
       add_wishlist(brand,model,year,price)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Your wishlist")
    db.check_car_prices_wishlist()
    wishlist = db.get_car_wishlist()
    #st.write(wishlist)
    if len(wishlist) > 0:
        st.markdown("<p style='font-size:12px; color:grey;'>The market price shown is an approximate estimate generated by AI and is subject to variation.</p>", unsafe_allow_html=True)
    for car in wishlist:
        col1, col2 = st.columns([4, 1])
        with col1:
            price = int(car['price'])
            t = f"{price:,}"

            try:
                market_price = int(car['market'])
                m = f"{market_price:,}"
                if market_price < price:
                    color = "green"
                else:
                    color = "white"
            except ValueError:
                m = "N/A"
                color = "red"

            bubble_html = f"""
                        <div style="border-radius: 10px; background-color: black; padding: 10px; margin: 5px; position: relative; color: white;">
                           <div style="display: inline-block;">
                               <strong style="font-size: 18px;">{car['brand']} {car['model']}</strong><br>
                               Year: {car['year']}<br>
                               Target Price: RM {t}<br>
                           </div>
                           <div style="position: absolute; right: 10px; top: 10px; text-align: right;">
                               <span style="font-size: 10px;">Market Price:</span><br>
                               <strong span style="font-size: 35px; color: {color};">{m}</strong></span>
                           </div>
                       </div>
                          """
            st.markdown(bubble_html, unsafe_allow_html=True)
        with col2:
            # st.markdown("<br>", unsafe_allow_html=True)
            delete_button = st.button(f"X", key=f"{car['brand']} {car['model']} {car['year']} {car['price']} {car['last_updated']}")
            if delete_button:
                delete_car_from_wishlist(car['brand'], car['model'], car['year'], car['price'], car['market'], car['last_updated'])
                with col1:
                    st.success(f"Successfully deleted")
                    time.sleep(2)
                st.experimental_rerun()


with tab3:
    st.subheader("KarAi finds the best car for you using AI!")
    brand = st.text_input("Brand")
    model = st.text_input("Model")
    year = st.slider(
       "Year Make",
       min_value=1980,
       max_value=datetime.now().year,
       value=(datetime.now().year - 7, datetime.now().year - 3))
    price = st.slider(
       "Price",
       min_value=100,
       max_value=2000000,
       value=(50000, 150000))
    body = st.text_input("Body Type (Sedan, SUV, Truck, Coupe, etc.)")
    fuel = st.selectbox('Fuel Type', ["Gasoline", "Diesel", "Hybrid", "Electric", "Hydrogen Fuel Cell"])
    transmission = st.selectbox('Transmission', ["Automatic", "Manual"])
    others = st.text_input("Specify other requirements here")

    submit_search = st.button("Search")

    # Display the results when the search button is pressed
    if submit_search:
        prompt = f'brand: {brand}\n' \
                 f'model: {model}\n' \
                 f'year make: {year[0]}-{year[1]}\n' \
                 f'budget: {price[0]}-{price[1]}\n' \
                 f'body type: {body}\n' \
                 f'fuel type: {fuel}\n' \
                 f'transmission type: {transmission}\n' \
                 f'extras: {others}'
        print(prompt)
        results = gpt.search_for_cars(client,prompt)

        st.subheader("Search Results:")
        if len(results) > 0:
            st.markdown("<p style='font-size:12px; color:grey;'>The market price shown is an approximate estimate generated by AI and is subject to variation.</p>",unsafe_allow_html=True)
            for car in results:
               price = int(car[3])
               m = f"{price:,}"

               link = car[4]
               link_html = ' '.join(
                   [f'<a href="https://{l}" style="color: white;" target="_blank">{l}</a>' for l in link])
               # Using HTML and CSS to create a "bubble" appearance
               bubble_html = f"""
                    <div style="border-radius: 10px; background-color: black; padding: 20px; margin: 5px; position: relative; color: white;">
                       <div style="display: inline-block;">
                           <strong style="font-size: 18px;">{car[2]} {car[0]} {car[1]}</strong><br>
                           Link: {link_html}<br>
                       </div>
                       <div style="position: absolute; right: 15px; top: 10px; text-align: right;">
                           <span style="font-size: 10px;">Average Market Price:</span><br>
                           <strong span style="font-size: 35px; position: relative; top: -10px;">{m}</strong></span>
                       </div>
                   </div>
                """
               st.markdown(bubble_html, unsafe_allow_html=True)
        else:
            st.write("No cars found matching your criteria.")


with tab4:
    st.header("Profile")
    st.markdown(f"""Username: {st.session_state.log_in_user}""")
    st.markdown(f"""Cars In Garage: {db.count_cars_garage()}""")
    st.markdown(f"""Cars In Wishlist: {db.count_cars_wishlist()}""")
    st.markdown("<br>", unsafe_allow_html=True)


    st.subheader("Change Password")

    # Initialize a session state variable to control the visibility of the password fields
    if 'change_password_active' not in st.session_state:
        st.session_state['change_password_active'] = True

    if st.session_state['change_password_active']:
        old_pw = st.text_input("Old Password", type="password", key="old_pw")
        new_pw = st.text_input("New Password", type="password", key="new_pw")
        new_pw_retype = st.text_input("Retype New Password", type="password", key="new_pw_retype")

        change_pw_button = st.button("Change Password")

        if change_pw_button:
            if new_pw != new_pw_retype:
                st.error("Retyped Password Does Not Match")
            else:
                if db.login(st.session_state.log_in_user, old_pw):
                    db.change_password(st.session_state.log_in_user, hash_password(new_pw_retype))
                    st.success("Password Changed Successfully!")
                    time.sleep(2)
                    # Set the session state to False to hide the inputs after a successful change
                    st.session_state['change_password_active'] = False
                    st.rerun()
                else:
                    st.error("Old Password Is Incorrect")
    else:
        st.write("Reset the form to update password again.")
        if st.button("Reset Password Form"):
            st.session_state['change_password_active'] = True

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Account Management")
    logout_button = st.button("Logout")
    if logout_button:
        st.session_state.clear()  # Optionally clear all session state on logout
        st.switch_page("main.py")