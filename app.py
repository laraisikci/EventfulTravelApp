import streamlit as st
import pandas as pd

st.set_page_config(page_title="EventfulTravelApp", layout="wide", page_icon="✈️")

# 2. Custom CSS for a Clean Aesthetic
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
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
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Header Section with Color
st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🌍 Eventful Travel App</h1>", unsafe_allow_html=True) # FIXED HERE
st.markdown("<p style='text-align: center; font-size: 18px;'>Find your next adventure based on your unique vibe.</p>", unsafe_allow_html=True) # FIXED HERE
st.divider()


# FRONT-END: Discovery Widgets
with st.sidebar:
    st.header("📍 Travel Details")
    # Using a date range (new widget)
    travel_dates = st.date_input("When are you free?", [])
    budget = st.slider("Max Flight Budget (€)", 50, 1000, 300)
    interests = st.multiselect("Personal Interests", ["Music Festivals", "Art Galleries", "Sports", "Hiking", "Foodie Tours"])

    st.header("🎨 2. Personal Interests")
    interests = st.multiselect(
        "What do you love?", 
        ["Music Festivals", "Art Galleries", "Sports", "Hiking", "Foodie Tours"]
    )


# FRONT-END: Main Page (Vibe Selection)
st.subheader("What's the mood of this trip?")
col_v, col_a = st.columns(2)

with col_v:
    vibes = st.multiselect(
        "Trip Vibe:",
        ["Relaxation", "Adventure", "Nightlife", "Culture", "Hidden Gems", "Romantic", "Foodie", "Beach"],
        default=["Culture"]
    )
with col_a:
    activity_level = st.select_slider(
        "Desired activity level:",
        options=["Very Low", "Moderate", "Intense"]
    )



# BACKEND: Recommendation Logic (Offline Line)
def recommend_destination(vibes, activity, interests):
    # logic prioritizing 'Adventure' + 'Intense'
    if "Adventure" in vibes and activity == "Intense":
        return "Chamonix, France", "⛰️ Perfect for high-altitude hiking and the Alpine Experience."
    
    # Prioritizing specific interests if selected
    if "Music Festivals" in interests:
        return "Barcelona, Spain", "💃 Great for sightseeing Gaudi's masterpieces and sunny rooftop events."
    
    # Vibe-based logic
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
    
# INTERACTION: The "Surprise Me" Trigger
st.divider() # Adds a clean line
if st.button("✨ SURPRISE ME ✨"):
    # We call the logic function here
    city, reason = recommend_destination(vibes, activity_level, interests)
    st.balloons()

    st.markdown(f"""
        <div class="recommendation-card">
            <h2 style='color: #FF4B4B;'>Pack your bags for {city}!</h2>
            <p style='font-size: 18px;'>{reason}</p>
        </div>
    """, unsafe_allow_input=True)
    
    # Displaying the result
    st.success(f"### We recommend: **{city}**")

    
    # UI Organization: Using columns for the 'AI' Output
    c1, c2 = st.columns(2)
    with c1:
        st.info(f"**The Purpose:** {reason}")
    with c2:
        # Mocking the AI confidence/score requirement
        st.metric("Convenience Match", "94%", delta="High Compatibility")
    
    st.balloons()