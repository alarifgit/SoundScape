import discord
import asyncio
import logging
from collections import deque
from utils.embed import EmbedGenerator

logger = logging.getLogger('hertz')

class Player:
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.queue = deque()
        self.current = None
        self.volume = 0.5
        self.loop = False
        self.now_playing = None
        logger.info(f"Player initialized for guild")

    async def add_to_queue(self, ctx: discord.ApplicationContext, source: dict):
        """Add track to queue and start playback if needed"""
        # Add track with requester info
        self.queue.append(source)
        position = len(self.queue)
        
        # Send embed response
        embed = EmbedGenerator.added_to_queue(source, position)
        await ctx.followup.send(embed=embed)

        # Start playback if not active
        vc = ctx.guild.voice_client
        if not vc or not vc.is_playing():
            await self.play_next(ctx)

    async def play_next(self, ctx: discord.ApplicationContext):
        """Play next track in queue"""
        if not self.queue:
            self.current = None
            self.now_playing = None
            return

        self.current = self.queue.popleft()
        
        # Handle looping
        if self.loop and self.current:
            self.queue.appendleft(self.current)
            
        vc = ctx.guild.voice_client

        # Connect to voice if needed
        if not vc:
            try:
                vc = await ctx.author.voice.channel.connect()
            except Exception as e:
                logger.error(f"Connection error: {str(e)}")
                embed = EmbedGenerator.error(f"Failed to join voice: {str(e)}")
                await ctx.channel.send(embed=embed)
                return

        try:
            # Play audio with reconnect options
            vc.play(
                discord.FFmpegPCMAudio(
                    self.current['url'], 
                    before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
                ),
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    self.play_next(ctx), 
                    self.bot.loop
                )
            )
            vc.source = discord.PCMVolumeTransformer(vc.source, volume=self.volume)
            
            # Send now playing embed
            self.now_playing = self.current
            embed = EmbedGenerator.now_playing(self.current)
            await ctx.channel.send(embed=embed)
        except Exception as e:
            # Handle playback errors
            logger.error(f"Playback error: {str(e)}")
            embed = EmbedGenerator.error(f"Playback error: {str(e)}")
            await ctx.channel.send(embed=embed)
            await self.play_next(ctx)

    async def skip(self, ctx: discord.ApplicationContext):
        vc = ctx.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await asyncio.sleep(0.5)  # Allow the after callback to trigger

    async def show_queue(self, ctx: discord.ApplicationContext):
        page = 1  # For now, implement pagination later
        total_pages = (len(self.queue) + 9) // 10  # 10 per page
        
        embed = EmbedGenerator.queue_list(
            queue=list(self.queue),
            current=self.now_playing,
            page=page,
            total_pages=total_pages
        )
        await ctx.respond(embed=embed)

    async def remove(self, ctx: discord.ApplicationContext, index: int):
        if 1 <= index <= len(self.queue):
            removed = list(self.queue)[index-1]
            del self.queue[index-1]
            
            # Create custom removal embed
            embed = EmbedGenerator.added_to_queue(removed, 0)
            embed.title = "🗑️ Removed from queue"
            embed.description = None
            await ctx.respond(embed=embed)
        else:
            embed = EmbedGenerator.error("Invalid queue position")
            await ctx.respond(embed=embed)

    async def set_volume(self, ctx: discord.ApplicationContext, level: float):
        self.volume = max(0.0, min(1.0, level))
        vc = ctx.guild.voice_client
        if vc and vc.source:
            vc.source.volume = self.volume

    async def now_playing(self, ctx: discord.ApplicationContext):
        if self.now_playing:
            embed = EmbedGenerator.now_playing(self.now_playing)
            # Add player status
            embed.add_field(name="Volume", value=f"{int(self.volume*100)}%", inline=True)
            embed.add_field(name="Looping", value="✅" if self.loop else "❌", inline=True)
            await ctx.respond(embed=embed)
        else:
            embed = EmbedGenerator.error("No track currently playing")
            await ctx.respond(embed=embed)

    async def disconnect(self, ctx: discord.ApplicationContext):
        vc = ctx.guild.voice_client
        if vc:
            await vc.disconnect()
            self.queue.clear()
            self.current = None
            self.now_playing = None