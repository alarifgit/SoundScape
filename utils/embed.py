import discord

class EmbedGenerator:
    # Muse-inspired color palette
    COLORS = {
        "spotify": 0x1DB954,
        "youtube": 0xFF0000,
        "success": 0x3498db,
        "warning": 0xF1C40F,
        "error": 0xE74C3C,
        "info": 0x2ECC71
    }

    ICONS = {
        "play": "▶️",
        "pause": "⏸️",
        "stop": "⏹️",
        "queue": "📋",
        "volume": "🔊",
        "skip": "⏭️",
        "remove": "🗑️",
        "loop": "🔁",
        "disconnect": "👋",
        "error": "❌",
        "success": "✅"
    }

    @staticmethod
    def now_playing(track: dict) -> discord.Embed:
        """Now playing embed in Muse style"""
        embed = discord.Embed(
            title=f"{EmbedGenerator.ICONS['play']} Now Playing",
            color=EmbedGenerator.COLORS["spotify" if track.get('is_spotify') else "youtube"]
        )
        embed.add_field(
            name="Track", 
            value=f"[{track['title']}]({track['webpage_url']})", 
            inline=False
        )
        
        if track.get('artist'):
            embed.add_field(name="Artist", value=track['artist'], inline=True)
            
        if track.get('album'):
            embed.add_field(name="Album", value=track['album'], inline=True)
            
        if track.get('duration'):
            mins, secs = divmod(track['duration'], 60)
            embed.add_field(name="Duration", value=f"{mins}:{secs:02d}", inline=True)
            
        if track.get('thumbnail'):
            embed.set_thumbnail(url=track['thumbnail'])
            
        embed.set_footer(
            text="Requested by: " + track.get('requester', 'Unknown'),
            icon_url=track.get('requester_avatar')
        )
        return embed

    @staticmethod
    def added_to_queue(track: dict, position: int) -> discord.Embed:
        """Added to queue embed in Muse style"""
        embed = discord.Embed(
            title=f"{EmbedGenerator.ICONS['queue']} Added to Queue",
            description=f"Position #{position}",
            color=EmbedGenerator.COLORS["success"]
        )
        embed.add_field(
            name="Track", 
            value=f"[{track['title']}]({track['webpage_url']})", 
            inline=False
        )
        
        if track.get('duration'):
            mins, secs = divmod(track['duration'], 60)
            embed.add_field(name="Duration", value=f"{mins}:{secs:02d}", inline=True)
            
        if track.get('thumbnail'):
            embed.set_thumbnail(url=track['thumbnail'])
            
        embed.set_footer(
            text="Requested by: " + track.get('requester', 'Unknown'),
            icon_url=track.get('requester_avatar')
        )
        return embed

    @staticmethod
    def queue_list(queue: list, current: dict, page: int, total_pages: int) -> discord.Embed:
        """Queue list embed in Muse style"""
        embed = discord.Embed(
            title=f"{EmbedGenerator.ICONS['queue']} Current Queue",
            description=f"Page {page}/{total_pages}",
            color=EmbedGenerator.COLORS["info"]
        )
        
        # Current track
        if current:
            embed.add_field(
                name=f"{EmbedGenerator.ICONS['play']} Now Playing",
                value=f"[{current['title']}]({current['webpage_url']})",
                inline=False
            )
        
        # Queue items
        if queue:
            queue_text = ""
            for idx, track in enumerate(queue):
                if idx >= 10:  # Only show 10 per page
                    break
                mins, secs = divmod(track.get('duration', 0), 60)
                duration = f"{mins}:{secs:02d}" if track.get('duration') else "N/A"
                queue_text += f"`{idx+1}.` [{track['title']}]({track['webpage_url']}) `{duration}`\n"
            
            embed.add_field(
                name="Up Next",
                value=queue_text or "No tracks in queue",
                inline=False
            )
        else:
            embed.add_field(
                name="Up Next",
                value="No tracks in queue",
                inline=False
            )
            
        # Queue metadata
        total_duration = sum(t.get('duration', 0) for t in queue)
        total_mins, total_secs = divmod(total_duration, 60)
        total_hours, total_mins = divmod(total_mins, 60)
        
        embed.add_field(
            name="Queue Info",
            value=f"Tracks: {len(queue)}\nDuration: "
                  f"{f'{total_hours}h ' if total_hours else ''}{total_mins}m {total_secs}s",
            inline=False
        )
        return embed

    @staticmethod
    def error(message: str) -> discord.Embed:
        """Error embed in Muse style"""
        embed = discord.Embed(
            title=f"{EmbedGenerator.ICONS['error']} Error",
            description=message,
            color=EmbedGenerator.COLORS["error"]
        )
        return embed

    @staticmethod
    def success(message: str) -> discord.Embed:
        """Success embed in Muse style"""
        embed = discord.Embed(
            title=f"{EmbedGenerator.ICONS['success']} Success",
            description=message,
            color=EmbedGenerator.COLORS["success"]
        )
        return embed