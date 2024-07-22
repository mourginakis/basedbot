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


all_time_cost: float = 0.0


# Events

@bot.event
async def on_ready():
    print(f'{bot.user} successfully logged in!')



@bot.command(name="greet")
async def greet(ctx):
    await ctx.send("Hello! I'm BasedBot!")



@bot.command(name="draw")
async def draw(ctx, *, prompt: str = None):

    if not prompt:
        await ctx.send("Error: no prompt")
        return None
    
    # Process the entire prompt
    # all_time_cost += 0.40
    await ctx.send(f"Prompt: {prompt}")
    await ctx.send(f"Working..... Queue now full.")

    await ctx.send(f"Image Generation Cost: $0.04")
    return None


@bot.command(name="info")
async def draw(ctx):
    await ctx.send(
        f"I'm BasedBot! I run DALLE-3.\n"
        f"We can only run one image at a time.\n"
        f"Max prompt length: 1000 characters.\n"
        f"All time cost (not yet implemented): {all_time_cost:,.2f}\n"
        f"https://cookbook.openai.com/articles/what_is_new_with_dalle_3\n"
    )
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

