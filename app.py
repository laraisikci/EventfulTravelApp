import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import cohere
import json
from datetime import date

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Europe This Week", layout="wide", page_icon="🌍")

# ── COHERE CLIENT ──────────────────────────────────────────────────────────────
try:
    COHERE_API_KEY = st.secrets["COHERE_API_KEY"]
except:
    COHERE_API_KEY = ""
co = cohere.Client(COHERE_API_KEY, timeout=120) if COHERE_API_KEY else None

# ── CITY DATABASE ──────────────────────────────────────────────────────────────
CITY_DATA = {
    "Barcelona, Spain": {
        "vibes": {"Beach": 3, "Nightlife": 3, "Culture": 2, "Foodie": 2, "Adventure": 1, "Relaxation": 1, "Romantic": 2, "Hidden Gems": 0},
        "interests": {"Music Festivals": 3, "Art Galleries": 2, "Sports": 1, "Hiking": 1, "Foodie Tours": 2},
        "distance_zone": 1, "base_flight": 80,
        "description": "Sun, Gaudí, and the best nightlife in Southern Europe.",
        "emoji": "💃", "lat": 41.3851, "lon": 2.1734,
        "energy": 3, "social": 3, "splurge": 2, "sunshine": 3, "adventure": 1,
    },
    "Paris, France": {
        "vibes": {"Romantic": 3, "Culture": 3, "Foodie": 3, "Hidden Gems": 1, "Relaxation": 1, "Nightlife": 1, "Beach": 0, "Adventure": 0},
        "interests": {"Art Galleries": 3, "Music Festivals": 1, "Sports": 1, "Hiking": 0, "Foodie Tours": 3},
        "distance_zone": 1, "base_flight": 100,
        "description": "Romance, world-class cuisine, and iconic art museums.",
        "emoji": "🗼", "lat": 48.8566, "lon": 2.3522,
        "energy": 2, "social": 2, "splurge": 3, "sunshine": 1, "adventure": 0,
    },
    "Amsterdam, Netherlands": {
        "vibes": {"Nightlife": 3, "Culture": 2, "Hidden Gems": 2, "Romantic": 2, "Foodie": 1, "Relaxation": 1, "Beach": 0, "Adventure": 1},
        "interests": {"Music Festivals": 3, "Art Galleries": 2, "Sports": 1, "Hiking": 0, "Foodie Tours": 1},
        "distance_zone": 1, "base_flight": 90,
        "description": "World-class DJs, canals, and a vibrant cultural scene.",
        "emoji": "🎧", "lat": 52.3676, "lon": 4.9041,
        "energy": 3, "social": 3, "splurge": 2, "sunshine": 1, "adventure": 1,
    },
    "Naples, Italy": {
        "vibes": {"Foodie": 3, "Culture": 2, "Hidden Gems": 2, "Beach": 2, "Romantic": 1, "Relaxation": 2, "Nightlife": 1, "Adventure": 0},
        "interests": {"Foodie Tours": 3, "Art Galleries": 2, "Music Festivals": 1, "Sports": 1, "Hiking": 1},
        "distance_zone": 1, "base_flight": 90,
        "description": "The birthplace of pizza with authentic markets and history.",
        "emoji": "🍕", "lat": 40.8518, "lon": 14.2681,
        "energy": 2, "social": 2, "splurge": 1, "sunshine": 3, "adventure": 1,
    },
    "Ljubljana, Slovenia": {
        "vibes": {"Relaxation": 3, "Hidden Gems": 3, "Culture": 2, "Romantic": 2, "Adventure": 1, "Foodie": 1, "Nightlife": 0, "Beach": 0},
        "interests": {"Hiking": 2, "Art Galleries": 1, "Foodie Tours": 2, "Music Festivals": 0, "Sports": 1},
        "distance_zone": 1, "base_flight": 85,
        "description": "Europe's hidden gem — peaceful, green, and charming.",
        "emoji": "🍃", "lat": 46.0569, "lon": 14.5058,
        "energy": 1, "social": 1, "splurge": 1, "sunshine": 2, "adventure": 1,
    },
    "Ghent, Belgium": {
        "vibes": {"Culture": 3, "Hidden Gems": 3, "Foodie": 2, "Romantic": 2, "Relaxation": 2, "Nightlife": 1, "Beach": 0, "Adventure": 0},
        "interests": {"Art Galleries": 3, "Foodie Tours": 2, "Music Festivals": 2, "Sports": 0, "Hiking": 0},
        "distance_zone": 1, "base_flight": 95,
        "description": "Medieval architecture, craft beer, and a thriving art scene.",
        "emoji": "🏰", "lat": 51.0543, "lon": 3.7174,
        "energy": 1, "social": 2, "splurge": 1, "sunshine": 1, "adventure": 0,
    },
    "Mallorca, Spain": {
        "vibes": {"Beach": 3, "Relaxation": 3, "Romantic": 2, "Foodie": 1, "Nightlife": 2, "Adventure": 1, "Culture": 1, "Hidden Gems": 1},
        "interests": {"Hiking": 2, "Foodie Tours": 1, "Music Festivals": 1, "Art Galleries": 0, "Sports": 2},
        "distance_zone": 1, "base_flight": 100,
        "description": "Crystal clear water, hidden coves, and coastal bliss.",
        "emoji": "🏖️", "lat": 39.6953, "lon": 3.0176,
        "energy": 2, "social": 2, "splurge": 2, "sunshine": 3, "adventure": 2,
    },
    "Chamonix, France": {
        "vibes": {"Adventure": 3, "Relaxation": 1, "Hidden Gems": 2, "Romantic": 2, "Culture": 1, "Nightlife": 0, "Beach": 0, "Foodie": 1},
        "interests": {"Hiking": 3, "Sports": 3, "Art Galleries": 0, "Foodie Tours": 0, "Music Festivals": 0},
        "distance_zone": 1, "base_flight": 110,
        "description": "Alpine adventure capital — hiking, skiing, and mountain air.",
        "emoji": "⛰️", "lat": 45.9237, "lon": 6.8694,
        "energy": 3, "social": 1, "splurge": 2, "sunshine": 2, "adventure": 3,
    },
    "Lisbon, Portugal": {
        "vibes": {"Culture": 3, "Foodie": 2, "Romantic": 2, "Hidden Gems": 2, "Relaxation": 2, "Nightlife": 2, "Beach": 1, "Adventure": 0},
        "interests": {"Art Galleries": 2, "Foodie Tours": 3, "Music Festivals": 2, "Hiking": 1, "Sports": 1},
        "distance_zone": 1, "base_flight": 95,
        "description": "Fado music, pastel de nata, and stunning hilltop views.",
        "emoji": "🎵", "lat": 38.7223, "lon": -9.1393,
        "energy": 2, "social": 2, "splurge": 1, "sunshine": 3, "adventure": 1,
    },
    "Reykjavik, Iceland": {
        "vibes": {"Adventure": 3, "Hidden Gems": 3, "Relaxation": 2, "Romantic": 2, "Culture": 1, "Nightlife": 1, "Beach": 0, "Foodie": 0},
        "interests": {"Hiking": 3, "Art Galleries": 1, "Music Festivals": 1, "Sports": 2, "Foodie Tours": 0},
        "distance_zone": 2, "base_flight": 180,
        "description": "Northern lights, geysers, and raw volcanic landscapes.",
        "emoji": "🌌", "lat": 64.1466, "lon": -21.9426,
        "energy": 3, "social": 1, "splurge": 3, "sunshine": 0, "adventure": 3,
    },
    "Dubrovnik, Croatia": {
        "vibes": {"Beach": 3, "Romantic": 3, "Culture": 2, "Hidden Gems": 2, "Relaxation": 2, "Nightlife": 1, "Adventure": 1, "Foodie": 1},
        "interests": {"Art Galleries": 1, "Hiking": 2, "Foodie Tours": 2, "Music Festivals": 1, "Sports": 1},
        "distance_zone": 1, "base_flight": 120,
        "description": "Stunning city walls and crystal Adriatic sea.",
        "emoji": "🏰", "lat": 42.6507, "lon": 18.0944,
        "energy": 2, "social": 2, "splurge": 2, "sunshine": 3, "adventure": 1,
    },
    "Prague, Czech Republic": {
        "vibes": {"Culture": 3, "Hidden Gems": 2, "Nightlife": 3, "Romantic": 2, "Foodie": 1, "Relaxation": 1, "Beach": 0, "Adventure": 0},
        "interests": {"Art Galleries": 2, "Music Festivals": 2, "Foodie Tours": 1, "Sports": 0, "Hiking": 0},
        "distance_zone": 1, "base_flight": 85,
        "description": "Fairytale architecture, cheap beer, and buzzing nightlife.",
        "emoji": "🍺", "lat": 50.0755, "lon": 14.4378,
        "energy": 3, "social": 3, "splurge": 1, "sunshine": 1, "adventure": 0,
    },
    "Seville, Spain": {
        "vibes": {"Culture": 3, "Foodie": 3, "Romantic": 3, "Nightlife": 2, "Hidden Gems": 1, "Relaxation": 1, "Beach": 0, "Adventure": 0},
        "interests": {"Art Galleries": 2, "Foodie Tours": 3, "Music Festivals": 2, "Sports": 1, "Hiking": 0},
        "distance_zone": 1, "base_flight": 90,
        "description": "Flamenco, tapas, and Moorish palaces under the Andalusian sun.",
        "emoji": "💃", "lat": 37.3891, "lon": -5.9845,
        "energy": 2, "social": 3, "splurge": 1, "sunshine": 3, "adventure": 0,
    },
    "Vienna, Austria": {
        "vibes": {"Culture": 3, "Romantic": 3, "Relaxation": 2, "Foodie": 2, "Hidden Gems": 1, "Nightlife": 1, "Beach": 0, "Adventure": 0},
        "interests": {"Art Galleries": 3, "Music Festivals": 3, "Foodie Tours": 2, "Sports": 0, "Hiking": 0},
        "distance_zone": 1, "base_flight": 105,
        "description": "Classical music, imperial palaces, and Viennese coffee culture.",
        "emoji": "🎻", "lat": 48.2082, "lon": 16.3738,
        "energy": 1, "social": 2, "splurge": 2, "sunshine": 1, "adventure": 0,
    },
    "Algarve, Portugal": {
        "vibes": {"Beach": 3, "Relaxation": 3, "Romantic": 2, "Adventure": 1, "Foodie": 1, "Hidden Gems": 1, "Nightlife": 1, "Culture": 0},
        "interests": {"Hiking": 2, "Sports": 2, "Foodie Tours": 1, "Art Galleries": 0, "Music Festivals": 0},
        "distance_zone": 1, "base_flight": 100,
        "description": "Dramatic cliffs, golden beaches, and fresh seafood.",
        "emoji": "🌊", "lat": 37.0179, "lon": -7.9304,
        "energy": 1, "social": 1, "splurge": 1, "sunshine": 3, "adventure": 2,
    },
}

# ── SLIDER EMOJI HELPERS ───────────────────────────────────────────────────────

def energy_emoji(v):
    if v <= 25: return "😴 Exhausted"
    if v <= 50: return "🧘 Chilling"
    if v <= 75: return "😊 Good vibes"
    return "⚡ Full power!"

def social_emoji(v):
    if v <= 25: return "💆🏻‍♀️ Don't call me, I'm busy"
    if v <= 50: return "🤝 Selective"
    if v <= 75: return "😄 Sociable"
    return "🎉 Party animal!"

def splurge_emoji(v):
    if v <= 25: return "🪙 Budget mode"
    if v <= 50: return "💳 Moderate"
    if v <= 75: return "💰 Treating myself"
    return "🤑 Splash out!"

def sunshine_emoji(v):
    if v <= 25: return "🌧️ Cozy indoors"
    if v <= 50: return "⛅ Flexible"
    if v <= 75: return "🌤️ Prefer sunny"
    return "☀️ Need that sun!"

def adventure_emoji(v):
    if v <= 25: return "🛋️ Sofa mode"
    if v <= 50: return "🚶 Easy pace"
    if v <= 75: return "🏃 Active"
    return "🧗 Adrenaline seeker!"

# ── SLIDER → VIBE MAPPING ──────────────────────────────────────────────────────

def sliders_to_profile(energy, social, splurge, sunshine, adventure):
    vibes = []
    interests = []
    if energy >= 70:
        vibes.append("Nightlife")
        if adventure >= 60:
            vibes.append("Adventure")
    elif energy <= 35:
        vibes.append("Relaxation")
    if social >= 70:
        vibes.append("Nightlife")
        interests.append("Music Festivals")
    elif social <= 35:
        vibes.append("Hidden Gems")
        vibes.append("Romantic")
    if splurge >= 70:
        vibes.append("Romantic")
        interests.append("Art Galleries")
        interests.append("Foodie Tours")
    elif splurge <= 35:
        vibes.append("Hidden Gems")
    if sunshine >= 70:
        vibes.append("Beach")
        vibes.append("Relaxation")
    elif sunshine <= 35:
        vibes.append("Culture")
        interests.append("Art Galleries")
    if adventure >= 70:
        vibes.append("Adventure")
        interests.append("Hiking")
        interests.append("Sports")
    elif adventure <= 35:
        vibes.append("Culture")
        vibes.append("Foodie")
        interests.append("Foodie Tours")
    vibes = list(dict.fromkeys(vibes)) or ["Culture"]
    interests = list(dict.fromkeys(interests))
    combined = (energy + adventure) / 2
    activity_level = "Intense" if combined >= 65 else ("Very Low" if combined < 35 else "Moderate")
    return vibes, interests, activity_level

# ── SCORING MODEL ──────────────────────────────────────────────────────────────

def score_cities(vibes, interests, activity_level, energy, social, splurge, sunshine, adventure, city_event_counts, city_weather):
    activity_multiplier = {"Very Low": 0.5, "Moderate": 1.0, "Intense": 1.5}
    mult = activity_multiplier[activity_level]
    results = []
    for city, data in CITY_DATA.items():
        vibe_score = sum(data["vibes"].get(v, 0) for v in vibes)
        if "Adventure" in vibes:
            vibe_score += data["vibes"].get("Adventure", 0) * (mult - 1)
        if "Relaxation" in vibes:
            vibe_score += data["vibes"].get("Relaxation", 0) * (0.5 - mult if mult < 1 else 0)
        interest_score = sum(data["interests"].get(i, 0) for i in interests)
        slider_score = 0
        slider_score += data.get("energy", 0) * (energy / 100) * 2
        slider_score += data.get("social", 0) * (social / 100) * 2
        slider_score += data.get("splurge", 0) * (splurge / 100) * 2
        slider_score += data.get("sunshine", 0) * (sunshine / 100) * 2
        slider_score += data.get("adventure", 0) * (adventure / 100) * 2
        event_count = city_event_counts.get(city, 0)
        event_bonus = min(event_count * 0.5, 3.0)
        if social >= 60 or energy >= 60:
            slider_score += event_bonus
        weather = city_weather.get(city, {})
        temp = weather.get("temp", 15)
        weathercode = weather.get("weathercode", 3)
        is_sunny = weathercode <= 2
        if sunshine >= 60 and is_sunny and temp >= 18:
            slider_score += 2.0
        elif sunshine <= 40 and not is_sunny:
            slider_score += 1.0
        total = vibe_score + interest_score + slider_score
        max_possible = len(vibes) * 3 + len(interests) * 3 + 30 + 3 + 2
        match_pct = min(round((total / max_possible) * 100), 99) if max_possible > 0 else 0
        results.append({
            "city": city, "vibe_score": round(vibe_score, 1),
            "interest_score": round(interest_score, 1),
            "slider_score": round(slider_score, 1),
            "total_score": round(total, 1), "match_pct": match_pct,
            "description": data["description"], "emoji": data["emoji"],
            "event_count": event_count, "weather": weather,
        })
    return pd.DataFrame(results).sort_values("total_score", ascending=False).reset_index(drop=True)

# ── LIVE DATA ──────────────────────────────────────────────────────────────────

def fetch_event_counts_all_cities():
    try:
        api_key = st.secrets["TICKETMASTER_API_KEY"]
    except:
        api_key = "9Rri7l1kutIcmyOqcbKstEN88GkcPGy7"
    counts = {}
    for city_name in CITY_DATA:
        clean_city = city_name.split(',')[0].strip()
        try:
            url = f"https://app.ticketmaster.com/discovery/v2/events.json?city={clean_city}&apikey={api_key}&size=20"
            data = requests.get(url, timeout=4).json()
            counts[city_name] = min(data.get("page", {}).get("totalElements", 0), 20)
        except:
            counts[city_name] = 0
    return counts

def fetch_weather_all_cities():
    descriptions = {
        0: ("☀️", "Clear sky"), 1: ("🌤️", "Mainly clear"), 2: ("⛅", "Partly cloudy"),
        3: ("☁️", "Overcast"), 45: ("🌫️", "Foggy"), 51: ("🌦️", "Light drizzle"),
        61: ("🌧️", "Light rain"), 63: ("🌧️", "Moderate rain"),
        71: ("🌨️", "Light snow"), 80: ("🌦️", "Showers"), 95: ("⛈️", "Thunderstorm"),
    }
    weather = {}
    for city_name, data in CITY_DATA.items():
        lat, lon = data.get("lat"), data.get("lon")
        try:
            url = (f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
                   f"&current=temperature_2m,weathercode,windspeed_10m,relative_humidity_2m&timezone=auto")
            result = requests.get(url, timeout=4).json()
            current = result.get("current", {})
            code = current.get("weathercode", 3)
            emoji, desc = descriptions.get(code, ("🌡️", "Variable"))
            weather[city_name] = {
                "temp": round(current.get("temperature_2m", 15)),
                "weathercode": code, "description": desc, "emoji": emoji,
                "wind": round(current.get("windspeed_10m", 0)),
                "humidity": current.get("relative_humidity_2m", 0),
            }
        except:
            weather[city_name] = {"temp": 15, "weathercode": 3, "description": "Unknown", "emoji": "🌡️", "wind": 0, "humidity": 0}
    return weather

def fetch_real_events(city_name):
    clean_city = city_name.split(',')[0].strip()
    try:
        api_key = st.secrets["TICKETMASTER_API_KEY"]
    except:
        api_key = "9Rri7l1kutIcmyOqcbKstEN88GkcPGy7"
    try:
        url = f"https://app.ticketmaster.com/discovery/v2/events.json?city={clean_city}&apikey={api_key}&size=4"
        data = requests.get(url, timeout=5).json()
        if "_embedded" in data:
            return data['_embedded']['events'][:4]
        return []
    except:
        return []

# ── LLM: MOOD NARRATIVE ────────────────────────────────────────────────────────

def get_mood_narrative(city, vibes, interests, activity_level, energy, social, splurge, sunshine, adventure, match_pct, city_weather, event_count):
    if not co:
        return None
    weather = city_weather.get(city, {})
    weather_desc = f"{weather.get('emoji','')} {weather.get('temp','?')}°C, {weather.get('description','unknown')}"
    prompt = f"""You are a travel mood expert. A traveler's current mood:
- Energy: {energy}/100, Social: {social}/100, Budget: {splurge}/100, Sunshine: {sunshine}/100, Adventure: {adventure}/100
- Matched with: {city} ({match_pct}% match)
- LIVE: Weather right now: {weather_desc}. Events this week: {event_count} on Ticketmaster.

Write a mood-aware, enthusiastic explanation referencing the live data. Respond ONLY with JSON:
{{
  "headline": "Punchy 6-8 word headline",
  "narrative": "2-3 sentences mentioning live weather and/or events specifically",
  "mood_tag": "2-3 word mood label (e.g. Recharge Mode, Party Ready)",
  "activities": ["Activity 1", "Activity 2", "Activity 3"],
  "packing_tip": "One tip based on live weather and activity level"
}}
Only JSON, no markdown."""
    response = co.chat(model="command-r-plus-08-2024", message=prompt, temperature=0.7)
    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    try:
        return json.loads(raw.strip())
    except:
        return None

# ── LLM: MULTI-AGENT DEBATE ────────────────────────────────────────────────────

AGENTS = [
    {"name": "Budget Traveler", "emoji": "🎒", "color": "#22c55e", "bg": "#f0fdf4", "border": "#86efac",
     "persona": "You are a Budget Traveler. You care about value for money, cheap flights, affordable food, and off-peak deals. Skeptical of pricey cities."},
    {"name": "Luxury Traveler", "emoji": "👑", "color": "#a855f7", "bg": "#faf5ff", "border": "#d8b4fe",
     "persona": "You are a Luxury Traveler. You care about premium experiences, fine dining, boutique hotels, and cultural prestige. Dismissive of budget destinations."},
    {"name": "Adventure Seeker", "emoji": "🧗", "color": "#f97316", "bg": "#fff7ed", "border": "#fdba74",
     "persona": "You are an Adventure Seeker. You care about hiking, sports, nature, and adrenaline. Bored by museum-heavy or relaxation cities."},
]

def _call_agent(agent, top3, vibes, activity_level, flight_costs):
    cities_info = "\n".join([f"- {c['city']}: {c['match_pct']}% match, €{flight_costs.get(c['city'],'?')} flight, {c.get('event_count',0)} events this week" for c in top3])
    prompt = f"""{agent['persona']}

Destinations: {cities_info}
Traveler vibes: {', '.join(vibes)}. Activity level: {activity_level}.

Evaluate each city in 1 sentence from your persona, pick your winner.
Respond ONLY with JSON:
{{"evaluations": {{"{top3[0]['city']}": "...", "{top3[1]['city']}": "...", "{top3[2]['city']}": "..."}}, "winner": "city name", "verdict": "One punchy sentence"}}"""
    response = co.chat(model="command-r-plus-08-2024", message=prompt, temperature=0.75)
    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    try:
        return json.loads(raw.strip())
    except:
        return {"evaluations": {}, "winner": top3[0]["city"], "verdict": "Unable to evaluate."}

def _call_moderator(agent_results, top3):
    debate = "\n".join([f"{a['emoji']} {a['name']}: recommends {r.get('winner','?')} — {r.get('verdict','')}" for a, r in zip(AGENTS, agent_results)])
    prompt = f"""You are a neutral moderator. Debate summary:\n{debate}\n\nSynthesize and give a final verdict. Only JSON:
{{"final_city": "one of the 3 cities", "consensus": "1 sentence on agreement/disagreement", "synthesis": "2 sentence balanced recommendation", "confidence": "High / Medium / Low"}}"""
    response = co.chat(model="command-r-plus-08-2024", message=prompt, temperature=0.5)
    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    try:
        return json.loads(raw.strip())
    except:
        return {"final_city": top3[0]["city"], "consensus": "Mixed opinions.", "synthesis": "Top-ranked city is the best fit.", "confidence": "Medium"}

def get_agent_debate(scores_df, vibes, activity_level, budget, travel_dates, city_weather):
    if not co:
        return None
    top3 = []
    flight_costs = {}
    for i in range(min(3, len(scores_df))):
        row = scores_df.iloc[i]
        city_name = row["city"]
        data = CITY_DATA.get(city_name, {})
        base = data.get("base_flight", 120)
        zone = data.get("distance_zone", 1)
        season_mult = 1.0
        if travel_dates and len(travel_dates) >= 1:
            month = travel_dates[0].month
            if month in [6, 7, 8, 12]: season_mult = 1.35
            elif month in [4, 5, 9, 10]: season_mult = 1.1
        flight_costs[city_name] = round(base * zone * season_mult)
        top3.append({"city": city_name, "emoji": data.get("emoji", "🌍"), "match_pct": row["match_pct"], "event_count": row.get("event_count", 0)})
    agent_results = [_call_agent(agent, top3, vibes, activity_level, flight_costs) for agent in AGENTS]
    moderator = _call_moderator(agent_results, top3)
    return {"top3": top3, "agent_results": agent_results, "moderator": moderator, "flight_costs": flight_costs}

# ── COST MODEL ─────────────────────────────────────────────────────────────────

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

# ── CSS ────────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Lora:wght@700&display=swap');

html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }
.block-container { padding-top: 0.5rem !important; background: #fef9f4; }

/* Hero */
.hero-wrap {
    background: linear-gradient(160deg, #ff6b35 0%, #ff8c5a 40%, #ffb347 100%);
    border-radius: 0px; padding: 64px 52px 56px; margin-bottom: 32px;
    margin-left: -4rem; margin-right: -4rem;
    position: relative; overflow: hidden; border: none;
}
.hero-wrap::after {
    content: "🌍"; font-size: 260px; position: absolute;
    right: -20px; bottom: -40px; opacity: 0.1; line-height: 1;
}
.live-pill {
    display: inline-block; background: rgba(255,255,255,0.25); color: white;
    font-size: 10px; font-weight: 800; padding: 4px 14px;
    border-radius: 20px; letter-spacing: 2px; margin-bottom: 16px;
    backdrop-filter: blur(4px);
}
.hero-title {
    font-family: 'Lora', serif; font-size: 56px; font-weight: 700;
    color: white; margin: 0 0 12px; line-height: 1.1;
    text-shadow: 0 2px 12px rgba(0,0,0,0.1);
}
.hero-sub { font-size: 18px; color: rgba(255,255,255,0.88); max-width: 600px; line-height: 1.6; }

/* Mood panel — removed white box, sliders sit directly on page background */
.mood-panel {
    background: transparent; padding: 0; margin-bottom: 20px;
}
.mood-panel-title {
    font-family: 'Lora', serif; font-size: 20px; font-weight: 700;
    color: #1e1e2e; margin-bottom: 20px;
}
.slider-row { margin-bottom: 18px; }
.slider-header {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 4px;
}
.slider-name { font-size: 14px; font-weight: 700; color: #374151; }
.slider-val {
    font-size: 13px; font-weight: 700; color: #ff6b35;
    background: #fff3ee; padding: 3px 10px; border-radius: 12px;
}

/* Result cards */
.city-hero {
    background: linear-gradient(135deg, #ff6b35 0%, #ff9a6c 100%);
    border-radius: 24px; padding: 36px 40px; margin-bottom: 24px;
    position: relative; overflow: hidden;
}
.city-hero::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}
.city-emoji-big { font-size: 56px; display: block; margin-bottom: 10px; }
.city-name-big {
    font-family: 'Lora', serif; font-size: 40px; font-weight: 700;
    color: white; margin: 0 0 8px; line-height: 1.1;
}
.city-desc { font-size: 16px; color: rgba(255,255,255,0.85); margin: 0 0 18px; }
.pill {
    display: inline-block; background: rgba(255,255,255,0.25);
    color: white; font-weight: 700; font-size: 13px;
    padding: 6px 16px; border-radius: 20px; margin-right: 8px; margin-bottom: 6px;
    backdrop-filter: blur(4px);
}

/* Insight card */
.insight-card {
    background: #fffbf7; border-radius: 20px; padding: 28px 32px;
    border: 2px solid #fdd8c0; margin-bottom: 20px;
}
.insight-tag {
    display: inline-block; background: #ff6b35; color: white;
    font-size: 12px; font-weight: 800; padding: 4px 14px;
    border-radius: 20px; margin-bottom: 14px;
}
.insight-headline {
    font-family: 'Lora', serif; font-size: 22px; font-weight: 700;
    color: #1e1e2e; margin-bottom: 12px; line-height: 1.3;
}
.insight-narrative { font-size: 15px; color: #4b5563; line-height: 1.7; margin-bottom: 18px; }
.activity-pill {
    display: inline-block; background: #fff3ee; color: #ff6b35;
    font-weight: 700; font-size: 13px; padding: 6px 14px;
    border-radius: 20px; margin: 4px 4px 4px 0;
}
.tip-row {
    background: #fef3c7; border-radius: 12px; padding: 12px 16px;
    font-size: 13px; color: #92400e; margin-top: 14px; font-weight: 600;
}

/* Stat cards */
.stat-row { display: flex; gap: 12px; margin-bottom: 20px; }
.stat-bubble {
    flex: 1; background: white; border-radius: 16px; padding: 18px;
    text-align: center; box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border: 1.5px solid #f3f4f6;
}
.stat-bubble .s-icon { font-size: 24px; margin-bottom: 6px; }
.stat-bubble .s-val { font-family: 'Lora', serif; font-size: 26px; font-weight: 700; color: #1e1e2e; }
.stat-bubble .s-lab { font-size: 11px; font-weight: 700; color: #9ca3af; text-transform: uppercase; letter-spacing: 1px; margin-top: 2px; }

/* Debate */
.debate-wrap { background: #f9fafb; border-radius: 20px; padding: 24px; border: 1.5px solid #e5e7eb; margin: 20px 0; }
.agent-bubble {
    border-radius: 16px; padding: 18px 20px; margin-bottom: 12px;
    border: 1.5px solid;
}
.agent-name-row { font-size: 15px; font-weight: 800; margin-bottom: 10px; }
.agent-eval-line { font-size: 13px; color: #4b5563; line-height: 1.5; margin-bottom: 6px; }
.agent-pick {
    display: inline-block; font-size: 12px; font-weight: 700;
    padding: 4px 12px; border-radius: 20px; margin-top: 6px; color: white;
}
.verdict-card {
    background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
    border-radius: 18px; padding: 24px 28px; margin-top: 16px;
    border: 2px solid #ff6b35;
}
.verdict-label { font-size: 10px; font-weight: 800; letter-spacing: 3px; color: #ff9a6c; margin-bottom: 10px; text-transform: uppercase; }
.verdict-city { font-family: 'Lora', serif; font-size: 28px; font-weight: 700; color: white; margin-bottom: 8px; }
.verdict-text { font-size: 14px; color: rgba(255,255,255,0.75); line-height: 1.6; }
.conf-pill { display: inline-block; font-size: 11px; font-weight: 700; padding: 4px 12px; border-radius: 20px; margin-top: 12px; }

/* Events */
.event-bubble {
    background: white; border-radius: 16px; padding: 18px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06); border: 1.5px solid #f3f4f6;
}
.event-name { font-weight: 700; font-size: 14px; color: #1e1e2e; line-height: 1.4; margin-bottom: 6px; }
.event-date { font-size: 12px; color: #9ca3af; }

/* Chat */
.chat-wrap { background: white; border-radius: 20px; padding: 24px; border: 1.5px solid #f3f4f6; margin-top: 8px; }
.chat-title { font-family: 'Lora', serif; font-size: 20px; font-weight: 700; color: #1e1e2e; margin-bottom: 4px; }
.chat-sub { font-size: 13px; color: #9ca3af; margin-bottom: 16px; }

/* Limits */
.limit-wrap { background: #fffbeb; border-radius: 16px; padding: 22px 26px; border-left: 5px solid #fbbf24; margin-top: 12px; }
.limit-wrap h4 { font-family: 'Lora', serif; font-size: 16px; color: #1e1e2e; margin-bottom: 10px; }
.limit-wrap li { font-size: 13px; color: #6b7280; margin-bottom: 5px; line-height: 1.5; }

/* Section labels */
.sec-label { font-size: 11px; font-weight: 800; letter-spacing: 3px; text-transform: uppercase; color: #ff6b35; margin-bottom: 4px; }
.sec-title { font-family: 'Lora', serif; font-size: 24px; font-weight: 700; color: #1e1e2e; margin-bottom: 16px; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #fff8f4 0%, #fff3ee 100%) !important;
    border-right: 2px solid #fdd8c0 !important;
}
[data-testid="stSidebar"] * { color: #374151 !important; background-color: transparent !important; }
[data-testid="stSidebar"] h3 { color: #ff6b35 !important; }
[data-testid="stSidebar"] .stSlider { background: transparent !important; }
[data-testid="stSidebar"] .stSlider div[data-testid="stTickBar"] { background: transparent !important; }

/* Button */
.stButton > button {
    background: linear-gradient(135deg, #ff6b35, #ff9a6c) !important;
    color: white !important; border: none !important;
    border-radius: 50px !important; padding: 14px 32px !important;
    font-size: 17px !important; font-weight: 800 !important;
    font-family: 'Nunito', sans-serif !important;
    width: 100% !important; box-shadow: 0 6px 20px rgba(255,107,53,0.35) !important;
    letter-spacing: 0.5px !important;
}
</style>
""", unsafe_allow_html=True)

# ── HERO ───────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero-wrap">
    <div class="live-pill">● LIVE THIS WEEK</div>
    <div class="hero-title">Europe This Week 🌍</div>
    <p class="hero-sub">Slide into your mood — we'll find the European city that matches how you feel right now, using live events and real weather data.</p>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 🗓️ Trip Details")
    travel_dates = st.date_input("When are you going?", [])
    budget = st.slider("Max Flight Budget (€)", 50, 500, 200)
    st.markdown("---")
    st.markdown("### ✨ How it works")
    st.markdown("1. Set your mood sliders\n2. We fetch **live events + weather** for 15 cities\n3. AI matches your mood to the best city this week\n4. 3 AI agents debate your top picks\n5. You get a personalised city recommendation!")

# ── MOOD SLIDERS ───────────────────────────────────────────────────────────────

st.markdown("<div class='sec-label'>Step 1</div><div class='sec-title'>How are you feeling? 🎭</div>", unsafe_allow_html=True)

st.markdown("<div class='mood-panel-title'>Move the sliders to match your current mood 👇</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    energy = st.slider("🔋 Energy Level", 0, 100, 50, key="sl_energy")
    st.markdown(f"<div style='font-size:12px;color:#ff6b35;font-weight:700;margin-top:-12px;margin-bottom:16px;'>{energy_emoji(energy)}</div>", unsafe_allow_html=True)

    social = st.slider("👥 Social Appetite", 0, 100, 50, key="sl_social")
    st.markdown(f"<div style='font-size:12px;color:#ff6b35;font-weight:700;margin-top:-12px;margin-bottom:16px;'>{social_emoji(social)}</div>", unsafe_allow_html=True)

    splurge = st.slider("💸 Budget Mood", 0, 100, 50, key="sl_splurge")
    st.markdown(f"<div style='font-size:12px;color:#ff6b35;font-weight:700;margin-top:-12px;margin-bottom:16px;'>{splurge_emoji(splurge)}</div>", unsafe_allow_html=True)

with col2:
    sunshine = st.slider("☀️ Sunshine Craving", 0, 100, 50, key="sl_sunshine")
    st.markdown(f"<div style='font-size:12px;color:#ff6b35;font-weight:700;margin-top:-12px;margin-bottom:16px;'>{sunshine_emoji(sunshine)}</div>", unsafe_allow_html=True)

    adventure = st.slider("🧗 Adventure Appetite", 0, 100, 50, key="sl_adventure")
    st.markdown(f"<div style='font-size:12px;color:#ff6b35;font-weight:700;margin-top:-12px;margin-bottom:16px;'>{adventure_emoji(adventure)}</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col_btn, _ = st.columns([1, 2])
with col_btn:
    clicked = st.button("🗺️  Find My City This Week!", key="go_btn")

# ── SESSION STATE ──────────────────────────────────────────────────────────────

for key in ["chat_history", "recommendation_done", "current_city"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key == "chat_history" else (False if key == "recommendation_done" else None)

# ── MAIN LOGIC ─────────────────────────────────────────────────────────────────

if clicked:
    st.session_state.chat_history = []

    # Save slider values with different keys to avoid widget conflict
    saved_energy = energy
    saved_social = social
    saved_splurge = splurge
    saved_sunshine = sunshine
    saved_adventure = adventure

    with st.spinner("🌍 Fetching live events and weather for all 15 cities..."):
        city_event_counts = fetch_event_counts_all_cities()
        city_weather = fetch_weather_all_cities()

    vibes, interests, activity_level = sliders_to_profile(saved_energy, saved_social, saved_splurge, saved_sunshine, saved_adventure)

    with st.spinner("🎯 Matching your mood to this week's city vibes..."):
        scores_df = score_cities(vibes, interests, activity_level, saved_energy, saved_social, saved_splurge, saved_sunshine, saved_adventure, city_event_counts, city_weather)
        top = scores_df.iloc[0]
        city = top["city"]
        city_info = CITY_DATA[city]
        est_flight, est_act, total_est, affordable, season_label, num_days = estimate_cost(city, budget, travel_dates, activity_level)
        real_events = fetch_real_events(city)

    with st.spinner("✨ Generating your mood-aware travel narrative..."):
        llm_insight = get_mood_narrative(city, vibes, interests, activity_level, saved_energy, saved_social, saved_splurge, saved_sunshine, saved_adventure, top["match_pct"], city_weather, city_event_counts.get(city, 0))

    with st.spinner("🤖 Running AI agent debate on your top 3 cities..."):
        debate = get_agent_debate(scores_df, vibes, activity_level, budget, travel_dates, city_weather)

    # Store everything in session state WITHOUT conflicting widget keys
    st.session_state.recommendation_done = True
    st.session_state.current_city = city
    st.session_state.scores_df = scores_df
    st.session_state.top = top
    st.session_state.city_info = city_info
    st.session_state.est_flight = est_flight
    st.session_state.est_act = est_act
    st.session_state.total_est = total_est
    st.session_state.affordable = affordable
    st.session_state.season_label = season_label
    st.session_state.num_days = num_days
    st.session_state.real_events = real_events
    st.session_state.llm_insight = llm_insight
    st.session_state.debate = debate
    st.session_state.vibes = vibes
    st.session_state.interests = interests
    st.session_state.activity_level = activity_level
    st.session_state.city_weather = city_weather
    st.session_state.city_event_counts = city_event_counts
    # Save slider values with non-conflicting names
    st.session_state.saved_energy = saved_energy
    st.session_state.saved_social = saved_social
    st.session_state.saved_splurge = saved_splurge
    st.session_state.saved_sunshine = saved_sunshine
    st.session_state.saved_adventure = saved_adventure

    st.balloons()

# ── DISPLAY RESULTS ────────────────────────────────────────────────────────────

if st.session_state.recommendation_done:
    city = st.session_state.current_city
    top = st.session_state.top
    city_info = st.session_state.city_info
    scores_df = st.session_state.scores_df
    vibes = st.session_state.vibes
    interests = st.session_state.interests
    activity_level = st.session_state.activity_level
    city_weather = st.session_state.city_weather
    city_event_counts = st.session_state.city_event_counts
    llm_insight = st.session_state.llm_insight
    debate = st.session_state.debate
    real_events = st.session_state.real_events
    est_flight = st.session_state.est_flight
    est_act = st.session_state.est_act
    total_est = st.session_state.total_est
    affordable = st.session_state.affordable
    season_label = st.session_state.season_label
    num_days = st.session_state.num_days
    saved_energy = st.session_state.saved_energy
    saved_social = st.session_state.saved_social
    saved_splurge = st.session_state.saved_splurge
    saved_sunshine = st.session_state.saved_sunshine
    saved_adventure = st.session_state.saved_adventure

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Live Europe Mood Map ──
    st.markdown("<div class='sec-label'>Live This Week</div><div class='sec-title'>Europe's Mood Map 🗺️</div>", unsafe_allow_html=True)
    st.caption("Bubble size = live events this week · Color = current temperature · Updated in real time")

    map_data = []
    for city_name, data in CITY_DATA.items():
        w = city_weather.get(city_name, {})
        ev = city_event_counts.get(city_name, 0)
        row = scores_df[scores_df["city"] == city_name]
        match_pct = int(row["match_pct"].values[0]) if len(row) > 0 else 0
        map_data.append({
            "city": city_name.split(",")[0], "lat": data["lat"], "lon": data["lon"],
            "temp": w.get("temp", 15), "events": max(ev, 1),
            "match_pct": match_pct, "weather": w.get("description", ""),
        })

    map_df = pd.DataFrame(map_data)
    fig_map = px.scatter_geo(
        map_df, lat="lat", lon="lon", text="city",
        size="events", size_max=45,
        color="temp", color_continuous_scale=["#93c5fd", "#fde68a", "#fb923c", "#ef4444"],
        hover_data={"events": True, "temp": True, "match_pct": True, "weather": True, "lat": False, "lon": False},
        labels={"temp": "°C", "events": "Events", "match_pct": "Your match %"},
    )
    fig_map.update_traces(textposition="top center", textfont=dict(size=10, color="#374151"))
    fig_map.update_layout(
        geo=dict(scope="europe", showland=True, landcolor="#fef9f0",
                 showocean=True, oceancolor="#dbeafe",
                 showcoastlines=True, coastlinecolor="#e5e7eb",
                 showcountries=True, countrycolor="#e5e7eb"),
        height=420, margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_colorbar=dict(title="Temp °C", thickness=12, len=0.6),
    )
    st.plotly_chart(fig_map, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── City Hero Card ──
    w = city_weather.get(city, {})
    ev_count = city_event_counts.get(city, 0)
    st.markdown(f"""
    <div class="city-hero">
        <span class="city-emoji-big">{city_info['emoji']}</span>
        <div class="city-name-big">{city}</div>
        <div class="city-desc">{top['description']}</div>
        <span class="pill">⚡ {top['match_pct']}% mood match</span>
        <span class="pill">{w.get('emoji','')} {w.get('temp','?')}°C right now</span>
        <span class="pill">🎭 {ev_count} events this week</span>
    </div>
    """, unsafe_allow_html=True)

    # ── LLM Mood Insight ──
    if llm_insight:
        mood_tag = llm_insight.get("mood_tag", "")
        headline = llm_insight.get("headline", "")
        narrative = llm_insight.get("narrative", "")
        activities = llm_insight.get("activities", [])
        packing_tip = llm_insight.get("packing_tip", "")
        activities_html = "".join([f"<span class='activity-pill'>🎯 {a}</span>" for a in activities])
        st.markdown(f"""
        <div class="insight-card">
            <span class="insight-tag">✨ {mood_tag}</span>
            <div class="insight-headline">{headline}</div>
            <div class="insight-narrative">{narrative}</div>
            <div style='margin-bottom:8px;'>{activities_html}</div>
            <div class="tip-row">🎒 {packing_tip}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Stat Bubbles ──
    budget_diff = abs(budget - total_est)
    status = "✅ Under budget" if affordable else "⚠️ Over budget"
    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-bubble"><div class="s-icon">✈️</div><div class="s-val">€{est_flight}</div><div class="s-lab">Est. Flight · {season_label}</div></div>
        <div class="stat-bubble"><div class="s-icon">🎟️</div><div class="s-val">€{est_act}</div><div class="s-lab">Activities · {num_days} days</div></div>
        <div class="stat-bubble"><div class="s-icon">💰</div><div class="s-val">€{total_est}</div><div class="s-lab">{status} · €{budget_diff} diff</div></div>
        <div class="stat-bubble"><div class="s-icon">🎭</div><div class="s-val">{ev_count}</div><div class="s-lab">Live events this week</div></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Agent Debate ──
    if debate:
        st.markdown("<div class='sec-label'>Multi-Agent Analysis</div><div class='sec-title'>The AI Juries 🤖</div>", unsafe_allow_html=True)
        st.markdown("""
        <div style='background:#fff3ee;border-radius:14px;padding:16px 20px;margin-bottom:20px;border-left:4px solid #ff6b35;'>
            <p style='margin:0;font-size:14px;color:#374151;line-height:1.6;'>
                <b>How it works:</b> Three AI agents — each with a different travel personality — independently evaluate your top 3 matching cities.
                A neutral <b>Moderator</b> then reads all three opinions and delivers a final synthesized verdict.
                Each agent sees the same live event counts and flight costs, but weighs them differently based on their persona.
            </p>
        </div>
        """, unsafe_allow_html=True)
        top3 = debate["top3"]
        agent_results = debate["agent_results"]
        moderator = debate["moderator"]
        flight_costs = debate["flight_costs"]

        city_cols = st.columns(3)
        for i, c in enumerate(top3):
            w2 = city_weather.get(c["city"], {})
            with city_cols[i]:
                st.markdown(f"""
                <div style='background:white;border-radius:14px;padding:16px;text-align:center;border:1.5px solid #f3f4f6;box-shadow:0 2px 10px rgba(0,0,0,0.05);'>
                    <div style='font-size:30px;'>{c['emoji']}</div>
                    <div style='font-weight:800;font-size:14px;color:#1e1e2e;margin:6px 0 2px;'>{c['city'].split(',')[0]}</div>
                    <div style='font-size:12px;color:#9ca3af;'>{w2.get('emoji','')} {w2.get('temp','?')}°C · {c.get('event_count',0)} events</div>
                    <div style='font-size:13px;color:#ff6b35;font-weight:800;margin-top:4px;'>€{flight_costs.get(c['city'],'?')} · {c['match_pct']}% match</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='debate-wrap'>", unsafe_allow_html=True)

        for agent, result in zip(AGENTS, agent_results):
            evaluations = result.get("evaluations", {})
            winner = result.get("winner", "")
            verdict = result.get("verdict", "")
            evals_html = ""
            for c in top3:
                city_short = c["city"].split(",")[0]
                eval_text = evaluations.get(c["city"], "No evaluation.")
                is_winner = c["city"] == winner
                badge = f" <span style='background:{agent['color']};color:white;font-size:10px;padding:2px 8px;border-radius:10px;font-weight:800;'>TOP PICK ✓</span>" if is_winner else ""
                evals_html += f"<div class='agent-eval-line'><b>{c['emoji']} {city_short}{badge}</b> — {eval_text}</div>"
            st.markdown(f"""
            <div class="agent-bubble" style='background:{agent["bg"]};border-color:{agent["border"]};'>
                <div class="agent-name-row" style='color:{agent["color"]};'>{agent["emoji"]} {agent["name"]}</div>
                {evals_html}
                <span class="agent-pick" style='background:{agent["color"]};'>{verdict}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        conf_colors = {"High": "#22c55e", "Medium": "#f97316", "Low": "#ef4444"}
        conf = moderator.get("confidence", "Medium")
        final_city = moderator.get("final_city", city)
        final_emoji = next((c["emoji"] for c in top3 if c["city"] == final_city), "🌍")
        st.markdown(f"""
        <div class="verdict-card">
            <div class="verdict-label">⚖️ Final Verdict</div>
            <div class="verdict-city">{final_emoji} {final_city}</div>
            <div style='font-size:13px;color:rgba(255,255,255,0.5);margin-bottom:8px;'>{moderator.get("consensus","")}</div>
            <div class="verdict-text">{moderator.get("synthesis","")}</div>
            <span class="conf-pill" style='background:{conf_colors.get(conf,"#f97316")};color:white;'>Confidence: {conf}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Score chart ──
    with st.expander("📊 See full city ranking"):
        top5 = scores_df.head(8)
        fig2 = px.bar(top5, x="match_pct", y="city", orientation="h",
                      color="match_pct", color_continuous_scale=["#fde68a", "#fb923c", "#ff6b35"],
                      labels={"match_pct": "Mood Match %", "city": ""})
        fig2.update_layout(height=320, showlegend=False, coloraxis_showscale=False,
                           plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                           font=dict(family="Nunito"), yaxis={"categoryorder": "total ascending"},
                           margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Live Events ──
    st.markdown(f"<div class='sec-label'>Happening in {city.split(',')[0]}</div><div class='sec-title'>This Week's Events 🎭</div>", unsafe_allow_html=True)
    if real_events:
        ev_cols = st.columns(len(real_events))
        for i, event in enumerate(real_events):
            with ev_cols[i]:
                st.markdown(f"""
                <div class="event-bubble">
                    <div class="event-name">{event.get('name','Event')}</div>
                    <div class="event-date">📅 {event.get('dates',{}).get('start',{}).get('localDate','TBD')}</div>
                </div>
                """, unsafe_allow_html=True)
                st.link_button("Get Tickets 🎟️", event.get('url','#'), use_container_width=True)
    else:
        st.info("No events found via Ticketmaster right now.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Chatbot ──
    st.markdown(f"<div class='sec-label'>Ask Anything</div><div class='sec-title'>Your {city.split(',')[0]} Advisor 💬</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="chat-wrap">
        <div class="chat-title">Hi! Ask me anything about {city.split(',')[0]} 👋</div>
        <div class="chat-sub">What to do, where to eat, how to get there, what to pack — I'm here!</div>
    </div>
    """, unsafe_allow_html=True)

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if user_input := st.chat_input(f"Ask about {city.split(',')[0]}..."):
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                system_prompt = f"""You are a friendly travel assistant. The user is matched with {city} based on their mood this week.
Their mood: Energy {saved_energy}/100, Social {saved_social}/100, Budget {saved_splurge}/100, Sunshine {saved_sunshine}/100, Adventure {saved_adventure}/100.
Live weather in {city}: {city_weather.get(city,{}).get('temp','?')}°C, {city_weather.get(city,{}).get('description','')}.
Be concise, warm, and enthusiastic. Focus on {city}."""
                cohere_history = [{"role": "USER" if m["role"] == "user" else "CHATBOT", "message": m["content"]} for m in st.session_state.chat_history[:-1]]
                response = co.chat(model="command-r-plus-08-2024", message=user_input, chat_history=cohere_history, preamble=system_prompt, temperature=0.7)
                reply = response.text
            st.write(reply)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Limitations ──
    st.markdown("""
    <div class="limit-wrap">
        <h4>⚠️ A few things to keep in mind</h4>
        <ul>
            <li><b>15 cities only:</b> We cover 15 pre-selected European destinations.</li>
            <li><b>Slider mapping is rule-based:</b> Mood-to-vibe translation uses predefined thresholds, not learned preferences.</li>
            <li><b>Event counts are approximate:</b> Ticketmaster coverage varies by city.</li>
            <li><b>Weather is current, not forecast:</b> Shows today's conditions, not your travel dates.</li>
            <li><b>Agent opinions are simulated:</b> Budget/Luxury/Adventure personas reflect LLM knowledge, not real reviews.</li>
            <li><b>Cost estimates are approximate:</b> Based on typical prices, not real-time flight availability.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
