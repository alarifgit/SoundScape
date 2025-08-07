import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import asyncio

class SpotifyHandler:
    def __init__(self, client_id: str, client_secret: str):
        self.auth = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        self.sp = spotipy.Spotify(auth_manager=self.auth)

    async def get_track_info(self, url: str) -> dict:
        """Get track info from Spotify URL"""
        try:
            track = await asyncio.to_thread(self.sp.track, url)
            return {
                'title': track['name'],
                'artist': track['artists'][0]['name'],
                'duration': track['duration_ms'] // 1000,
                'thumbnail': track['album']['images'][0]['url'] if track['album']['images'] else '',
                'album': track['album']['name'],
                'is_spotify': True,
                'webpage_url': url  # Use original Spotify URL
            }
        except Exception as e:
            print(f"Spotify Error: {e}")
            return None