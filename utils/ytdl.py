import yt_dlp as youtube_dl
import re
import asyncio

# Optimized options from MusicBot
YTDL_OPTS = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0',
    'force-ipv4': True,
    'cachedir': False,
    'geo_bypass': True,
    'buffer_size': '16K',  # MusicBot optimization
    'http_chunk_size': '32K',  # MusicBot optimization
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

class YTDLSource:
    @staticmethod
    async def create_source(query: str, loop=None) -> dict:
        """Create audio source from query"""
        loop = loop or asyncio.get_event_loop()
        with youtube_dl.YoutubeDL(YTDL_OPTS) as ydl:
            try:
                # Determine if URL or search
                if not re.match(r'https?://', query):
                    query = f'ytsearch:{query}'
                    
                # Extract info
                data = await loop.run_in_executor(None, lambda: ydl.extract_info(query, download=False))
                
                # Process entries
                if 'entries' in data:
                    data = data['entries'][0]
                    
                # Format result
                return {
                    'url': data['url'],
                    'title': data.get('title', 'Unknown Title'),
                    'webpage_url': data.get('webpage_url', ''),
                    'duration': data.get('duration', 0),
                    'thumbnail': data.get('thumbnail', ''),
                    'artist': data.get('uploader', ''),
                    'source': data.get('extractor', 'youtube'),
                    'is_spotify': False
                }
            except Exception as e:
                print(f"YTDL Error: {e}")
                return None