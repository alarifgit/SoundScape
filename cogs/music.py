import os
import asyncio
import discord
import logging
from discord.commands import SlashCommandGroup
from discord.ext import commands
from utils.player import Player
from utils.ytdl import YTDLSource
from utils.spotify import SpotifyHandler
from utils.autocomplete import get_search_suggestions
from utils.embed import EmbedGenerator

logger = logging.getLogger('hertz')

class Music(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.players = {}
        self.spotify = SpotifyHandler(
            client_id=os.getenv('SPOTIFY_CLIENT_ID'),
            client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')
        )
        logger.info("Music cog initialized")

    def get_player(self, guild_id: int) -> Player:
        if guild_id not in self.players:
            self.players[guild_id] = Player(self.bot)
        return self.players[guild_id]

    # Create slash command group
    music = SlashCommandGroup("music", "Music player commands")

    @music.command(name="play", description="Play a song from YouTube or Spotify")
    async def play(
        self, 
        ctx: discord.ApplicationContext, 
        query: discord.Option(str, "Song name or URL", autocomplete=get_search_suggestions)
    ):
        """Play audio from YouTube/Spotify"""
        await ctx.defer()
        
        player = self.get_player(ctx.guild.id)
        
        # Check voice channel
        if not ctx.author.voice:
            embed = EmbedGenerator.error("You need to join a voice channel first!")
            await ctx.respond(embed=embed)
            return

        # Spotify URL handling
        if "open.spotify.com" in query:
            track_info = await self.spotify.get_track_info(query)
            if not track_info:
                embed = EmbedGenerator.error("Couldn't fetch Spotify track info")
                await ctx.respond(embed=embed)
                return
            query = f"{track_info['artist']} - {track_info['title']}"

        # Process query
        source = await YTDLSource.create_source(query, loop=self.bot.loop)
        if not source:
            embed = EmbedGenerator.error("No results found")
            await ctx.respond(embed=embed)
            return
        
        # Add requester information
        source['requester'] = ctx.author.display_name
        source['requester_avatar'] = ctx.author.display_avatar.url

        await player.add_to_queue(ctx, source)

    @music.command(name="skip", description="Skip the current song")
    async def skip(self, ctx: discord.ApplicationContext):
        player = self.get_player(ctx.guild.id)
        await player.skip(ctx)
        embed = EmbedGenerator.success("Skipped current song")
        await ctx.respond(embed=embed)

    @music.command(name="queue", description="Show the current queue")
    async def show_queue(self, ctx: discord.ApplicationContext):
        player = self.get_player(ctx.guild.id)
        await player.show_queue(ctx)

    @music.command(name="remove", description="Remove a song from the queue")
    async def remove(
        self, 
        ctx: discord.ApplicationContext, 
        index: discord.Option(int, "Position in queue to remove")
    ):
        player = self.get_player(ctx.guild.id)
        await player.remove(ctx, index)

    @music.command(name="volume", description="Set player volume (0-100)")
    async def set_volume(
        self, 
        ctx: discord.ApplicationContext, 
        level: discord.Option(int, "Volume level (0-100)", min_value=0, max_value=100)
    ):
        player = self.get_player(ctx.guild.id)
        await player.set_volume(ctx, level / 100)
        embed = EmbedGenerator.success(f"Volume set to {level}%")
        await ctx.respond(embed=embed)

    @music.command(name="nowplaying", description="Show current song info")
    async def now_playing(self, ctx: discord.ApplicationContext):
        player = self.get_player(ctx.guild.id)
        await player.now_playing(ctx)

    @music.command(name="disconnect", description="Disconnect from voice channel")
    async def disconnect(self, ctx: discord.ApplicationContext):
        player = self.get_player(ctx.guild.id)
        await player.disconnect(ctx)
        embed = EmbedGenerator.success("Disconnected from voice channel")
        await ctx.respond(embed=embed)