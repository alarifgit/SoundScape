import aiohttp
import json
import logging
import discord  # Import discord module

logger = logging.getLogger('hertz')

async def get_search_suggestions(ctx: discord.AutocompleteContext):
    """Get YouTube search suggestions using DuckDuckGo API"""
    query = ctx.value
    
    if not query or query.startswith('http'):
        return []
    
    url = "https://duckduckgo.com/ac/"
    params = {"q": query, "type": "list"}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    # Return top 5 suggestions
                    return data[0][:5]
    except Exception as e:
        logger.error(f"Autocomplete error: {str(e)}")
    return []