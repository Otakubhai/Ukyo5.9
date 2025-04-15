"""
Link splitter utilities - Functions for processing Telegram links
"""

import re

def process_split_links(start_link, end_link, anime_name=""):
    """
    Processes telegram links and generates a sequence of links with episode numbers.
    
    Args:
        start_link (str): The starting Telegram link (https://t.me/channel/message_id)
        end_link (str): The ending Telegram link (https://t.me/channel/message_id)
        anime_name (str): Template for the anime name with {episode} placeholder
        
    Returns:
        list: List of formatted links with episode numbers, or None if links are invalid
    """
    # Validate links format
    start_match = re.match(r'https://t.me/(\w+)/(\d+)', start_link)
    end_match = re.match(r'https://t.me/(\w+)/(\d+)', end_link)
    
    if not start_match or not end_match:
        return None
        
    # Extract channel name and message IDs
    channel_name, start_id = start_match.groups()
    _, end_id = end_match.groups()
    
    # Convert to integers
    start_id, end_id = int(start_id), int(end_id)
    
    # Generate links
    links = []
    for i, msg_id in enumerate(range(start_id, end_id + 1)):
        episode_num = f"{i+1:02d}"  # Format as 01, 02, etc.
        
        # Replace {episode} placeholder in anime name if present
        episode_name = anime_name.replace("{episode}", episode_num) if anime_name else f"Episode {episode_num}"
        
        # Format link
        formatted_link = f"https://t.me/{channel_name}/{msg_id} -n {episode_name} \n"
        links.append(formatted_link)
        
    return links
