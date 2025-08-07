import os
import sys
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('hertz')

load_dotenv()

# Validate critical environment variables
required_envs = ['DISCORD_TOKEN', 'SPOTIFY_CLIENT_ID', 'SPOTIFY_CLIENT_SECRET']
missing_envs = [var for var in required_envs if not os.getenv(var)]

if missing_envs:
    logger.error(f"Missing required environment variables: {', '.join(missing_envs)}")
    sys.exit(1)

# Activity configuration
activity_type = os.getenv('BOT_ACTIVITY_TYPE', 'playing').lower()
activity_name = os.getenv('BOT_ACTIVITY', 'next level music')

try:
    activity_enum = getattr(discord.ActivityType, activity_type, discord.ActivityType.playing)
    logger.info(f"Activity set to: {activity_type} - {activity_name}")
except Exception as e:
    logger.error(f"Invalid activity type '{activity_type}': {str(e)}")
    activity_enum = discord.ActivityType.playing

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = discord.Bot(
    intents=intents,
    activity=discord.Activity(
        type=activity_enum,
        name=activity_name
    )
)

# Load cogs directly
from cogs.music import Music
bot.add_cog(Music(bot))

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user} (ID: {bot.user.id})')
    
    # Generate invite URL
    permissions = discord.Permissions()
    permissions.update(
        view_channel=True,
        send_messages=True,
        embed_links=True,
        connect=True,
        speak=True,
        use_voice_activity=True
    )
    invite_url = discord.utils.oauth_url(
        bot.user.id,
        permissions=permissions,
        scopes=("bot", "applications.commands")
    )
    logger.info(f'Invite URL: {invite_url}')
    
    # Sync commands with robust error handling
    try:
        logger.info("Syncing commands...")
        synced = await bot.sync_commands()
        
        if synced is None:
            # Inspect registered commands
            commands = bot.application_commands
            logger.warning(f"Sync returned None! Registered commands: {len(commands)}")
            
            # Attempt alternative sync method
            await bot.register_commands()
            logger.info("Fallback command registration completed")
        else:
            logger.info(f"Synced {len(synced)} commands")
            
    except Exception as e:
        logger.error(f"Command sync failed: {str(e)}")
        # Detailed diagnostics
        logger.info(f"Command count: {len(bot.application_commands)}")
        logger.info(f"Command names: {[cmd.name for cmd in bot.application_commands]}")

if __name__ == '__main__':
    logger.info("Starting SoundScape bot...")
    bot.run(os.getenv('DISCORD_TOKEN'))