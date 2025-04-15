# Anime Multporn Bot

A Telegram bot that combines anime info fetching and multporn image downloading capabilities.

## Features

- **Anime Information**: Fetch anime information from AniList API and format it based on user preferences (Otaku, Hanime, Ongoing)
- **Multporn Image Downloading**: Download images from multporn.net and create PDFs
- **Link Splitting**: Generate episode links with formatted names

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/anime_multporn_bot.git
cd anime_multporn_bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API credentials:
```
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
```

4. Run the bot:
```bash
python merged_bot.py
```

## Project Structure

```
anime_multporn_bot/
├── merged_bot.py        # Main bot file
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (create this)
└── utils/               # Utility modules
    ├── __init__.py      # Package initialization
    ├── anime_utils.py   # Anime info fetching utilities
    ├── multporn_utils.py # Multporn image scraping utilities
    ├── pdf_utils.py     # PDF creation utilities
    └── link_splitter.py # Link processing utilities
```

## Commands

- `/start` - Start the bot
- `/anime` - Search for anime information
- `/setparams <anime_name with {episode}>` - Set anime name template for link splitting
- `/split` - Start link splitting process

## Usage

1. **Anime Information**:
   - Use `/anime` command
   - Enter anime name
   - Select quality (480p, 720p, 1080p, etc.)
   - Select format (Otaku, Hanime, Ongoing)

2. **Multporn Image Downloading**:
   - Send a multporn.net URL
   - Enter the number of images to download
   - Bot will download images and create a PDF

3. **Link Splitting**:
   - Use `/setparams` to set the anime name template (optional)
   - Use `/split` command
   - Send starting link (https://t.me/channel/message_id)
   - Send ending link (https://t.me/channel/message_id)

## Deployment on Linux VPS

1. Install required system packages:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a systemd service for automatic startup:
```bash
sudo nano /etc/systemd/system/anime-multporn-bot.service
```

5. Add the following content:
```
[Unit]
Description=Anime Multporn Telegram Bot
After=network.target

[Service]
User=your_username
WorkingDirectory=/home/your_username/anime_multporn_bot
ExecStart=/home/your_username/anime_multporn_bot/venv/bin/python merged_bot.py
Restart=on-failure
RestartSec=5
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=anime-multporn-bot

[Install]
WantedBy=multi-user.target
```

6. Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable anime-multporn-bot
sudo systemctl start anime-multporn-bot
```

7. Check the service status:
```bash
sudo systemctl status anime-multporn-bot
```

## Security Note

This bot restricts usage to a specific list of authorized users defined in the `ALLOWED_USERS` set in `merged_bot.py`. 
Make sure to update this list with your own user IDs.
