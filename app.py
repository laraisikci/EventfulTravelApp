import streamlit as st
import pandas as pd
import requests

# 1. Page Config MUST be the very first Streamlit command
st.set_page_config(page_title="EventfulTravelApp", layout="wide", page_icon="✈️")

# --- BACKEND FUNCTIONS ---

def predict_travel_costs(city_name, base_budget):
    clean_city = city_name.split(',')[0].strip()
    city_price_tiers = {
        "Barcelona": 140, "Paris": 210, "Amsterdam": 190, 
        "Naples": 95, "Ljubljana": 85, "Ghent": 130, "Mallorca": 110
    }
    est_flight = city_price_tiers.get(clean_city, 150)
    est_activities = 60 
    total_est = est_flight + est_activities
    is_affordable = total_est <= base_budget
    return est_flight, est_activities, total_est, is_affordable

def recommend_destination(vibes, activity, interests):
    if "Adventure" in vibes and activity == "Intense":
        return "Chamonix, France", "⛰️ Perfect for high-altitude hiking and the Alpine Experience."
    if "Music Festivals" in interests:
        return "Barcelona, Spain", "💃 Great for sightseeing Gaudi's masterpieces and sunny rooftop events."
    if "Culture" in vibes:
        return "Ghent, Belgium", "🏰 A hidden gem with incredible culture and food."
    elif "Relaxation" in vibes:
        return "Ljubljana, Slovenia", " 🍃 Peaceful walks by the river and world-class spas."
    elif "Nightlife" in vibes: 
        return "Amsterdam, Netherlands", "🎧 Best DJs and vibrant canal-side bars."
    elif "Foodie" in vibes or "Foodie Tours" in interests:
        return "Naples, Italy", "🍕 The birthpalce of pizza with authentic food markets."
    elif "Beach" in vibes:
        return "Mallorca, Spain", "🏖️ Crystal clear water and hidden coves."
    elif "Romantic" in vibes:
        return "Paris, France", "🗼 Sunset walks by the Seine and cozy bistros."
    else:
        return "Algarve, Portugal", "Ideal for relaxation and coastal Airbnb stays."

def fetch_real_events(city_name):
    clean_city = city_name.split(',')[0].strip()
    api_key = "9Rri7l1kutIcmyOqcbKstEN88GkcPGy7" 
    url = f"https://app.ticketmaster.com/discovery/v2/events.json?city={clean_city}&apikey={api_key}"
    try:
        response = requests.get(url)
        data = response.json()
        if "_embedded" in data:
            return data['_embedded']['events'][:3]
        return []
    except:
        return []

# --- UI STYLING ---

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button {
        background-color: #FF4B4B;
        color: white;
        border-radius: 20px;
        height: 3em;
        width: 100%;
        font-weight: bold;
    }
    .recommendation-card {
        padding: 20px;
        border-radius: 15px;
        background-color: #ffffff;
        border-left: 10px solid #FF4B4B;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🌍 Eventful Travel App</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px;'>Find your next adventure based on your unique vibe.</p>", unsafe_allow_html=True)
st.divider()

# --- SIDEBAR ---

with st.sidebar:
    st.header("📍 Travel Details")
    travel_dates = st.date_input("When are you free?", [])
    budget = st.slider("Max Flight Budget (€)", 50, 1000, 300)

    st.header("🎨 2. Personal Interests")
    interests = st.multiselect(
        "What do you love?", 
        ["Music Festivals", "Art Galleries", "Sports", "Hiking", "Foodie Tours"]
    )

# --- MAIN PAGE INPUTS ---

st.subheader("What's the mood of this trip?")
col_v, col_a = st.columns(2)

with col_v:
    vibes = st.multiselect("Trip Vibe:", ["Relaxation", "Adventure", "Nightlife", "Culture", "Hidden Gems", "Romantic", "Foodie", "Beach"], default=["Culture"])
with col_a:
    activity_level = st.select_slider("Desired activity level:", options=["Very Low", "Moderate", "Intense"])

# --- INTERACTION ---

st.divider() 

if st.button("✨ SURPRISE ME ✨"):
    # 1. Run Logic (All variables created here stay inside the button)
    city, reason = recommend_destination(vibes, activity_level, interests)
    est_flight, est_act, total_est, affordable = predict_travel_costs(city, budget)
    real_events = fetch_real_events(city)

    st.balloons()

    # 2. Display Recommendation Card
    st.markdown(f"""
    <div class="recommendation-card">
        <h2 style='color: #FF4B4B;'>Pack your bags for {city}!</h2>
        <p style='font-size: 18px;'>{reason}</p>
    </div>
    """, unsafe_allow_html=True)

    # 3. Display Budget Analysis
    st.write("### 💰 Budget Analysis (AI Estimate)")
    c1, c2, c3 = st.columns(3)
    budget_diff = budget - total_est
    status = "Under Budget" if affordable else "Over Budget"
    
    c1.metric("Estimated Flight", f"€{est_flight}")
    c2.metric("Airbnb & Events", f"€{est_act}")
    c3.metric("Total Est. Cost", f"€{total_est}", delta=f"€{budget_diff} {status}")

    if not affordable:
        st.warning("⚠️ This trip slightly exceeds your set budget. Consider shifting dates!")

    st.divider()

    # 4. Display Live Events
    if real_events:
        st.subheader(f"🎭 Live Events in {city.split(',')[0]}")
        cols = st.columns(len(real_events))
        for i, event in enumerate(real_events):
            with cols[i]:
                event_name = event.get('name', 'Event')
                event_date = event.get('dates', {}).get('start', {}).get('localDate', 'TBD')
                event_url = event.get('url', '#')
                st.info(f"**{event_name}**")
                st.caption(f"📅 Date: {event_date}")
                st.link_button("View Tickets", event_url)
    else:
        st.warning("No live events found for this location right now.")

    # 5. Display Confidence Match
    st.metric("Convenience Match", "94%", delta="High Compatibility")