# 🎧 music-sync

I'm someone who fuels every run and walk with music. After finishing a workout, I'd always want to remember what I was listening to, but Spotify's history is one long undifferentiated list, and Strava knows nothing about it.

This project bridges the gap. It automatically matches the tracks I was playing on Spotify to the window of my Strava activity, then writes them into the activity description as a playlist. No manual logging, no trying to remember what came on during mile three.

## How It Works

After a workout is recorded on Strava, the script fetches my Spotify recently-played history and finds any tracks whose playback timestamp falls within the activity's start and end time. The matched tracks are written directly into the Strava activity description.

A GitHub Actions workflow runs the sync every 15 minutes in the background, so it just happens automatically after every activity.

## Example Output

```
🎧 Workout playlist:
- Dive — Olivia Dean
- Something Inbetween — Olivia Dean
- Die On This Hill — SIENNA SPIRO
- Landslide — Fleetwood Mac
- Almost (Sweet Music) — Hozier
```

## Built With

- Python
- Strava API
- Spotify API
- GitHub Actions