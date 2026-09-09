from datetime import datetime, timedelta
import base64
import requests
import streamlit as st
from streamlit_autorefresh import st_autorefresh

API_KEY = "API_KEY"
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": API_KEY}

st.set_page_config(page_title="Live Sport Tracker", layout="wide")

count = st_autorefresh(interval=30000, key="datarefresh")

st.sidebar.title("Parametres")
competition_choice = st.sidebar.selectbox(
    "Choisir une competition", ["Ligue des Champions", "Ligue 1"]
)

comp_codes = {"Ligue des Champions": "CL", "Ligue 1": "FL1"}
current_code = comp_codes[competition_choice]

st.title(f"Tracker - {competition_choice}")


@st.cache_data(ttl=30)
def get_all_matches(comp_code):
  url = f"{BASE_URL}/competitions/{comp_code}/matches"
  response = requests.get(url, headers=HEADERS)
  if response.status_code == 200:
    return response.json().get("matches", [])
  return []


@st.cache_data(ttl=60)
def get_standings(comp_code):
  url = f"{BASE_URL}/competitions/{comp_code}/standings"
  response = requests.get(url, headers=HEADERS)
  if response.status_code == 200:
    return response.json().get("standings", [])
  return []


matches = get_all_matches(current_code)
standings = get_standings(current_code)

matchdays = sorted(
    list(set(m.get("matchday") for m in matches if m.get("matchday")))
)

if matchdays:
  selected_matchday = st.sidebar.selectbox(
      "Filtrer par Journée",
      matchdays,
      format_func=lambda x: f"Journée {x}",
  )
else:
  selected_matchday = None

st.markdown("---")

# Création de deux onglets : l'un pour les matchs, l'autre pour le classement
tab_matches, tab_standings = st.tabs(["Matchs & Live", "Classement"])

with tab_matches:
  if "previous_scores" not in st.session_state:
    st.session_state.previous_scores = {}

  goal_scored = False
  matches_found = False

  for match in matches:
    if selected_matchday and match.get("matchday") != selected_matchday:
      continue

    matches_found = True
    match_id = match["id"]
    status = match["status"]
    utc_date = match["utcDate"]
    match_date = utc_date.split("T")[0]
    match_time = utc_date.split("T")[1][:5]

    home = match["homeTeam"]["name"]
    home_crest = match["homeTeam"].get("crest")
    away = match["awayTeam"]["name"]
    away_crest = match["awayTeam"].get("crest")

    score = match.get("score", {})
    full_time = score.get("fullTime", {})
    home_goals = full_time.get("home")
    away_goals = full_time.get("away")

    if status in ["IN_PLAY", "PAUSED"] and home_goals is not None and away_goals is not None:
      current_match_score = (home_goals, away_goals)
      if match_id in st.session_state.previous_scores:
        if current_match_score != st.session_state.previous_scores[match_id]:
          goal_scored = True
      st.session_state.previous_scores[match_id] = current_match_score

    with st.container(border=True):
      c1, c2, c3, c4, c5, c6 = st.columns([1.5, 0.4, 2, 1, 2, 0.4])

      with c1:
        if status == "FINISHED":
          st.markdown(
              "<span style='color: gray; font-weight: bold;'>TERMINE</span>",
              unsafe_allow_html=True,
          )
        elif status in ["IN_PLAY", "PAUSED"]:
          st.markdown(
              "<span style='color: green; font-weight: bold;'>EN COURS</span>",
              unsafe_allow_html=True,
          )
        else:
          st.markdown(
              f"<span style='color: blue;'>{match_date} ({match_time} UTC)</span>",
              unsafe_allow_html=True,
          )

      with c2:
        if home_crest:
          st.image(home_crest, width=30)

      with c3:
        st.markdown(f"**{home}**")

      with c4:
        if status in ["FINISHED", "IN_PLAY", "PAUSED"]:
          st.markdown(
              f"<h4 style='text-align: center; margin: 0;'>{home_goals} -"
              f" {away_goals}</h4>",
              unsafe_allow_html=True,
          )
        else:
          st.markdown(
              "<h4 style='text-align: center; margin: 0; color: gray;'>VS</h4>",
              unsafe_allow_html=True,
          )

      with c5:
        st.markdown(f"**{away}**")

      with c6:
        if away_crest:
          st.image(away_crest, width=30)

  if goal_scored:
    st.balloons()
    st.toast("BUT MARQUE ! Grosse ambiance sur le multiplex !")
    try:
      with open("JingleBut.mp3", "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        audio_html = f"""
                    <audio autoplay>
                        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                    </audio>
                """
        st.markdown(audio_html, unsafe_allow_html=True)
    except FileNotFoundError:
      st.warning("Fichier JingleBut.mp3 introuvable dans le dossier.")

  if not matches_found:
    st.info("Aucun match trouve pour cette selection.")

with tab_standings:
  if standings:
    # Pour la Ligue des champions (phase de ligue unique) ou Ligue 1 (groupe unique)
    table_data = standings[0].get("table", [])
    if table_data:
      formatted_table = []
      for row in table_data:
        formatted_table.append({
            "Rang": row.get("position"),
            "Equipe": row.get("team", {}).get("name"),
            "Pts": row.get("points"),
            "J": row.get("playedGames"),
            "G": row.get("won"),
            "N": row.get("draw"),
            "P": row.get("lost"),
            "BP": row.get("goalsFor"),
            "BC": row.get("goalsAgainst"),
            "DB": row.get("goalDifference"),
        })
      st.dataframe(
          formatted_table,
          use_container_width=True,
          hide_index=True,
      )
    else:
      st.info("Classement indisponible pour le moment.")
  else:
      st.info("Aucune donnée de classement trouvée.")
