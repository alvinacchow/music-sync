import backend
def main():
    strava_token = backend.get_strava_token()
    spotify_token = backend.get_spotify_token()

    activity = backend.get_latest_activity(strava_token)
    tracks = backend.get_spotify_tracks(spotify_token)

    matched = backend.match_tracks(activity, tracks)

    print("MATCHED TRACKS:", matched)

    backend.update_strava(activity["id"], strava_token, matched, activity)
if __name__ == "__main__":
    main()