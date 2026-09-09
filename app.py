from datetime import datetime, timedelta
import requests
import streamlit as st

API_KEY = "ffedc415bdcc4686afee119fcfacf9ad"
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": API_KEY}

st.set_page_config(page_title="Live Sport Tracker - LDC", layout="centered")

st.title("Tracker Ligue des Champions")

if "selected_date" not in st.session_state:
  st.session_state.selected_date = datetime.now().date()


# Récupération de tous les matchs de la LDC avec mise en cache (TTL de 5 minutes)
@st.cache_data(ttl=300)
def get_all_matches():
  url = f"{BASE_URL}/competitions/CL/matches"
  response = requests.get(url, headers=HEADERS)
  if response.status_code == 200:
    return response.json().get("matches", [])
  return []


matches = get_all_matches()

# Barre de navigation des jours avec des colonnes
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
  if st.button("<- Jour Précédent"):
    st.session_state.selected_date -= timedelta(days=1)
    st.rerun()

with col2:
  st.markdown(
      f"<h4 style='text-align: center;'>{st.session_state.selected_date.strftime('%d-%m-%Y')}</h4>",
      unsafe_allow_html=True,
  )

with col3:
  if st.button("Jour Suivant ->"):
    st.session_state.selected_date += timedelta(days=1)
    st.rerun()

# Filtrage des matchs pour la date active
selected_date_str = st.session_state.selected_date.strftime("%Y-%m-%d")
st.write(f"Matchs du : {selected_date_str}")

matches_found = False

for match in matches:
  utc_date = match["utcDate"]
  match_date = utc_date.split("T")[0]

  if match_date == selected_date_str:
    matches_found = True
    status = match["status"]
    home = match["homeTeam"]["name"]
    away = match["awayTeam"]["name"]

    score = match.get("score", {})
    full_time = score.get("fullTime", {})
    home_goals = full_time.get("home")
    away_goals = full_time.get("away")
    match_time = utc_date.split("T")[1][:5]

    if status == "FINISHED":
      st.info(f"**[TERMINE]** {home} **{home_goals} - {away_goals}** {away}")
    elif status in ["IN_PLAY", "PAUSED"]:
      st.success(f"**[EN COURS]** {home} **{home_goals} - {away_goals}** {away}")
    else:
      st.write(f"**[A VENIR - {match_time} UTC]** {home} vs {away}")

if not matches_found:
  st.warning("Aucun match de Ligue des Champions programmé à cette date.")