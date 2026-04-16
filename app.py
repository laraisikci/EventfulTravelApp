import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import cohere
import json
from datetime import date

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Eventful Travel App", layout="wide", page_icon="✈️")

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
    },
    "Paris, France": {
        "vibes": {"Romantic": 3, "Culture": 3, "Foodie": 3, "Hidden Gems": 1, "Relaxation": 1, "Nightlife": 1, "Beach": 0, "Adventure": 0},
        "interests": {"Art Galleries": 3, "Music Festivals": 1, "Sports": 1, "Hiking": 0, "Foodie Tours": 3},
        "distance_zone": 1, "base_flight": 100,
        "description": "Romance, world-class cuisine, and iconic art museums.",
        "emoji": "🗼", "lat": 48.8566, "lon": 2.3522,
    },
    "Amsterdam, Netherlands": {
        "vibes": {"Nightlife": 3, "Culture": 2, "Hidden Gems": 2, "Romantic": 2, "Foodie": 1, "Relaxation": 1, "Beach": 0, "Adventure": 1},
        "interests": {"Music Festivals": 3, "Art Galleries": 2, "Sports": 1, "Hiking": 0, "Foodie Tours": 1},
        "distance_zone": 1, "base_flight": 90,
        "description": "World-class DJs, canals, and a vibrant cultural scene.",
        "emoji": "🎧", "lat": 52.3676, "lon": 4.9041,
    },
    "Naples, Italy": {
        "vibes": {"Foodie": 3, "Culture": 2, "Hidden Gems": 2, "Beach": 2, "Romantic": 1, "Relaxation": 2, "Nightlife": 1, "Adventure": 0},
        "interests": {"Foodie Tours": 3, "Art Galleries": 2, "Music Festivals": 1, "Sports": 1, "Hiking": 1},
        "distance_zone": 1, "base_flight": 90,
        "description": "The birthplace of pizza with authentic markets and history.",
        "emoji": "🍕", "lat": 40.8518, "lon": 14.2681,
    },
    "Ljubljana, Slovenia": {
        "vibes": {"Relaxation": 3, "Hidden Gems": 3, "Culture": 2, "Romantic": 2, "Adventure": 1, "Foodie": 1, "Nightlife": 0, "Beach": 0},
        "interests": {"Hiking": 2, "Art Galleries": 1, "Foodie Tours": 2, "Music Festivals": 0, "Sports": 1},
        "distance_zone": 1, "base_flight": 85,
        "description": "Europe's hidden gem — peaceful, green, and charming.",
        "emoji": "🍃", "lat": 46.0569, "lon": 14.5058,
    },
    "Ghent, Belgium": {
        "vibes": {"Culture": 3, "Hidden Gems": 3, "Foodie": 2, "Romantic": 2, "Relaxation": 2, "Nightlife": 1, "Beach": 0, "Adventure": 0},
        "interests": {"Art Galleries": 3, "Foodie Tours": 2, "Music Festivals": 2, "Sports": 0, "Hiking": 0},
        "distance_zone": 1, "base_flight": 95,
        "description": "Medieval architecture, craft beer, and a thriving art scene.",
        "emoji": "🏰", "lat": 51.0543, "lon": 3.7174,
    },
    "Mallorca, Spain": {
        "vibes": {"Beach": 3, "Relaxation": 3, "Romantic": 2, "Foodie": 1, "Nightlife": 2, "Adventure": 1, "Culture": 1, "Hidden Gems": 1},
        "interests": {"Hiking": 2, "Foodie Tours": 1, "Music Festivals": 1, "Art Galleries": 0, "Sports": 2},
        "distance_zone": 1, "base_flight": 100,
        "description": "Crystal clear water, hidden coves, and coastal bliss.",
        "emoji": "🏖️", "lat": 39.6953, "lon": 3.0176,
    },
    "Chamonix, France": {
        "vibes": {"Adventure": 3, "Relaxation": 1, "Hidden Gems": 2, "Romantic": 2, "Culture": 1, "Nightlife": 0, "Beach": 0, "Foodie": 1},
        "interests": {"Hiking": 3, "Sports": 3, "Art Galleries": 0, "Foodie Tours": 0, "Music Festivals": 0},
        "distance_zone": 1, "base_flight": 110,
        "description": "Alpine adventure capital — hiking, skiing, and mountain air.",
        "emoji": "⛰️", "lat": 45.9237, "lon": 6.8694,
    },
    "Lisbon, Portugal": {
        "vibes": {"Culture": 3, "Foodie": 2, "Romantic": 2, "Hidden Gems": 2, "Relaxation": 2, "Nightlife": 2, "Beach": 1, "Adventure": 0},
        "interests": {"Art Galleries": 2, "Foodie Tours": 3, "Music Festivals": 2, "Hiking": 1, "Sports": 1},
        "distance_zone": 1, "base_flight": 95,
        "description": "Fado music, pastel de nata, and stunning hilltop views.",
        "emoji": "🎵", "lat": 38.7223, "lon": -9.1393,
    },
    "Reykjavik, Iceland": {
        "vibes": {"Adventure": 3, "Hidden Gems": 3, "Relaxation": 2, "Romantic": 2, "Culture": 1, "Nightlife": 1, "Beach": 0, "Foodie": 0},
        "interests": {"Hiking": 3, "Art Galleries": 1, "Music Festivals": 1, "Sports": 2, "Foodie Tours": 0},
        "distance_zone": 2, "base_flight": 180,
        "description": "Northern lights, geysers, and raw volcanic landscapes.",
        "emoji": "🌌", "lat": 64.1466, "lon": -21.9426,
    },
    "Dubrovnik, Croatia": {
        "vibes": {"Beach": 3, "Romantic": 3, "Culture": 2, "Hidden Gems": 2, "Relaxation": 2, "Nightlife": 1, "Adventure": 1, "Foodie": 1},
        "interests": {"Art Galleries": 1, "Hiking": 2, "Foodie Tours": 2, "Music Festivals": 1, "Sports": 1},
        "distance_zone": 1, "base_flight": 120,
        "description": "Stunning city walls and crystal Adriatic sea.",
        "emoji": "🏰", "lat": 42.6507, "lon": 18.0944,
    },
    "Prague, Czech Republic": {
        "vibes": {"Culture": 3, "Hidden Gems": 2, "Nightlife": 3, "Romantic": 2, "Foodie": 1, "Relaxation": 1, "Beach": 0, "Adventure": 0},
        "interests": {"Art Galleries": 2, "Music Festivals": 2, "Foodie Tours": 1, "Sports": 0, "Hiking": 0},
        "distance_zone": 1, "base_flight": 85,
        "description": "Fairytale architecture, cheap beer, and buzzing nightlife.",
        "emoji": "🍺", "lat": 50.0755, "lon": 14.4378,
    },
    "Seville, Spain": {
        "vibes": {"Culture": 3, "Foodie": 3, "Romantic": 3, "Nightlife": 2, "Hidden Gems": 1, "Relaxation": 1, "Beach": 0, "Adventure": 0},
        "interests": {"Art Galleries": 2, "Foodie Tours": 3, "Music Festivals": 2, "Sports": 1, "Hiking": 0},
        "distance_zone": 1, "base_flight": 90,
        "description": "Flamenco, tapas, and Moorish palaces under the Andalusian sun.",
        "emoji": "💃", "lat": 37.3891, "lon": -5.9845,
    },
    "Vienna, Austria": {
        "vibes": {"Culture": 3, "Romantic": 3, "Relaxation": 2, "Foodie": 2, "Hidden Gems": 1, "Nightlife": 1, "Beach": 0, "Adventure": 0},
        "interests": {"Art Galleries": 3, "Music Festivals": 3, "Foodie Tours": 2, "Sports": 0, "Hiking": 0},
        "distance_zone": 1, "base_flight": 105,
        "description": "Classical music, imperial palaces, and Viennese coffee culture.",
        "emoji": "🎻", "lat": 48.2082, "lon": 16.3738,
    },
    "Algarve, Portugal": {
        "vibes": {"Beach": 3, "Relaxation": 3, "Romantic": 2, "Adventure": 1, "Foodie": 1, "Hidden Gems": 1, "Nightlife": 1, "Culture": 0},
        "interests": {"Hiking": 2, "Sports": 2, "Foodie Tours": 1, "Art Galleries": 0, "Music Festivals": 0},
        "distance_zone": 1, "base_flight": 100,
        "description": "Dramatic cliffs, golden beaches, and fresh seafood.",
        "emoji": "🌊", "lat": 37.0179, "lon": -7.9304,
    },
}

# ── SCORING MODEL ──────────────────────────────────────────────────────────────

def score_cities(vibes, interests, activity_level):
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
        total = vibe_score + interest_score
        max_possible = len(vibes) * 3 + len(interests) * 3 if (vibes or interests) else 1
        match_pct = min(round((total / max_possible) * 100), 99) if max_possible > 0 else 0
        results.append({
            "city": city, "vibe_score": round(vibe_score, 1),
            "interest_score": round(interest_score, 1),
            "total_score": round(total, 1), "match_pct": match_pct,
            "description": data["description"], "emoji": data["emoji"],
        })
    return pd.DataFrame(results).sort_values("total_score", ascending=False).reset_index(drop=True)

# ── LLM FEATURE 1: Travel Narrative + Activities ───────────────────────────────

def get_llm_travel_insight(city, vibes, interests, activity_level, match_pct):
    """
    Calls Cohere with a carefully engineered prompt to return structured JSON.
    System prompt example:
        'You are a personalized travel expert. A traveler has been matched with {city}
         by a scoring algorithm ({match_pct}% match). Their profile: vibes, interests,
         activity level. Respond ONLY with a valid JSON object...'
    The JSON output drives the UI — non-straightforward post-processing.
    """
    if not co:
        return None

    prompt = f"""You are a personalized travel expert. A traveler has been matched with {city} by a scoring algorithm ({match_pct}% match).

Their profile:
- Trip vibes: {', '.join(vibes) if vibes else 'Not specified'}
- Personal interests: {', '.join(interests) if interests else 'Not specified'}
- Activity level: {activity_level}

Your task is to enrich this recommendation with personalized insights. You must respond ONLY with a valid JSON object — no explanation, no markdown, no extra text.

The JSON must have exactly this structure:
{{
  "narrative": "A 2-sentence personalized explanation of why this city matches their specific vibe profile. Be specific and enthusiastic.",
  "activities": [
    "Activity 1 tailored to their vibes and interests",
    "Activity 2 tailored to their vibes and interests",
    "Activity 3 tailored to their vibes and interests"
  ],
  "packing_tip": "One specific packing tip based on the city and activity level",
  "best_time_to_visit": "One sentence about the best time to visit given their vibe preferences"
}}

Remember: respond ONLY with the JSON object, nothing else."""

    response = co.chat(model="command-r-plus-08-2024", message=prompt, temperature=0.7)
    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        retry_prompt = f"""Return ONLY a JSON object with keys: narrative, activities (list of 3), packing_tip, best_time_to_visit.
City: {city}. Vibes: {', '.join(vibes)}. No markdown, no extra text, just the JSON."""
        retry_response = co.chat(model="command-r-plus-08-2024", message=retry_prompt, temperature=0.3)
        raw2 = retry_response.text.strip()
        if raw2.startswith("```"):
            raw2 = raw2.split("```")[1]
            if raw2.startswith("json"):
                raw2 = raw2[4:]
        try:
            return json.loads(raw2.strip())
        except:
            return None

# ── LLM FEATURE 3: Multi-Agent Debate ─────────────────────────────────────────

AGENTS = [
    {
        "name": "Budget Traveler",
        "emoji": "🎒",
        "color": "#4CAF50",
        "bg": "rgba(76,175,80,0.08)",
        "border": "#4CAF50",
        "persona": (
            "You are a Budget Traveler agent. You evaluate destinations purely through "
            "the lens of value for money. You care about: low flight costs, affordable "
            "accommodation, cheap local food, free or low-cost attractions, and off-peak "
            "travel opportunities. You are skeptical of expensive or overrated cities."
        ),
    },
    {
        "name": "Luxury Traveler",
        "emoji": "👑",
        "color": "#9C27B0",
        "bg": "rgba(156,39,176,0.08)",
        "border": "#9C27B0",
        "persona": (
            "You are a Luxury Traveler agent. You evaluate destinations through the lens "
            "of premium experiences. You care about: Michelin-starred restaurants, boutique "
            "hotels, exclusive experiences, cultural prestige, scenic beauty, and sophistication. "
            "You are dismissive of budget or party destinations."
        ),
    },
    {
        "name": "Adventure Seeker",
        "emoji": "🧗",
        "color": "#FF5722",
        "bg": "rgba(255,87,34,0.08)",
        "border": "#FF5722",
        "persona": (
            "You are an Adventure Seeker agent. You evaluate destinations through the lens "
            "of physical activity and outdoor excitement. You care about: hiking trails, "
            "water sports, extreme sports, nature access, and physical challenges. "
            "You are bored by museum-heavy or relaxation-focused cities."
        ),
    },
]

def _call_agent(agent, top3_cities, vibes, interests, activity_level, flight_costs):
    """
    Single agent evaluates the top 3 cities and picks a winner.
    Returns a dict with: winner, reasoning (per city), and verdict.
    """
    cities_info = "\n".join([
        f"- {c['city']} ({c['emoji']}): {c['match_pct']}% match score, est. flight €{flight_costs.get(c['city'], '?')}"
        for c in top3_cities
    ])

    prompt = f"""{agent['persona']}

A traveler is choosing between these 3 European destinations:
{cities_info}

Traveler profile:
- Vibes: {', '.join(vibes) if vibes else 'Not specified'}
- Interests: {', '.join(interests) if interests else 'Not specified'}
- Activity level: {activity_level}

From YOUR perspective as a {agent['name']}, evaluate each city in 1 sentence, then pick your top choice.
Respond ONLY with a valid JSON object with this exact structure:
{{
  "evaluations": {{
    "{top3_cities[0]['city']}": "Your 1-sentence evaluation from your persona",
    "{top3_cities[1]['city']}": "Your 1-sentence evaluation from your persona",
    "{top3_cities[2]['city']}": "Your 1-sentence evaluation from your persona"
  }},
  "winner": "The city name you recommend (must be one of the 3 above)",
  "verdict": "One punchy sentence explaining why your chosen city wins from your perspective"
}}

Respond ONLY with the JSON, no markdown, no extra text."""

    response = co.chat(model="command-r-plus-08-2024", message=prompt, temperature=0.75)
    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    try:
        return json.loads(raw)
    except:
        return {"evaluations": {}, "winner": top3_cities[0]["city"], "verdict": "Unable to evaluate at this time."}


def _call_moderator(agent_results, top3_cities, vibes, interests):
    """
    Moderator agent reads all 3 agent verdicts and synthesizes a final recommendation.
    This is the 4th LLM call — it receives the outputs of the first 3 as input,
    making this a genuine multi-agent pipeline.
    """
    debate_summary = ""
    for agent, result in zip(AGENTS, agent_results):
        debate_summary += f"\n{agent['emoji']} {agent['name']} recommends: {result.get('winner', '?')}\n"
        debate_summary += f"  Reason: {result.get('verdict', '')}\n"

    city_names = [c["city"] for c in top3_cities]

    prompt = f"""You are a neutral travel moderator. Three traveler personas have debated which of these destinations is best:
{', '.join(city_names)}

Here is the debate summary:
{debate_summary}

The traveler's profile:
- Vibes: {', '.join(vibes) if vibes else 'Not specified'}
- Interests: {', '.join(interests) if interests else 'Not specified'}

Your job is to synthesize the debate and give a final verdict. Consider all three perspectives and make a balanced recommendation.
Respond ONLY with a valid JSON object:
{{
  "final_city": "Your recommended city (must be one of the 3)",
  "consensus": "Was there agreement or disagreement among the agents? (1 sentence)",
  "synthesis": "2-sentence balanced explanation considering all perspectives",
  "confidence": "High / Medium / Low — how strongly does the debate support this choice?"
}}

Respond ONLY with the JSON, no markdown, no extra text."""

    response = co.chat(model="command-r-plus-08-2024", message=prompt, temperature=0.5)
    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    try:
        return json.loads(raw)
    except:
        return {
            "final_city": top3_cities[0]["city"],
            "consensus": "Mixed opinions across agents.",
            "synthesis": "Based on the overall profile, the top-ranked city is the best fit.",
            "confidence": "Medium"
        }


def get_agent_debate(scores_df, vibes, interests, activity_level, budget, travel_dates):
    """
    Orchestrates the full multi-agent debate pipeline:
    1. Get top 3 cities from scoring model
    2. Run 3 agent LLM calls (Budget, Luxury, Adventure)
    3. Run 1 moderator LLM call synthesizing the debate
    Returns all results for display.
    """
    if not co:
        return None

    # Build top 3 with flight cost estimates
    top3 = []
    flight_costs = {}
    for i in range(min(3, len(scores_df))):
        row = scores_df.iloc[i]
        city_name = row["city"]
        data = CITY_DATA.get(city_name, {})

        # Estimate flight cost for context
        base = data.get("base_flight", 120)
        zone = data.get("distance_zone", 1)
        season_mult = 1.0
        if travel_dates and len(travel_dates) >= 1:
            month = travel_dates[0].month
            if month in [6, 7, 8, 12]:
                season_mult = 1.35
            elif month in [4, 5, 9, 10]:
                season_mult = 1.1
        est_flight = round(base * zone * season_mult)
        flight_costs[city_name] = est_flight

        top3.append({
            "city": city_name,
            "emoji": data.get("emoji", "🌍"),
            "match_pct": row["match_pct"],
            "description": row["description"],
        })

    # Run 3 agent calls
    agent_results = []
    for agent in AGENTS:
        result = _call_agent(agent, top3, vibes, interests, activity_level, flight_costs)
        agent_results.append(result)

    # Run moderator call
    moderator = _call_moderator(agent_results, top3, vibes, interests)

    return {
        "top3": top3,
        "agent_results": agent_results,
        "moderator": moderator,
        "flight_costs": flight_costs,
    }

# ── LLM FEATURE 2: Travel Chatbot ─────────────────────────────────────────────

def get_chatbot_response(user_message, chat_history, city, vibes, interests):
    """
    Multi-call chatbot with full conversation history sent on every turn.
    System prompt is personalized with the recommended city and user profile.

    How context is maintained:
    - chat_history is a list of {"role": "user"/"assistant", "content": "..."}
    - On each turn, the full history is converted to Cohere's format and sent
    - This means the LLM always has the full conversation context
    - The preamble (system prompt) anchors the persona and city throughout
    """
    if not co:
        return "Cohere API key not configured."

    system_prompt = f"""You are a friendly and knowledgeable travel assistant for the Eventful Travel App.
The user has been recommended {city} based on their preferences: vibes ({', '.join(vibes)}), interests ({', '.join(interests)}).
Answer their travel questions specifically about {city} and their trip. Be concise, helpful, and enthusiastic.
If they ask about other destinations, you can briefly mention them but always bring focus back to {city}."""

    cohere_history = []
    for msg in chat_history:
        cohere_history.append({
            "role": "USER" if msg["role"] == "user" else "CHATBOT",
            "message": msg["content"]
        })

    response = co.chat(
        model="command-r-plus-08-2024",
        message=user_message,
        chat_history=cohere_history,
        preamble=system_prompt,
        temperature=0.7,
    )
    return response.text

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
        if month in [6, 7, 8, 12]:
            season_mult = 1.35
        elif month in [4, 5, 9, 10]:
            season_mult = 1.1
    daily_spend = {"Very Low": 40, "Moderate": 70, "Intense": 110}
    est_activities = daily_spend[activity_level] * num_days
    est_flight = round(base_flight * zone * season_mult)
    total = est_flight + est_activities
    affordable = total <= budget
    season_label = "Peak 🔴" if season_mult == 1.35 else ("Shoulder 🟡" if season_mult == 1.1 else "Off-peak 🟢")
    return est_flight, est_activities, total, affordable, season_label, num_days

# ── WEATHER ────────────────────────────────────────────────────────────────────

def fetch_weather(city_name):
    data = CITY_DATA.get(city_name, {})
    lat, lon = data.get("lat"), data.get("lon")
    if not lat or not lon:
        return None
    try:
        url = (f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
               f"&current=temperature_2m,weathercode,windspeed_10m,relative_humidity_2m&timezone=auto")
        result = requests.get(url, timeout=5).json()
        current = result.get("current", {})
        code = current.get("weathercode", 0)
        descriptions = {
            0: ("☀️", "Clear sky"), 1: ("🌤️", "Mainly clear"), 2: ("⛅", "Partly cloudy"),
            3: ("☁️", "Overcast"), 45: ("🌫️", "Foggy"), 51: ("🌦️", "Light drizzle"),
            61: ("🌧️", "Light rain"), 63: ("🌧️", "Moderate rain"),
            71: ("🌨️", "Light snow"), 80: ("🌦️", "Showers"), 95: ("⛈️", "Thunderstorm"),
        }
        emoji, desc = descriptions.get(code, ("🌡️", "Variable"))
        return {
            "temp": round(current.get("temperature_2m", 0)),
            "description": desc, "emoji": emoji,
            "wind": round(current.get("windspeed_10m", 0)),
            "humidity": current.get("relative_humidity_2m", 0),
        }
    except:
        return None

# ── TICKETMASTER ───────────────────────────────────────────────────────────────

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

# ── GLOBAL CSS ─────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Inter:wght@400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.block-container { padding-top: 1rem !important; }

.hero {
    background: linear-gradient(135deg, #FF4B4B 0%, #FF8C42 50%, #FFD166 100%);
    border-radius: 20px; padding: 52px 44px; margin-bottom: 32px;
    position: relative; overflow: hidden;
}
.hero::before {
    content: "✈️"; font-size: 180px; position: absolute;
    right: -10px; top: -20px; opacity: 0.12; line-height: 1;
}
.hero h1 {
    font-family: 'Playfair Display', serif !important; font-size: 52px !important;
    font-weight: 900 !important; color: white !important; margin: 0 0 10px 0 !important;
    line-height: 1.1 !important; text-shadow: 0 2px 10px rgba(0,0,0,0.15);
}
.hero p { font-size: 18px; color: rgba(255,255,255,0.92); margin: 0; font-weight: 500; }

.section-label {
    font-size: 11px; font-weight: 700; letter-spacing: 3px;
    text-transform: uppercase; color: #FF4B4B; margin-bottom: 6px;
}
.section-title {
    font-family: 'Playfair Display', serif; font-size: 26px;
    font-weight: 700; color: #1a1a2e; margin-bottom: 20px;
}

.rec-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border-radius: 20px; padding: 36px 40px; margin-bottom: 28px;
    position: relative; overflow: hidden;
}
.rec-card::after {
    content: ''; position: absolute; top: 0; left: 0; right: 0;
    height: 4px; background: linear-gradient(90deg, #FF4B4B, #FF8C42, #FFD166);
}
.rec-card .city-emoji { font-size: 48px; margin-bottom: 12px; display: block; }
.rec-card h2 {
    font-family: 'Playfair Display', serif; font-size: 38px; font-weight: 900;
    color: white; margin: 0 0 10px 0; line-height: 1.1;
}
.rec-card .tagline { font-size: 16px; color: rgba(255,255,255,0.75); margin: 0 0 16px 0; line-height: 1.5; }
.match-badge {
    display: inline-block; background: linear-gradient(135deg, #FF4B4B, #FF8C42);
    color: white; font-weight: 700; font-size: 14px;
    padding: 6px 16px; border-radius: 30px;
}

.llm-card {
    background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
    border-radius: 16px; padding: 24px 28px; margin: 20px 0;
    border-left: 5px solid #FFD166;
}
.llm-card .llm-label {
    font-size: 10px; font-weight: 700; letter-spacing: 3px;
    text-transform: uppercase; color: #FFD166; margin-bottom: 8px;
}
.llm-card .llm-narrative { font-size: 15px; color: rgba(255,255,255,0.9); line-height: 1.7; margin-bottom: 16px; }
.llm-card .activity-item {
    background: rgba(255,255,255,0.08); border-radius: 8px;
    padding: 8px 14px; margin-bottom: 8px; font-size: 14px; color: white;
}
.llm-card .tip-box {
    background: rgba(255,209,102,0.15); border-radius: 8px;
    padding: 10px 14px; margin-top: 12px; font-size: 13px; color: #FFD166;
}

.debate-container {
    background: #f8f9ff; border-radius: 20px; padding: 28px;
    border: 2px solid #e8e8ff; margin: 20px 0;
}
.agent-card {
    border-radius: 14px; padding: 18px 20px; margin-bottom: 12px;
    border-left: 5px solid; position: relative;
}
.agent-name {
    font-weight: 700; font-size: 14px; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;
}
.agent-eval { font-size: 13px; color: #444; line-height: 1.5; margin-bottom: 6px; }
.agent-verdict {
    font-size: 13px; font-weight: 600; padding: 6px 12px;
    border-radius: 20px; display: inline-block; margin-top: 4px;
}
.moderator-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
    border-radius: 16px; padding: 24px 28px; margin-top: 20px;
    border: 2px solid #FFD166;
}
.moderator-label {
    font-size: 10px; font-weight: 700; letter-spacing: 3px;
    text-transform: uppercase; color: #FFD166; margin-bottom: 12px;
}
.moderator-city {
    font-family: 'Playfair Display', serif; font-size: 28px;
    font-weight: 900; color: white; margin-bottom: 8px;
}
.moderator-synthesis { font-size: 15px; color: rgba(255,255,255,0.85); line-height: 1.7; }
.confidence-badge {
    display: inline-block; font-weight: 700; font-size: 12px;
    padding: 4px 14px; border-radius: 20px; margin-top: 12px;
}

.stat-card {
    background: white; border-radius: 16px; padding: 20px 24px;
    text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.07);
    border-top: 4px solid #FF4B4B;
}
.stat-card .stat-label { font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #888; margin-bottom: 6px; }
.stat-card .stat-value { font-family: 'Playfair Display', serif; font-size: 32px; font-weight: 700; color: #1a1a2e; }
.stat-card .stat-sub { font-size: 12px; color: #aaa; margin-top: 4px; }

.weather-card {
    background: linear-gradient(135deg, #1976D2 0%, #42A5F5 100%);
    border-radius: 16px; padding: 24px; color: white; height: 100%;
}
.weather-card .temp { font-family: 'Playfair Display', serif; font-size: 52px; font-weight: 900; line-height: 1; margin: 8px 0; }
.weather-card .w-label { font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; opacity: 0.8; }
.weather-card .w-desc { font-size: 18px; font-weight: 600; margin: 4px 0 12px; }
.weather-card .w-detail { font-size: 13px; opacity: 0.85; }

.alt-card {
    background: white; border-radius: 16px; padding: 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.07); border-left: 5px solid #FF8C42;
}
.alt-card .alt-name { font-family: 'Playfair Display', serif; font-size: 18px; font-weight: 700; color: #1a1a2e; margin-bottom: 4px; }
.alt-card .alt-pct { display: inline-block; background: #FFF3E0; color: #FF8C42; font-weight: 700; font-size: 12px; padding: 2px 10px; border-radius: 20px; margin-bottom: 8px; }
.alt-card .alt-desc { font-size: 13px; color: #666; line-height: 1.5; }

.event-card {
    background: white; border-radius: 16px; padding: 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.07); border-top: 4px solid #FFD166;
}
.event-card .event-name { font-weight: 700; font-size: 15px; color: #1a1a2e; margin-bottom: 6px; line-height: 1.3; }
.event-card .event-date { font-size: 12px; color: #888; margin-bottom: 12px; }

.chat-container {
    background: #f8f9fa; border-radius: 20px; padding: 28px;
    border: 2px solid #f0f0f0; margin-top: 12px;
}
.chat-header { font-family: 'Playfair Display', serif; font-size: 22px; font-weight: 700; color: #1a1a2e; margin-bottom: 4px; }
.chat-subheader { font-size: 13px; color: #888; margin-bottom: 20px; }

.limit-card {
    background: #FFFDE7; border-radius: 16px; padding: 24px 28px;
    border-left: 6px solid #FFD166; margin-top: 12px;
}
.limit-card h4 { font-family: 'Playfair Display', serif; font-size: 18px; color: #1a1a2e; margin-bottom: 12px; }
.limit-card li { font-size: 14px; color: #555; margin-bottom: 6px; line-height: 1.5; }

[data-testid="stSidebar"] { background: #1a1a2e !important; }
[data-testid="stSidebar"] * { color: white !important; }

.stButton > button {
    background: linear-gradient(135deg, #FF4B4B 0%, #FF8C42 100%) !important;
    color: white !important; border: none !important; border-radius: 50px !important;
    padding: 16px 32px !important; font-size: 18px !important; font-weight: 700 !important;
    width: 100% !important; box-shadow: 0 8px 24px rgba(255,75,75,0.35) !important;
}
hr { border-color: #f0f0f0 !important; }
</style>
""", unsafe_allow_html=True)

# ── HERO ───────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero">
    <h1>Where to next?</h1>
    <p>Tell us your vibe — we'll find your perfect European escape, debated by AI agents and backed by live data.</p>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 📍 Travel Details")
    travel_dates = st.date_input("When are you free?", [])
    budget = st.slider("Max Flight Budget (€)", 50, 1000, 300)
    st.markdown("---")
    st.markdown("### 🎨 Personal Interests")
    interests = st.multiselect(
        "What do you love?",
        ["Music Festivals", "Art Galleries", "Sports", "Hiking", "Foodie Tours"]
    )

# ── MAIN INPUTS ────────────────────────────────────────────────────────────────

st.markdown("<div class='section-label'>Step 1</div><div class='section-title'>What's the mood of this trip?</div>", unsafe_allow_html=True)

col_v, col_a = st.columns([2, 1])
with col_v:
    vibes = st.multiselect(
        "Trip Vibe — pick everything that applies:",
        ["Relaxation", "Adventure", "Nightlife", "Culture", "Hidden Gems", "Romantic", "Foodie", "Beach"],
        default=["Culture"]
    )
with col_a:
    activity_level = st.select_slider(
        "Activity level:",
        options=["Very Low", "Moderate", "Intense"],
        value="Moderate"
    )

st.markdown("<br>", unsafe_allow_html=True)

col_btn, _ = st.columns([1, 2])
with col_btn:
    clicked = st.button("✈️  SURPRISE ME", key="go_btn")

# ── SESSION STATE ──────────────────────────────────────────────────────────────

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "recommendation_done" not in st.session_state:
    st.session_state.recommendation_done = False
if "current_city" not in st.session_state:
    st.session_state.current_city = None

# ── MAIN LOGIC ─────────────────────────────────────────────────────────────────

if clicked:
    if not vibes and not interests:
        st.warning("Please select at least one vibe or interest!")
        st.stop()

    st.session_state.chat_history = []

    with st.spinner("Finding your perfect destination..."):
        scores_df = score_cities(vibes, interests, activity_level)
        top = scores_df.iloc[0]
        city = top["city"]
        city_info = CITY_DATA[city]
        est_flight, est_act, total_est, affordable, season_label, num_days = estimate_cost(city, budget, travel_dates, activity_level)
        weather = fetch_weather(city)
        real_events = fetch_real_events(city)

    with st.spinner("✨ Getting AI-powered travel insights..."):
        llm_insight = get_llm_travel_insight(city, vibes, interests, activity_level, top["match_pct"])

    with st.spinner("🤖 Running agent debate on your top 3 cities..."):
        debate = get_agent_debate(scores_df, vibes, interests, activity_level, budget, travel_dates)

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
    st.session_state.weather = weather
    st.session_state.real_events = real_events
    st.session_state.llm_insight = llm_insight
    st.session_state.debate = debate
    st.session_state.vibes = vibes
    st.session_state.interests = interests

    st.balloons()

# ── DISPLAY RESULTS ────────────────────────────────────────────────────────────

if st.session_state.recommendation_done:
    city = st.session_state.current_city
    top = st.session_state.top
    city_info = st.session_state.city_info
    est_flight = st.session_state.est_flight
    est_act = st.session_state.est_act
    total_est = st.session_state.total_est
    affordable = st.session_state.affordable
    season_label = st.session_state.season_label
    num_days = st.session_state.num_days
    weather = st.session_state.weather
    real_events = st.session_state.real_events
    llm_insight = st.session_state.llm_insight
    debate = st.session_state.debate
    scores_df = st.session_state.scores_df
    vibes = st.session_state.vibes
    interests = st.session_state.interests

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Recommendation Card ──
    st.markdown(f"""
    <div class="rec-card">
        <span class="city-emoji">{city_info['emoji']}</span>
        <h2>{city}</h2>
        <p class="tagline">{top['description']}</p>
        <span class="match-badge">⚡ {top['match_pct']}% Match</span>
    </div>
    """, unsafe_allow_html=True)

    # ── LLM Insight Card ──
    if llm_insight:
        activities_html = "".join([f"<div class='activity-item'>🎯 {a}</div>" for a in llm_insight.get("activities", [])])
        st.markdown(f"""
        <div class="llm-card">
            <div class="llm-label">✨ AI-Powered Travel Insight</div>
            <div class="llm-narrative">{llm_insight.get("narrative", "")}</div>
            <div style='font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#FFD166;margin-bottom:10px;'>Recommended Activities</div>
            {activities_html}
            <div class="tip-box">🎒 Packing tip: {llm_insight.get("packing_tip", "")}</div>
            <div class="tip-box" style='margin-top:8px;'>📅 Best time: {llm_insight.get("best_time_to_visit", "")}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── MULTI-AGENT DEBATE (Feature 3) ────────────────────────────────────────
    if debate:
        st.markdown("<div class='section-label'>New in v3</div><div class='section-title'>🤖 AI Agent Debate</div>", unsafe_allow_html=True)

        top3 = debate["top3"]
        agent_results = debate["agent_results"]
        moderator = debate["moderator"]
        flight_costs = debate["flight_costs"]

        # Show the 3 cities being debated
        st.markdown(f"**Three AI agents with different travel personas debated your top 3 cities:**")
        city_cols = st.columns(3)
        for i, c in enumerate(top3):
            with city_cols[i]:
                st.markdown(f"""
                <div style='text-align:center;padding:16px;background:white;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,0.07);'>
                    <div style='font-size:32px;'>{c['emoji']}</div>
                    <div style='font-weight:700;font-size:14px;color:#1a1a2e;margin-top:6px;'>{c['city'].split(',')[0]}</div>
                    <div style='font-size:12px;color:#888;'>{c['match_pct']}% match · €{flight_costs.get(c['city'], '?')} flight</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Agent verdicts
        st.markdown("<div class='debate-container'>", unsafe_allow_html=True)
        for agent, result in zip(AGENTS, agent_results):
            evaluations = result.get("evaluations", {})
            winner = result.get("winner", "")
            verdict = result.get("verdict", "")

            evals_html = ""
            for c in top3:
                city_short = c["city"].split(",")[0]
                eval_text = evaluations.get(c["city"], "No evaluation available.")
                is_winner = c["city"] == winner
                winner_badge = f" <span style='background:{agent['color']};color:white;font-size:10px;padding:2px 8px;border-radius:10px;font-weight:700;'>PICK ✓</span>" if is_winner else ""
                evals_html += f"<div class='agent-eval'><b>{c['emoji']} {city_short}{winner_badge}</b> — {eval_text}</div>"

            st.markdown(f"""
            <div class="agent-card" style='background:{agent["bg"]};border-left-color:{agent["border"]};'>
                <div class="agent-name" style='color:{agent["color"]};'>{agent["emoji"]} {agent["name"]}</div>
                {evals_html}
                <span class="agent-verdict" style='background:{agent["color"]};color:white;'>{verdict}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Moderator verdict
        confidence_colors = {"High": "#4CAF50", "Medium": "#FF9800", "Low": "#F44336"}
        conf = moderator.get("confidence", "Medium")
        conf_color = confidence_colors.get(conf, "#FF9800")
        final_city = moderator.get("final_city", city)
        final_emoji = next((c["emoji"] for c in top3 if c["city"] == final_city), "🌍")

        st.markdown(f"""
        <div class="moderator-card">
            <div class="moderator-label">⚖️ Moderator Verdict</div>
            <div class="moderator-city">{final_emoji} {final_city}</div>
            <div style='font-size:13px;color:rgba(255,255,255,0.6);margin-bottom:8px;'>{moderator.get("consensus", "")}</div>
            <div class="moderator-synthesis">{moderator.get("synthesis", "")}</div>
            <span class="confidence-badge" style='background:{conf_color};color:white;'>Confidence: {conf}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Stat Cards ──
    s1, s2, s3, s4 = st.columns(4)
    budget_diff = abs(budget - total_est)
    status_icon = "✅" if affordable else "⚠️"
    with s1:
        st.markdown(f"""<div class="stat-card"><div class="stat-label">Est. Flight</div><div class="stat-value">€{est_flight}</div><div class="stat-sub">Season: {season_label}</div></div>""", unsafe_allow_html=True)
    with s2:
        st.markdown(f"""<div class="stat-card"><div class="stat-label">Activities</div><div class="stat-value">€{est_act}</div><div class="stat-sub">{num_days} day{'s' if num_days > 1 else ''}</div></div>""", unsafe_allow_html=True)
    with s3:
        st.markdown(f"""<div class="stat-card"><div class="stat-label">Total Cost</div><div class="stat-value">€{total_est}</div><div class="stat-sub">{status_icon} €{budget_diff} {'under' if affordable else 'over'}</div></div>""", unsafe_allow_html=True)
    with s4:
        st.markdown(f"""<div class="stat-card"><div class="stat-label">Match Score</div><div class="stat-value">{top['match_pct']}%</div><div class="stat-sub">Based on {len(vibes)} vibes</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Map + Weather ──
    col_map, col_wx = st.columns([2, 1])
    with col_map:
        st.markdown("<div class='section-label'>Location</div><div class='section-title'>Where is it?</div>", unsafe_allow_html=True)
        fig_map = go.Figure(go.Scattergeo(
            lat=[city_info["lat"]], lon=[city_info["lon"]],
            mode="markers+text",
            marker=dict(size=20, color="#FF4B4B", symbol="circle", line=dict(width=3, color="white")),
            text=[city], textposition="top center",
            textfont=dict(size=14, color="#1a1a2e"),
        ))
        fig_map.update_layout(
            geo=dict(scope="europe", showland=True, landcolor="#f5f5f5",
                     showocean=True, oceancolor="#E3F2FD",
                     showcoastlines=True, coastlinecolor="#ccc",
                     showcountries=True, countrycolor="#ddd",
                     center=dict(lat=city_info["lat"], lon=city_info["lon"]),
                     projection_scale=4),
            height=320, margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with col_wx:
        st.markdown("<div class='section-label'>Right now</div><div class='section-title'>Weather</div>", unsafe_allow_html=True)
        if weather:
            st.markdown(f"""
            <div class="weather-card">
                <div class="w-label">Current conditions</div>
                <div class="temp">{weather['emoji']} {weather['temp']}°C</div>
                <div class="w-desc">{weather['description']}</div>
                <div class="w-detail">💨 {weather['wind']} km/h wind</div>
                <div class="w-detail">💧 {weather['humidity']}% humidity</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Weather unavailable.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Score Charts ──
    st.markdown("<div class='section-label'>Model output</div><div class='section-title'>Why this destination?</div>", unsafe_allow_html=True)
    col_bar, col_rank = st.columns(2)
    with col_bar:
        fig = px.bar(
            {"Category": ["Vibe Match", "Interest Match"], "Score": [top["vibe_score"], top["interest_score"]]},
            x="Category", y="Score", color="Category",
            color_discrete_sequence=["#FF4B4B", "#FF8C42"], title="Score Breakdown for " + city.split(",")[0],
        )
        fig.update_layout(showlegend=False, height=300, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter"))
        fig.update_yaxes(gridcolor="#f0f0f0")
        st.plotly_chart(fig, use_container_width=True)

    with col_rank:
        top5 = scores_df.head(5)
        fig2 = px.bar(top5, x="match_pct", y="city", orientation="h",
                      color="match_pct", color_continuous_scale=["#FFD166", "#FF8C42", "#FF4B4B"],
                      labels={"match_pct": "Match %", "city": ""}, title="Top 5 Destinations")
        fig2.update_layout(height=300, showlegend=False, coloraxis_showscale=False,
                           plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                           font=dict(family="Inter"), yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig2, use_container_width=True)

    with st.expander("📊 See full ranking of all 15 destinations"):
        fig3 = px.bar(scores_df, x="match_pct", y="city", orientation="h",
                      color="match_pct", color_continuous_scale=["#FFD166", "#FF8C42", "#FF4B4B"],
                      labels={"match_pct": "Match %", "city": ""})
        fig3.update_layout(height=520, coloraxis_showscale=False,
                           plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                           yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Alternatives ──
    st.markdown("<div class='section-label'>Also consider</div><div class='section-title'>Other destinations you might love</div>", unsafe_allow_html=True)
    alt_cols = st.columns(3)
    for i, (_, row) in enumerate(scores_df.iloc[1:4].iterrows()):
        with alt_cols[i]:
            alt_info = CITY_DATA[row['city']]
            st.markdown(f"""
            <div class="alt-card">
                <div style='font-size:28px;margin-bottom:8px;'>{alt_info['emoji']}</div>
                <div class="alt-name">{row['city']}</div>
                <span class="alt-pct">⚡ {row['match_pct']}% match</span>
                <div class="alt-desc">{row['description']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Live Events ──
    st.markdown(f"<div class='section-label'>Live in {city.split(',')[0]}</div><div class='section-title'>🎭 Upcoming Events</div>", unsafe_allow_html=True)
    if real_events:
        ev_cols = st.columns(len(real_events))
        for i, event in enumerate(real_events):
            with ev_cols[i]:
                st.markdown(f"""
                <div class="event-card">
                    <div class="event-name">{event.get('name', 'Event')}</div>
                    <div class="event-date">📅 {event.get('dates', {}).get('start', {}).get('localDate', 'TBD')}</div>
                </div>
                """, unsafe_allow_html=True)
                st.link_button("View Tickets 🎟️", event.get('url', '#'), use_container_width=True)
    else:
        st.info("No live events found for this location right now via Ticketmaster.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── CHATBOT ───────────────────────────────────────────────────────────────
    st.markdown("<div class='section-label'>AI Travel Assistant</div><div class='section-title'>💬 Ask me anything about your trip</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="chat-container">
        <div class="chat-header">Your {city.split(',')[0]} Travel Assistant</div>
        <div class="chat-subheader">Ask me about things to do, what to pack, local tips, transport, food, and more.</div>
    </div>
    """, unsafe_allow_html=True)

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if user_input := st.chat_input(f"Ask something about {city.split(',')[0]}..."):
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                reply = get_chatbot_response(
                    user_input,
                    st.session_state.chat_history[:-1],
                    city, vibes, interests
                )
            st.write(reply)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Limitations ──
    st.markdown("""
    <div class="limit-card">
        <h4>⚠️ Model Limitations</h4>
        <ul>
            <li><b>Fixed city list:</b> Only 15 pre-selected European destinations are considered by the scoring model.</li>
            <li><b>Static scores:</b> Vibe and interest scores were manually assigned and do not update based on real-world data.</li>
            <li><b>Agent personas are simulated:</b> The Budget, Luxury and Adventure agents are LLM personas, not real user data — their opinions reflect training knowledge, not live prices or reviews.</li>
            <li><b>LLM hallucination risk:</b> AI-generated activity suggestions are based on general knowledge and may not reflect current availability.</li>
            <li><b>Approximate costs:</b> Flight prices do not reflect real-time pricing or your departure city.</li>
            <li><b>Current weather only:</b> Weather reflects today's conditions, not the forecast for your travel dates.</li>
            <li><b>Ticketmaster coverage varies:</b> Live event availability depends on the API and may not include all local events.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
