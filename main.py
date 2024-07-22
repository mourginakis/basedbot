#!/usr/bin/env python3

import os
from dotenv import load_dotenv
import discord
from discord.ext import commands


# Load in secrets/config
load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")


# Init the bot server/client

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


# Events

@bot.event
async def on_ready():
    print(f'{bot.user} successfully logged in!')


@bot.event
async def on_message(message):
    # Make sure the Bot doesn't respond to its own messages
    if message.author == bot.user: 
        return
    
    # Check if the message is in the "basedbot" channel
    if message.channel.name == 'basedbot':
        await message.channel.send(f'Received message: {message.content}')
        # await message.channel.send(f'From: {str(message)}')
        # await message.channel.send(f'Author: {str(message.content)}')

    await bot.process_commands(message)

bot.run(DISCORD_BOT_TOKEN)

