import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as plolygo
from datetime import date

st.set_page_config(page_title="Eventful Travel App", layout="wide", page_icon="✈️")

CITY_DATA = {
    "Barcelona, Spain": {"vibes": {"Beach": 3, "Nightlife": 3, "Culture": 2, "Foodie": 2, "Adventure": 1, "Relaxation": 1, "Romantic": 2, "Hidden Gems": 0}, "interests": {"Music Festivals": 3, "Art Galleries": 2, "Sports": 1, "Hiking": 1, "Foodie Tours": 2}, "distance_zone": 1, "base_flight": 80, "description": "Sun, Gaudí, and the best nightlife in Southern Europe.", "emoji": "💃", "lat": 41.3851, "lon": 2.1734},
    "Paris, France": {"vibes": {"Romantic": 3, "Culture": 3, "Foodie": 3, "Hidden Gems": 1, "Relaxation": 1, "Nightlife": 1, "Beach": 0, "Adventure": 0}, "interests": {"Art Galleries": 3, "Music Festivals": 1, "Sports": 1, "Hiking": 0, "Foodie Tours": 3}, "distance_zone": 1, "base_flight": 100, "description": "Romance, world-class cuisine, and iconic art museums.", "emoji": "🗼", "lat": 48.8566, "lon": 2.3522},
    "Amsterdam, Netherlands": {"vibes": {"Nightlife": 3, "Culture": 2, "Hidden Gems": 2, "Romantic": 2, "Foodie": 1, "Relaxation": 1, "Beach": 0, "Adventure": 1}, "interests": {"Music Festivals": 3, "Art Galleries": 2, "Sports": 1, "Hiking": 0, "Foodie Tours": 1}, "distance_zone": 1, "base_flight": 90, "description": "World-class DJs, canals, and a vibrant cultural scene.", "emoji": "🎧", "lat": 52.3676, "lon": 4.9041},
    "Naples, Italy": {"vibes": {"Foodie": 3, "Culture": 2, "Hidden Gems": 2, "Beach": 2, "Romantic": 1, "Relaxation": 2, "Nightlife": 1, "Adventure": 0}, "interests": {"Foodie Tours": 3, "Art Galleries": 2, "Music Festivals": 1, "Sports": 1, "Hiking": 1}, "distance_zone": 1, "base_flight": 90, "description": "The birthplace of pizza with authentic markets and history.", "emoji": "🍕", "lat": 40.8518, "lon": 14.2681},
    "Ljubljana, Slovenia": {"vibes": {"Relaxation": 3, "Hidden Gems": 3, "Culture": 2, "Romantic": 2, "Adventure": 1, "Foodie": 1, "Nightlife": 0, "Beach": 0}, "interests": {"Hiking": 2, "Art Galleries": 1, "Foodie Tours": 2, "Music Festivals": 0, "Sports": 1}, "distance_zone": 1, "base_flight": 85, "description": "Europe's hidden gem — peaceful, green, and charming.", "emoji": "🍃", "lat": 46.0569, "lon": 14.5058},
    "Ghent, Belgium": {"vibes": {"Culture": 3, "Hidden Gems": 3, "Foodie": 2, "Romantic": 2, "Relaxation": 2, "Nightlife": 1, "Beach": 0, "Adventure": 0}, "interests": {"Art Galleries": 3, "Foodie Tours": 2, "Music Festivals": 2, "Sports": 0, "Hiking": 0}, "distance_zone": 1, "base_flight": 95, "description": "Medieval architecture, craft beer, and a thriving art scene.", "emoji": "🏰", "lat": 51.0543, "lon": 3.7174},
    "Mallorca, Spain": {"vibes": {"Beach": 3, "Relaxation": 3, "Romantic": 2, "Foodie": 1, "Nightlife": 2, "Adventure": 1, "Culture": 1, "Hidden Gems": 1}, "interests": {"Hiking": 2, "Foodie Tours": 1, "Music Festivals": 1, "Art Galleries": 0, "Sports": 2}, "distance_zone": 1, "base_flight": 100, "description": "Crystal clear water, hidden coves, and coastal bliss.", "emoji": "🏖️", "lat": 39.6953, "lon": 3.0176},
    "Chamonix, France": {"vibes": {"Adventure": 3, "Relaxation": 1, "Hidden Gems": 2, "Romantic": 2, "Culture": 1, "Nightlife": 0, "Beach": 0, "Foodie": 1}, "interests": {"Hiking": 3, "Sports": 3, "Art Galleries": 0, "Foodie Tours": 0, "Music Festivals": 0}, "distance_zone": 1, "base_flight": 110, "description": "Alpine adventure capital — hiking, skiing, and mountain air.", "emoji": "⛰️", "lat": 45.9237, "lon": 6.8694},
    "Lisbon, Portugal": {"vibes": {"Culture": 3, "Foodie": 2, "Romantic": 2, "Hidden Gems": 2, "Relaxation": 2, "Nightlife": 2, "Beach": 1, "Adventure": 0}, "interests": {"Art Galleries": 2, "Foodie Tours": 3, "Music Festivals": 2, "Hiking": 1, "Sports": 1}, "distance_zone": 1, "base_flight": 95, "description": "Fado music, pastel de nata, and stunning hilltop views.", "emoji": "🎵", "lat": 38.7223, "lon": -9.1393},
    "Reykjavik, Iceland": {"vibes": {"Adventure": 3, "Hidden Gems": 3, "Relaxation": 2, "Romantic": 2, "Culture": 1, "Nightlife": 1, "Beach": 0, "Foodie": 0}, "interests": {"Hiking": 3, "Art Galleries": 1, "Music Festivals": 1, "Sports": 2, "Foodie Tours": 0}, "distance_zone": 2, "base_flight": 180, "description": "Northern lights, geysers, and raw volcanic landscapes.", "emoji": "🌌", "lat": 64.1466, "lon": -21.9426},
    "Dubrovnik, Croatia": {"vibes": {"Beach": 3, "Romantic": 3, "Culture": 2, "Hidden Gems": 2, "Relaxation": 2, "Nightlife": 1, "Adventure": 1, "Foodie": 1}, "interests": {"Art Galleries": 1, "Hiking": 2, "Foodie Tours": 2, "Music Festivals": 1, "Sports": 1}, "distance_zone": 1, "base_flight": 120, "description": "Stunning city walls and crystal Adriatic sea.", "emoji": "🏰", "lat": 42.6507, "lon": 18.0944},
    "Prague, Czech Republic": {"vibes": {"Culture": 3, "Hidden Gems": 2, "Nightlife": 3, "Romantic": 2, "Foodie": 1, "Relaxation": 1, "Beach": 0, "Adventure": 0}, "interests": {"Art Galleries": 2, "Music Festivals": 2, "Foodie Tours": 1, "Sports": 0, "Hiking": 0}, "distance_zone": 1, "base_flight": 85, "description": "Fairytale architecture, cheap beer, and buzzing nightlife.", "emoji": "🍺", "lat": 50.0755, "lon": 14.4378},
    "Seville, Spain": {"vibes": {"Culture": 3, "Foodie": 3, "Romantic": 3, "Nightlife": 2, "Hidden Gems": 1, "Relaxation": 1, "Beach": 0, "Adventure": 0}, "interests": {"Art Galleries": 2, "Foodie Tours": 3, "Music Festivals": 2, "Sports": 1, "Hiking": 0}, "distance_zone": 1, "base_flight": 90, "description": "Flamenco, tapas, and Moorish palaces under the Andalusian sun.", "emoji": "💃", "lat": 37.3891, "lon": -5.9845},
    "Vienna, Austria": {"vibes": {"Culture": 3, "Romantic": 3, "Relaxation": 2, "Foodie": 2, "Hidden Gems": 1, "Nightlife": 1, "Beach": 0, "Adventure": 0}, "interests": {"Art Galleries": 3, "Music Festivals": 3, "Foodie Tours": 2, "Sports": 0, "Hiking": 0}, "distance_zone": 1, "base_flight": 105, "description": "Classical music, imperial palaces, and Viennese coffee culture.", "emoji": "🎻", "lat": 48.2082, "lon": 16.3738},
    "Algarve, Portugal": {"vibes": {"Beach": 3, "Relaxation": 3, "Romantic": 2, "Adventure": 1, "Foodie": 1, "Hidden Gems": 1, "Nightlife": 1, "Culture": 0}, "interests": {"Hiking": 2, "Sports": 2, "Foodie Tours": 1, "Art Galleries": 0, "Music Festivals": 0}, "distance_zone": 1, "base_flight": 100, "description": "Dramatic cliffs, golden beaches, and fresh seafood.", "emoji": "🌊", "lat": 37.0179, "lon": -7.9304},
}

def score_cities(vibes, interests, activity_level):
    mult = {"Very Low": 0.5, "Moderate": 1.0, "Intense": 1.5}[activity_level]
    results = []
    for city, data in CITY_DATA.items():
        vibe_score = sum(data["vibes"].get(v, 0) for v in vibes)
        if "Adventure" in vibes:
            vibe_score += data["vibes"].get("Adventure", 0) * (mult - 1)
        if "Relaxation" in vibes:
            vibe_score += data["vibes"].get("Relaxation", 0) * (0.5 - mult if mult < 1 else 0)
        interest_score = sum(data["interests"].get(i, 0) for i in interests)
        total = vibe_score + interest_score
        max_possible = len(vibes) * 3 + len(interests) * 3 if (vibes or interests) else 1
        match_pct = min(round((total / max_possible) * 100), 99) if max_possible > 0 else 0
        results.append({"city": city, "vibe_score": round(vibe_score, 1), "interest_score": round(interest_score, 1), "total_score": round(total, 1), "match_pct": match_pct, "description": data["description"], "emoji": data["emoji"]})
    return pd.DataFrame(results).sort_values("total_score", ascending=False).reset_index(drop=True)

def estimate_cost(city_name, budget, travel_dates, activity_level):
    data = CITY_DATA.get(city_name, {})
    base_flight = data.get("base_flight", 120)
    zone = data.get("distance_zone", 1)
    num_days = 3
    if travel_dates and len(travel_dates) == 2:
        num_days = max((travel_dates[1] - travel_dates[0]).days, 1)
    season_mult = 1.0
    if travel_dates and len(travel_dates) >= 1:
        month = travel_dates[0].month
        if month in [6, 7, 8, 12]: season_mult = 1.35
        elif month in [4, 5, 9, 10]: season_mult = 1.1
    daily_spend = {"Very Low": 40, "Moderate": 70, "Intense": 110}
    est_activities = daily_spend[activity_level] * num_days
    est_flight = round(base_flight * zone * season_mult)
    total = est_flight + est_activities
    affordable = total <= budget
    season_label = "Peak 🔴" if season_mult == 1.35 else ("Shoulder 🟡" if season_mult == 1.1 else "Off-peak 🟢")
    return est_flight, est_activities, total, affordable, season_label, num_days

def fetch_weather(city_name):
    data = CITY_DATA.get(city_name, {})
    lat, lon = data.get("lat"), data.get("lon")
    if not lat or not lon: return None
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weathercode,windspeed_10m,relative_humidity_2m&timezone=auto"
        result = requests.get(url, timeout=5).json()
        current = result.get("current", {})
        code = current.get("weathercode", 0)
        descriptions = {0: ("☀️", "Clear sky"), 1: ("🌤️", "Mainly clear"), 2: ("⛅", "Partly cloudy"), 3: ("☁️", "Overcast"), 45: ("🌫️", "Foggy"), 51: ("🌦️", "Light drizzle"), 61: ("🌧️", "Light rain"), 63: ("🌧️", "Moderate rain"), 71: ("🌨️", "Light snow"), 80: ("🌦️", "Showers"), 95: ("⛈️", "Thunderstorm")}
        emoji, desc = descriptions.get(code, ("🌡️", "Variable"))
        return {"temp": round(current.get("temperature_2m", 0)), "description": desc, "emoji": emoji, "wind": round(current.get("windspeed_10m", 0)), "humidity": current.get("relative_humidity_2m", 0)}
    except:
        return None

def fetch_real_events(city_name):
    clean_city = city_name.split(',')[0].strip()
    try:
        api_key = st.secrets["TICKETMASTER_API_KEY"]
    except:
        api_key = "9Rri7l1kutIcmyOqcbKstEN88GkcPGy7"
    try:
        data = requests.get(f"https://app.ticketmaster.com/discovery/v2/events.json?city={clean_city}&apikey={api_key}&size=4", timeout=5).json()
        return data['_embedded']['events'][:4] if "_embedded" in data else []
    except:
        return []

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Inter:wght@400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.block-container { padding-top: 1rem !important; }
.hero { background: linear-gradient(135deg, #FF4B4B 0%, #FF8C42 50%, #FFD166 100%); border-radius: 20px; padding: 52px 44px; margin-bottom: 32px; position: relative; overflow: hidden; }
.hero::before { content: "✈️"; font-size: 180px; position: absolute; right: -10px; top: -20px; opacity: 0.12; line-height: 1; }
.hero h1 { font-family: 'Playfair Display', serif !important; font-size: 52px !important; font-weight: 900 !important; color: white !important; margin: 0 0 10px 0 !important; line-height: 1.1 !important; }
.hero p { font-size: 18px; color: rgba(255,255,255,0.92); margin: 0; font-weight: 500; }
.section-label { font-size: 11px; font-weight: 700; letter-spacing: 3px; text-transform: uppercase; color: #FF4B4B; margin-bottom: 6px; }
.section-title { font-family: 'Playfair Display', serif; font-size: 26px; font-weight: 700; color: #1a1a2e; margin-bottom: 20px; }
.rec-card { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-radius: 20px; padding: 36px 40px; margin-bottom: 28px; position: relative; overflow: hidden; }
.rec-card::after { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #FF4B4B, #FF8C42, #FFD166); }
.rec-card h2 { font-family: 'Playfair Display', serif; font-size: 38px; font-weight: 900; color: white; margin: 0 0 10px 0; }
.rec-card .tagline { font-size: 16px; color: rgba(255,255,255,0.75); margin: 0 0 16px 0; }
.match-badge { display: inline-block; background: linear-gradient(135deg, #FF4B4B, #FF8C42); color: white; font-weight: 700; font-size: 14px; padding: 6px 16px; border-radius: 30px; }
.stat-card { background: white; border-radius: 16px; padding: 20px 24px; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.07); border-top: 4px solid #FF4B4B; }
.stat-card .stat-label { font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #888; margin-bottom: 6px; }
.stat-card .stat-value { font-family: 'Playfair Display', serif; font-size: 32px; font-weight: 700; color: #1a1a2e; }
.stat-card .stat-sub { font-size: 12px; color: #aaa; margin-top: 4px; }
.weather-card { background: linear-gradient(135deg, #1976D2 0%, #42A5F5 100%); border-radius: 16px; padding: 24px; color: white; }
.weather-card .temp { font-family: 'Playfair Display', serif; font-size: 52px; font-weight: 900; line-height: 1; margin: 8px 0; }
.weather-card .w-label { font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; opacity: 0.8; }
.weather-card .w-desc { font-size: 18px; font-weight: 600; margin: 4px 0 12px; }
.weather-card .w-detail { font-size: 13px; opacity: 0.85; }
.alt-card { background: white; border-radius: 16px; padding: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.07); border-left: 5px solid #FF8C42; }
.alt-card .alt-name { font-family: 'Playfair Display', serif; font-size: 18px; font-weight: 700; color: #1a1a2e; margin-bottom: 4px; }
.alt-card .alt-pct { display: inline-block; background: #FFF3E0; color: #FF8C42; font-weight: 700; font-size: 12px; padding: 2px 10px; border-radius: 20px; margin-bottom: 8px; }
.alt-card .alt-desc { font-size: 13px; color: #666; line-height: 1.5; }
.event-card { background: white; border-radius: 16px; padding: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.07); border-top: 4px solid #FFD166; }
.event-card .event-name { font-weight: 700; font-size: 15px; color: #1a1a2e; margin-bottom: 6px; }
.event-card .event-date { font-size: 12px; color: #888; margin-bottom: 12px; }
.limit-card { background: #FFFDE7; border-radius: 16px; padding: 24px 28px; border-left: 6px solid #FFD166; margin-top: 12px; }
.limit-card h4 { font-family: 'Playfair Display', serif; font-size: 18px; color: #1a1a2e; margin-bottom: 12px; }
.limit-card li { font-size: 14px; color: #555; margin-bottom: 6px; line-height: 1.5; }
[data-testid="stSidebar"] { background: #1a1a2e !important; }
[data-testid="stSidebar"] label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] div { color: white !important; }
.stButton > button { background: linear-gradient(135deg, #FF4B4B 0%, #FF8C42 100%) !important; color: white !important; border: none !important; border-radius: 50px !important; font-size: 18px !important; font-weight: 700 !important; width: 100% !important; box-shadow: 0 8px 24px rgba(255,75,75,0.35) !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>Where to next?</h1>
    <p>Tell us your vibe — we'll find your perfect European escape, with live events and real-time weather.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 📍 Travel Details")
    travel_dates = st.date_input("When are you free?", [])
    budget = st.slider("Max Flight Budget (€)", 50, 1000, 300)
    st.markdown("---")
    st.markdown("### 🎨 Personal Interests")
    interests = st.multiselect("What do you love?", ["Music Festivals", "Art Galleries", "Sports", "Hiking", "Foodie Tours"])

st.markdown("<div class='section-label'>Step 1</div><div class='section-title'>What's the mood of this trip?</div>", unsafe_allow_html=True)
col_v, col_a = st.columns([2, 1])
with col_v:
    vibes = st.multiselect("Trip Vibe — pick everything that applies:", ["Relaxation", "Adventure", "Nightlife", "Culture", "Hidden Gems", "Romantic", "Foodie", "Beach"], default=["Culture"])
with col_a:
    activity_level = st.select_slider("Activity level:", options=["Very Low", "Moderate", "Intense"], value="Moderate")

st.markdown("<br>", unsafe_allow_html=True)
clicked = st.button("✈️  FIND MY DESTINATION")

if clicked:
    if not vibes and not interests:
        st.warning("Please select at least one vibe or interest!")
        st.stop()

    with st.spinner("Finding your perfect destination..."):
        scores_df = score_cities(vibes, interests, activity_level)
        top = scores_df.iloc[0]
        city = top["city"]
        city_info = CITY_DATA[city]
        est_flight, est_act, total_est, affordable, season_label, num_days = estimate_cost(city, budget, travel_dates, activity_level)
        weather = fetch_weather(city)
        real_events = fetch_real_events(city)

    st.balloons()
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="rec-card">
        <div style='font-size:48px;margin-bottom:12px;'>{city_info['emoji']}</div>
        <h2>{city}</h2>
        <p class="tagline">{top['description']}</p>
        <span class="match-badge">⚡ {top['match_pct']}% Match</span>
    </div>
    """, unsafe_allow_html=True)

    s1, s2, s3, s4 = st.columns(4)
    budget_diff = abs(budget - total_est)
    status_icon = "✅" if affordable else "⚠️"
    with s1:
        st.markdown(f'<div class="stat-card"><div class="stat-label">Est. Flight</div><div class="stat-value">€{est_flight}</div><div class="stat-sub">Season: {season_label}</div></div>', unsafe_allow_html=True)
    with s2:
        st.markdown(f'<div class="stat-card"><div class="stat-label">Activities</div><div class="stat-value">€{est_act}</div><div class="stat-sub">{num_days} day{"s" if num_days > 1 else ""}</div></div>', unsafe_allow_html=True)
    with s3:
        st.markdown(f'<div class="stat-card"><div class="stat-label">Total Cost</div><div class="stat-value">€{total_est}</div><div class="stat-sub">{status_icon} €{budget_diff} {"under" if affordable else "over"}</div></div>', unsafe_allow_html=True)
    with s4:
        st.markdown(f'<div class="stat-card"><div class="stat-label">Match Score</div><div class="stat-value">{top["match_pct"]}%</div><div class="stat-sub">Based on {len(vibes)} vibe(s)</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_map, col_wx = st.columns([2, 1])

    with col_map:
        st.markdown("<div class='section-label'>Location</div><div class='section-title'>Where is it?</div>", unsafe_allow_html=True)
        fig_map = plolygo.Figure(plolygo.Scattergeo(
            lat=[city_info["lat"]], lon=[city_info["lon"]],
            mode="markers+text",
            marker=dict(size=20, color="#FF4B4B", symbol="circle", line=dict(width=3, color="white")),
            text=[city], textposition="top center",
            textfont=dict(size=13, color="#1a1a2e"),
        ))
        fig_map.update_layout(
            geo=dict(scope="europe", showland=True, landcolor="#f5f5f5", showocean=True, oceancolor="#E3F2FD", showcoastlines=True, coastlinecolor="#ccc", showcountries=True, countrycolor="#ddd", center=dict(lat=city_info["lat"], lon=city_info["lon"]), projection_scale=4),
            height=320, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with col_wx:
        st.markdown("<div class='section-label'>Right now</div><div class='section-title'>Weather</div>", unsafe_allow_html=True)
        if weather:
            st.markdown(f'<div class="weather-card"><div class="w-label">Current conditions</div><div class="temp">{weather["emoji"]} {weather["temp"]}°C</div><div class="w-desc">{weather["description"]}</div><div class="w-detail">💨 {weather["wind"]} km/h wind</div><div class="w-detail">💧 {weather["humidity"]}% humidity</div></div>', unsafe_allow_html=True)
        else:
            st.info("Weather unavailable.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-label'>Model output</div><div class='section-title'>Why this destination?</div>", unsafe_allow_html=True)
    col_bar, col_rank = st.columns(2)

    with col_bar:
        fig = px.bar({"Category": ["Vibe Match", "Interest Match"], "Score": [top["vibe_score"], top["interest_score"]]}, x="Category", y="Score", color="Category", color_discrete_sequence=["#FF4B4B", "#FF8C42"], title="Score Breakdown for " + city.split(",")[0])
        fig.update_layout(showlegend=False, height=300, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter"))
        fig.update_yaxes(gridcolor="#f0f0f0")
        st.plotly_chart(fig, use_container_width=True)

    with col_rank:
        fig2 = px.bar(scores_df.head(5), x="match_pct", y="city", orientation="h", color="match_pct", color_continuous_scale=["#FFD166", "#FF8C42", "#FF4B4B"], labels={"match_pct": "Match %", "city": ""}, title="Top 5 Destinations")
        fig2.update_layout(height=300, showlegend=False, coloraxis_showscale=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter"), yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig2, use_container_width=True)

    with st.expander("📊 See full ranking of all 15 destinations"):
        fig3 = px.bar(scores_df, x="match_pct", y="city", orientation="h", color="match_pct", color_continuous_scale=["#FFD166", "#FF8C42", "#FF4B4B"], labels={"match_pct": "Match %", "city": ""}, title="All Destinations Ranked")
        fig3.update_layout(height=520, coloraxis_showscale=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-label'>Also consider</div><div class='section-title'>Other destinations you might love</div>", unsafe_allow_html=True)
    alt_cols = st.columns(3)
    for i, (_, row) in enumerate(scores_df.iloc[1:4].iterrows()):
        with alt_cols[i]:
            alt_info = CITY_DATA[row['city']]
            st.markdown(f'<div class="alt-card"><div style="font-size:28px;margin-bottom:8px;">{alt_info["emoji"]}</div><div class="alt-name">{row["city"]}</div><span class="alt-pct">⚡ {row["match_pct"]}% match</span><div class="alt-desc">{row["description"]}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<div class='section-label'>Live in {city.split(',')[0]}</div><div class='section-title'>🎭 Upcoming Events</div>", unsafe_allow_html=True)
    if real_events:
        ev_cols = st.columns(len(real_events))
        for i, event in enumerate(real_events):
            with ev_cols[i]:
                st.markdown(f'<div class="event-card"><div class="event-name">{event.get("name","Event")}</div><div class="event-date">📅 {event.get("dates",{}).get("start",{}).get("localDate","TBD")}</div></div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                st.link_button("View Tickets 🎟️", event.get("url","#"), use_container_width=True)
    else:
        st.info("No live events found for this location right now via Ticketmaster.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="limit-card">
        <h4>⚠️ Model Limitations</h4>
        <ul>
            <li><b>Fixed city list:</b> Only 15 pre-selected European destinations are considered.</li>
            <li><b>Static scores:</b> Vibe and interest scores were manually assigned and do not update based on real-world data or user feedback.</li>
            <li><b>Approximate costs:</b> Flight prices do not reflect real-time pricing, airline availability, or your departure city.</li>
            <li><b>No personalisation memory:</b> The model does not learn from previous sessions or improve over time.</li>
            <li><b>Current weather only:</b> Weather reflects today's conditions, not the forecast for your travel dates.</li>
            <li><b>Ticketmaster coverage varies:</b> Live event availability depends on the API and may not include all local events.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
