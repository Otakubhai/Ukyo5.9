"""
Anime utilities - Functions for fetching anime information from AniList
"""

import aiohttp

async def fetch_anime_info(anime_name):
    """
    Fetches anime details from AniList API.

    Args:
        anime_name (str): The name of the anime to search for.

    Returns:
        dict: Anime details from AniList API.
    """
    url = "https://graphql.anilist.co/"
    query = """
    query ($search: String) {
        Media(search: $search, type: ANIME) {
            id
            title {
                romaji
                english
            }
            episodes
            genres
            coverImage {
                extraLarge
            }
        }
    }
    """
    variables = {"search": anime_name}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"query": query, "variables": variables}) as response:
            data = await response.json()
            return data.get("data", {}).get("Media")
