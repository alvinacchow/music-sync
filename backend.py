import requests, os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json 

load_dotenv()

def get_strava_token():
    r = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": os.getenv("STRAVA_CLIENT_ID"),
            "client_secret": os.getenv("STRAVA_CLIENT_SECRET"),
            "grant_type": "refresh_token",
            "refresh_token": os.getenv("STRAVA_REFRESH_TOKEN"),
        },
    )

    data = r.json()

    if "access_token" not in data:
        raise Exception(f"Strava auth error: {data}")

    return data["access_token"]

def get_spotify_token():
    with open(".cache", "r") as f:
        cache = json.load(f)

    refresh_token = cache["refresh_token"]

    r = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": os.getenv("SPOTIFY_CLIENT_ID"),
            "client_secret": os.getenv("SPOTIFY_CLIENT_SECRET")
        }
    )

    data = r.json()

    if "access_token" not in data:
        raise Exception(data)

    return data["access_token"]


def get_latest_activity(token):
    r = requests.get(
        "https://www.strava.com/api/v3/athlete/activities",
        headers={"Authorization": f"Bearer {token}"},
    )

    data = r.json()

    # IMPORTANT: handle API errors cleanly
    if not isinstance(data, list):
        raise Exception(f"Strava API error: {data}")

    if len(data) == 0:
        raise Exception("No activities found")

    return data[0]

def get_spotify_tracks(token):
    r = requests.get(
        "https://api.spotify.com/v1/me/player/recently-played?limit=50",
        headers={"Authorization": f"Bearer {token}"}
    )
    data = r.json()

    if "items" not in data:
        raise Exception(f"Spotify API error: {data}")

    # DEBUG: print timestamps
    print("\n🎧 Spotify playback history (raw):")
    for item in data["items"][:10]:
        print(
            item["played_at"],
            "|",
            item["track"]["name"],
            "—",
            item["track"]["artists"][0]["name"]
        )

    return data["items"]

def match_tracks(activity, tracks):
    start = datetime.fromisoformat(activity["start_date"].replace("Z",""))
    end = start + timedelta(seconds=activity["elapsed_time"])

    matched = []

    for t in tracks:
        played = datetime.fromisoformat(t["played_at"].replace("Z",""))

        name = t["track"]["name"]

        if start - timedelta(minutes=1) <= played <= end + timedelta(minutes=1):
            print("✅ MATCH:", played, "|", name)
            matched.append(f"{name} — {t['track']['artists'][0]['name']}")
        else:
            print("❌ SKIP :", played, "|", name)

    print("\n🏃 Strava activity window:")
    print("START:", start)
    print("END  :", end)
    return matched

def update_strava(activity_id, token, tracks):
    if not tracks:
        return

    description = "🎧 Workout playlist:\n" + "\n".join(f"- {t}" for t in tracks)

    requests.put(
        f"https://www.strava.com/api/v3/activities/{activity_id}",
        headers={"Authorization": f"Bearer {token}"},
        data={"description": description}
    )