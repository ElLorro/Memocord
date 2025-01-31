import os
import discord
import requests
from discord.ext import commands
from dotenv import load_dotenv
import base64

load_dotenv()
SERVER_ADDR = os.getenv('SERVER_ADDR') if os.getenv('SERVER_ADDR') else print('SERVER_ADDR is required')
url = f'{SERVER_ADDR}/v1'
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN') if os.getenv('DISCORD_BOT_TOKEN') else print('DISCORD_BOT_TOKEN is required')
MEMOS_API_KEY = os.getenv('MEMOS_API_KEY') if os.getenv('MEMOS_API_KEY') else print('MEMOS_API_KEY is required')
WHITELISTED_USERS = os.getenv('WHITELISTED_USERS').split(',') if os.getenv('WHITELISTED_USERS') else print('WHITELISTED_USERS is required')
WHITELISTED_CHANNELS = os.getenv('WHITELISTED_CHANNELS').split(',') if os.getenv('WHITELISTED_CHANNELS') else []

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')

@bot.event
async def on_message(message):
    print(f'📩 New message from {message.author}: {message.content}')
    """Handles new messages and stores them as memos."""
    if message.author == bot.user:
        return
    if str(message.author.id) not in WHITELISTED_USERS:
        print(f'❌ User {message.author} not whitelisted!')
        return
    if message.channel.type != discord.ChannelType.private:
        if message.channel.id not in WHITELISTED_CHANNELS:
            return
        #ignore all messages that are not from whitelisted channels
        
    try:
        payload = {
            "content": message.content,
            "visibility": "PRIVATE",
            "resources": []
        }
        if message.attachments:
            for attachment in message.attachments:
                content = base64.b64encode(await attachment.read()).decode('utf-8')
                resource = {
                    "filename": attachment.filename,
                    "type": attachment.content_type,
                    "content": content,
                }
                response = requests.post(f'{url}/resources', json=resource, headers={"Authorization": MEMOS_API_KEY})
                payload['resources'].append({
                    "name": response.json()['name'],
                })
        print(f'📤 Sending memo: {payload}')
        response = requests.post(f'{url}/memos', json=payload, headers={"Authorization": MEMOS_API_KEY})

        print(response.json())
        await message.add_reaction('👍')
    except:
        try: await message.add_reaction('👎')
        except: pass
        try:
            await message.delete()
        except:
            pass

# Run the bot
bot.run(DISCORD_BOT_TOKEN)