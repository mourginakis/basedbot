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


@bot.command(name="greet")
async def greet(ctx):
    await ctx.send("Hello! I'm BasedBot!")

@bot.command(name="draw")
async def draw(ctx, *, prompt: str = None):  # The '*' tells the command to take the rest of the message as 'prompt'
    if not prompt:
        await ctx.send("Error: no prompt")
        return None
    
        # Process the prompt or perform the drawing action here
    await ctx.send(f"Drawing: {prompt}")


@bot.command(name="info")
async def draw(ctx):
    await ctx.send("I'm BasedBot! I can draw images for you!")
    return None







# ---------------- We probably won't use this ----------------

@bot.event
async def on_message(message):
    # Make sure the Bot doesn't respond to its own messages
    if message.author == bot.user: 
        return None
    
    # Check if the message is in the "basedbot" channel
    if message.channel.name == 'basedbot':
        pass
        # await message.channel.send(f"echo: {message.content}")

    await bot.process_commands(message)

bot.run(DISCORD_BOT_TOKEN)

