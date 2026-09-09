from datetime import datetime
import time
import requests

API_KEY = "ffedc415bdcc4686afee119fcfacf9ad"
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": API_KEY}


def get_champions_league_matches():
  url = f"{BASE_URL}/competitions/CL/matches"
  response = requests.get(url, headers=HEADERS)

  if response.status_code == 200:
    data = response.json()
    matches_found = False

    # Récupération de la date du jour au format "YYYY-MM-DD"
    today_str = datetime.now().strftime("%Y-%m-%d")
    print(f"--- Matchs du jour ({today_str}) ---")

    for match in data.get("matches", []):
      utc_date = match["utcDate"]  # Format: "2026-09-09T21:00:00Z"
      match_date = utc_date.split("T")[0]  # On extrait juste la partie "YYYY-MM-DD"

      # On ne traite que les matchs qui ont lieu aujourd'hui
      if match_date == today_str:
        matches_found = True
        status = match["status"]
        home = match["homeTeam"]["name"]
        away = match["awayTeam"]["name"]

        score = match.get("score", {})
        full_time = score.get("fullTime", {})
        home_goals = full_time.get("home")
        away_goals = full_time.get("away")

        # Heure du match (pour afficher l'heure si c'est à venir)
        match_time = utc_date.split("T")[1][:5]  # Extrait "HH:MM"

        if status == "FINISHED":
          print(f"[TERMINE] {home} {home_goals} - {away_goals} {away}")
        elif status in ["IN_PLAY", "PAUSED"]:
          print(f"[EN COURS] {home} {home_goals} - {away_goals} {away}")
        else:
          print(f"[A VENIR - {match_time} UTC] {home} vs {away}")

    if not matches_found:
      print("Aucun match de Ligue des Champions programmé aujourd'hui.")
  else:
    print(f"Erreur API : {response.status_code}")


if __name__ == "__main__":
  while True:
    print("\nVérification des scores...")
    get_champions_league_matches()
    print("Prochaine vérification dans 60 secondes...")
    time.sleep(60)