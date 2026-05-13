import requests, os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json 
from dateutil import parser

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
    r = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": os.getenv("SPOTIFY_REFRESH_TOKEN"),
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
        "https://api.spotify.com/v1/me/player/recently-played?limit=20",
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
    start = parser.isoparse(activity["start_date"])
    end = start + timedelta(seconds=activity["elapsed_time"])

    print(f"Activity: {activity['name']}")
    print(f"Type: {activity['sport_type']}")
    print(f"elapsed_time: {activity['elapsed_time']}s")
    print(f"moving_time: {activity['moving_time']}s")
    print("Raw Strava start_date:", activity["start_date"])
    print("Raw Strava start_date_local:", activity["start_date_local"])
    matched = []

    for t in tracks:
        played_at = parser.isoparse(t["played_at"])  # when the track FINISHED

        # Only match if the track finished within the workout window
        name = t["track"]["name"]
        if start <= played_at <= end:
            matched.append(f"{name} by {t['track']['artists'][0]['name']}")
            print("✅ MATCH:", played_at, "|", name)
        else:
            print("❌ SKIP :", played_at, "|", name)

    return matched


def update_strava(activity_id, token, tracks, activity):
    if not tracks:
        return

    # Don't overwrite if already synced
    existing_description = activity.get("description") or ""
    if "🎧 Workout playlist:" in existing_description:
        print("Already synced, skipping.")
        return

    description = "🎧 Workout playlist:\n" + "\n".join(f"- {t}" for t in tracks)

    requests.put(
        f"https://www.strava.com/api/v3/activities/{activity_id}",
        headers={"Authorization": f"Bearer {token}"},
        data={"description": description}
    )